# Coverage of `nba-transaction-legality.json`

Study 001 (policy representation), arm **B**. This document states what the Judgment Pack encodes,
what it deliberately does not, the exact `/facts/derived/*` contract the pack depends on, and every
place the CBA text was ambiguous and a reading had to be chosen.

The pack was authored from
`rulearena/checkout/nba/reference_rules.txt` only, plus the list of 61 rule-name identifiers used by
the benchmark's `relevant_rules` annotations. No benchmark instance, gold answer, or answer
distribution was read.

- Spec version: `0.1.0-draft`
- `judgment-pack spec validate packs/nba-transaction-legality.json` → **exit 0**
- Outcomes: `legal`, `illegal`
- Rules: **61**
- `/facts/derived/*` fields required: **124**
- Vocabulary coverage: **61 / 61 (100%)** of the benchmark's `relevant_rules` identifiers

---

## 1. Architecture of the encoding

**No arithmetic.** JPS 0.1.0-draft §2.2/§7.4 compares facts; it cannot compute. Every quantity that
has to be *calculated* (post-transaction Team Salary, apron comparisons, percentage-of-cap limits,
aggregate incoming/outgoing salary in a trade) is read from `/facts/derived/<name>` and is produced
by the study's separate, published, deterministic preprocessor. The pack contributes the **policy**:
which provision governs which situation, which numeric threshold applies, and what the legal
consequence of crossing it is.

**Ratios, not amounts.** Wherever the CBA states a percentage, the preprocessor supplies a *ratio*
and the pack holds the *percentage*. For example the pack asserts
`ratio-non-taxpayer-mid-level-aggregate-first-year-salary-to-cap > "0.0912"`; the constant 9.12%
from Article VII, Section 6(e)(1) lives in the pack, and the division lives in the preprocessor.
The same pattern carries 25% / 30% / 35% (Article II, Section 7), 105%, 175%, 120%, 130%, 3.32%,
5.678%, 5.15%, 5%, 8%, 4.5%, and the nominal constants `$250,000` and `$7,500,000`.

**Every rule is a violation detector.** All 61 rules resolve to `illegal`; `legal` is reachable only
as `fallbackOutcome`. This is forced by the resolution model: JPS §8 treats two *distinct* candidate
outcomes as `conflict` → `unresolved`. With one outcome per rule, any number of simultaneous
violations agree instead of conflicting, and every fired rule id is an independently reportable
citation. A pack that also contained affirmative "legal" rules would go unresolved whenever a legal
rule and an illegal rule both matched.

**Gate-then-test.** Each rule's `when` is `all[<gate>, <violation test>]`, where the gate is a
boolean that the preprocessor emits on **every** instance. JPS §7.1 conjunction is strong: a false
child makes the conjunction false even when a sibling is unknown. So an inapplicable rule evaluates
`false` (not `unknown`) and never escalates, while an *applicable* rule whose amount is missing or
redacted evaluates `unknown`.

**Escalation is the point.** Every rule carries `onUnknown: "escalate"`. If a fact an applicable rule
depends on is absent from the facts document, the run produces
`unresolved / reasons:["unknown"] / handoff: requested → "NBA salary cap analyst"` rather than a
guessed boolean. Redacting any `/facts/derived/*` field named below, on an instance where its gate is
true, is therefore expected to convert an answer into an escalation.

**One exception object.** `provision-outside-pack-scope` (`effect: "escalate"`,
`onUnknown: "ignore"`) fires when `/facts/derived/contains-provision-outside-pack-scope` is `true`,
i.e. when the instance turns on a family listed in §3 below. `onUnknown: "ignore"` is deliberate: a
missing scope marker means the preprocessor did not classify the instance, which is not itself a
missing legal fact.

**Evidence requirements are advisory.** All three declared `evidenceRequirements` have
`required: false`, and no rule uses an `evidence-present` condition. This is deliberate: under the
§8 resolution model a `required: true` requirement with no `--evidence` input is *unknown*, which
would make every instance unresolved. Run the evaluator **without** `--evidence`.

**Rule ids.** JPS `localId` is `^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$`, so the benchmark's snake_case
identifiers appear kebab-cased. The mapping is the exact bijection `_ → -`; it is verifiable with:

```
python3 -c "import json,glob;v={r.replace('_','-') for f in glob.glob('rulearena/checkout/nba/annotated_problems/*.json') for i in json.load(open(f)) for r in i['relevant_rules']};p={r['id'] for r in json.load(open('packs/nba-transaction-legality.json'))['rules']};print(len(v),len(p),v==p)"
```

---

## 2. Rule families encoded

| Family | CBA source | Rule ids (kebab-cased benchmark identifiers) |
|---|---|---|
| Basic cap rule | Art. VII §2(b)(1) | `salary-cap-no-exceed-without-exception` |
| Maximum Annual Salary by Years of Service | Art. II §7(a)(i)–(iii), §7(g) | `maximum-salary-for-player-less-than-7-year-service`, `maximum-salary-for-player-7-to-9-year-service`, `maximum-salary-for-player-10-or-more-year-service`, `higher-max-criterion-for-5th-year-eligible-player` |
| Annual increase/decrease limits | Art. VII §5(a)(1)–(2) | `salary-increase-and-decrease-ratio-for-qualiyfing-or-early-qualifying-veteran-free-agent`, `salary-increase-and-decrease-ratio-qualiyfing-or-early-qualifying-veteran-free-agent`, `salary-increase-and-decrease-ratio-except-qualiyfing-or-early-qualifying-veteran-free-agent` |
| Contract length | Art. IX; Art. VII §6(d)(2), (e)(2), (f)(1), (g)(2), (i) | `contract-length-at-most-4-year-except-qualifying-veteran-free-agent-5-year`, `contract-length-at-most-4-year-non-taxpayer-mid-level-exception`, `contract-length-at-most-2-year-taxpayer-mid-level-exception`, `contract-length-at-most-2-year-bi-annual-exception`, `contract-length-at-most-3-year-mid-level-exception-for-room-team`, `contract-length-at-most-2-year-minimum-player-salary-exception` |
| Veteran Free Agent Exceptions | Art. VII §6(b)(1)–(3); Art. I (t), (rr), (yy) | `qualifying-veteran-free-agent-exception`, `qualified-veteran-free-agent-exception`, `early-qualifying-veteran-free-agent-exception`, `non-qualifying-veteran-free-agent-exception` |
| Mid-level / bi-annual / minimum amounts | Art. VII §6(d)(1), (e)(1), (f)(1), (g)(1), (i) | `non-taxpayer-mid-level-exception`, `nontaxpayer-mid-level-exception`, `taxpayer-mid-level-exception`, `mid-level-exception-for-room-team`, `bi-annual-exception`, `minimum-player-salary-exception` |
| Apron hard caps (Transaction Restrictions Table) | Art. VII §2(e)(2), §2(e)(4) rows A, B, C, E, H, I, J, K; §2(e)(2)(iii); §6(f)(5) | `bi-annual-exception-hard-cap-first-apron-level`, `non-taxpayer-mid-level-exception-hard-cap-first-apron-level`, `nontaxpayer-mid-level-exception-hard-cap-first-apron-level`, `non-taxpayer-mid-level-exception-hard-cap-second-apron-level`, `taxpayer-mid-level-exception-hard-cap-second-apron-level`, `taxpayer-mid-level-exception-hard-cap-first-apron-level`, `sign-and-trade-hard-cap-first-apron-level`, `expanded-traded-player-exception-hard-cap-first-apron-level`, `aggregated-traded-player-exception-hard-cap-second-apron-level`, `sign-and-trade-assigner-traded-player-exception-hard-cap-second-apron-level`, `cash-in-trade-hard-cap-second-apron-level` |
| Traded Player Exceptions | Art. VII §6(j)(1)(i), (ii), (iv), (v); §6(j)(3); §6(j)(4)(ii) | `standard-traded-player-exception`, `aggregated-standard-traded-player-exception`, `expanded-traded-player-exception`, `traded-player-exception-for-room-team`, `traded-player-exception-250k-reduced-first-apron-level`, `traded-player-exception-only-one-minimum-traded-player-under-conditions` |
| Sign-and-trade | Art. VII §8(e)(1)(ii), (iii), (vi), (vii); §6(j)(5) | `sign-and-trade-3-to-4-year`, `sign-and-trade-not-with-mid-level-exception`, `sign-and-trade-assignee-team-has-room`, `sign-and-trade-no-higher-than-25-percent-for-higher-max-5th-year-eligible-player`, `sign-and-trade-qualifying-free-agent-half-salary-for-traded-player-exception` |
| Cash in trades | Art. VII §8(a) | `pay-or-receive-cash-maximum-in-a-year` |
| Stepien rule | By-Laws §7.03 | `stepien-rule-no-sell-or-no-consecutive-first-round-draft-pick-trade`, `stepien-rule-no-consecutive-first-round-draft-pick-trade` |
| Post-signing trade bar | Art. VII §8(d)(ii) | `free-agent-sign-contract-cannot-be-traded-within-3-month-or-before-dec-15` |
| Over 38 Rule (cap consequence) | Art. VII §3(a)(2)(i), (ii), (iv) | `defer-compensation-38-year-old`, `defer-compensation-qualifying-veteran-free-agent-38-year-old`, `defer-compensation-38-year-old-qualifying-veteran-free-agent-38-year-old` |
| Free Agent Amounts / cap holds (cap consequence) | Art. VII §4(d)(1)–(3) | `salary-space-consumption-qualifying-veteran-free-agent`, `salary-space-consumption-early-qualifying-veteran-free-agent`, `salary-space-consumption-non-qualifying-veteran-free-agent` |
| Restricted free agency offer sheets | Art. XI §5(b), §5(d)(i)–(iii) | `offer-sheet-for-1-or-2-year-service-player-no-more-than-mid-level-in-first-2-year`, `offer-sheet-for-1-or-2-year-service-player-3rd-year-maximum-if-first-2-year-maximum`, `offer-sheet-for-1-or-2-year-service-player-4th-year-maximum-if-first-3-year-maximum`, `offer-sheet-for-1-or-2-year-service-player-4th-year-maximum-if-3-year`, `offer-sheet-for-1-or-2-year-service-player-average-salary-more-than-2-year` |

---

## 3. Out of scope — what the pack does **not** encode

These provisions appear in `reference_rules.txt` but carry no rule in the pack. When an instance
turns on one of them, the preprocessor should set
`/facts/derived/contains-provision-outside-pack-scope` to `true`, which escalates rather than
guesses.

| Not encoded | CBA location | Why |
|---|---|---|
| All arithmetic: Team Salary computation, Salary Cap / apron levels, Free Agent Amount values, Minimum and Average Player Salary, exception dollar amounts | Art. VII §4(a)–(c), §4(d)(4)–(8); passim | Architectural: JPS has no arithmetic. Delegated to the preprocessor by design and disclosed as the study's scope limit. |
| Rookie Scale Extension and Designated Veteran Player Extension percentage mechanics | Art. II §7(d), §7(e) | Extension mechanics; no benchmark citation name. |
| Subsequent Salary Cap Year projection for post-season transactions | Art. VII §2(e)(2)(ii), §2(e)(3) | Requires forward projection of options, ETOs, and Higher Max outcomes; no citation name. |
| Draft Pick Penalty and the Second Apron Team pick-trade freeze | Art. VII §2(f) | Multi-year state across Salary Cap Years; no citation name. |
| Exception mutual-exclusion and consecutive-year bars (Bi-annual not in two consecutive years; Room MLE extinguishing the others) | Art. VII §6(d)(3), §6(e)(3), §6(f)(2), §6(g)(1), §6(g)(3) | Requires prior-Salary-Cap-Year history not present in the facts contract. |
| Offer-sheet matching via an exception | Art. VII §6(b)(3)(ii), §6(e)(5) | Right-of-first-refusal mechanics; no citation name. |
| Transition Traded Player Exception (2023-24 only) and table rows F and G | Art. VII §6(j)(1)(iii); §2(e)(4) rows F, G | Date-conditioned on the Regular Season calendar; no citation name. See reading 13. |
| Two-month aggregation bar; base-compensation protection reductions; Disabled Player Exception interaction; Two-Way Player carve-out | Art. VII §6(j)(4)(i), §6(j)(6), §6(j)(7), §6(j)(8) | Date- and protection-conditioned; no citation name. |
| "At or above the Salary Cap" precondition for using Exceptions; TPE cap-space absorption | Art. VII §6(n)(1), §6(n)(2) | Team Salary bookkeeping; delegated to the preprocessor's derivation of the `uses-*` flags. |
| Veteran and Rookie Scale Extensions in full: timing, anniversary rules, 140% / 107.5% / 120% / 105% extension maxima | Art. VII §7(a), §7(b); §8(e)(2) | No benchmark citation name for any extension provision. |
| Trade-consent, trade deadline, 30-day rookie bar, January 15 bar, post-extension and post-renegotiation trade bars, rookie-scale-extension trade valuation, re-signing a waived traded player | Art. VII §8(b), §8(c), §8(d)(i), §8(d)(iii), §8(f), §8(g), §8(h) | No citation name; §8(d)(ii) alone is named and is encoded. |
| Right of first refusal mechanics: notices, deadlines, principal terms, one-year amendment and trade bars | Art. XI §5(c), §5(e)–(o) | Procedural; no citation name. Only §5(b) and §5(d) are encoded. |
| Sign-and-trade conditions (i), (iv), (v) — prior-season roster, first-Season skill protection, pre-Regular-Season timing | Art. VII §8(e)(1)(i), (iv), (v) | No citation name; encoding them would emit citations the gold never contains. See reading 14. |

---

## 4. Required `/facts/derived/*` contract

**Presence discipline — the single most important rule for the preprocessor.**

- Fields marked **always** MUST be present on *every* facts document, as JSON `true`/`false`.
  Omitting one makes every rule that reads it `unknown`, which escalates the instance.
- Every other field MUST be present **whenever its stated gate is `true`** and MUST be **omitted**
  when the underlying quantity is genuinely unavailable or has been redacted for the escalation
  condition. Absent ⇒ `unknown` ⇒ escalate. That is the intended behaviour.
- Every ordered-compared value MUST be a **JSON string** matching `-?(0|[1-9][0-9]*)(\.[0-9]+)?`.
  A JSON number yields `unknown` for ordered comparison. Booleans stay JSON booleans.
- `ratio-…-to-X` means *numerator ÷ X*, as a decimal string. Where the denominator could be zero or
  undefined, omit the field.
- "Worst case" below means: the maximum over the qualifying operations in the instance, because the
  benchmark question is whether *any* operation is illegal.

### 4.1 Always-present booleans (39)

| Field | CBA-sourced definition |
|---|---|
| `contains-provision-outside-pack-scope` | `true` iff deciding this instance requires a provision family listed in §3. |
| `any-transaction-without-exception` | `true` iff at least one operation is performed by a team **not** invoking any Art. VII §6 Exception and not acting with Room under §2(b)(2). |
| `uses-qualifying-veteran-free-agent-exception` | `true` iff an operation signs a Contract stated to use the Qualifying Veteran Free Agent Exception (§6(b)(1)). |
| `uses-early-qualifying-veteran-free-agent-exception` | Same for the Early Qualifying Veteran Free Agent Exception (§6(b)(3)). |
| `uses-non-qualifying-veteran-free-agent-exception` | Same for the Non-Qualifying Veteran Free Agent Exception (§6(b)(2)). |
| `uses-non-taxpayer-mid-level-exception` | Same for the Non-Taxpayer Mid-Level Salary Exception (§6(e)). |
| `uses-taxpayer-mid-level-exception` | Same for the Taxpayer Mid-Level Salary Exception (§6(f)). |
| `uses-bi-annual-exception` | Same for the Bi-annual Exception (§6(d)). |
| `uses-room-mid-level-exception` | Same for the Mid-Level Salary Exception for Room Teams (§6(g)). |
| `uses-minimum-player-salary-exception` | Same for the Minimum Player Salary Exception (§6(i)). |
| `uses-standard-traded-player-exception` | `true` iff a team acquires a player using the Standard Traded Player Exception (§6(j)(1)(i)). |
| `uses-aggregated-standard-traded-player-exception` | Same for the Aggregated Standard Traded Player Exception (§6(j)(1)(ii)). |
| `uses-expanded-traded-player-exception` | Same for the Expanded Traded Player Exception (§6(j)(1)(iv)). |
| `uses-room-traded-player-exception` | Same for Room Under Salary Cap Plus $250,000 (§6(j)(1)(v)). |
| `uses-any-traded-player-exception` | Logical OR of the four preceding flags. |
| `uses-traded-player-exception-for-signed-and-traded-contract` | `true` iff a team acquires a player using a Traded Player Exception that is *in respect of* a Contract signed and traded under §8(e)(1) — table row J. |
| `includes-sign-and-trade` | `true` iff any operation is a Contract signed and traded pursuant to §8(e)(1). |
| `acquires-player-under-sign-and-trade-contract` | `true` iff a team *acquires* a player under a §8(e)(1) Contract — table row C. |
| `includes-cash-in-trade` | `true` iff any team pays **or** receives cash in connection with a trade (§8(a)). |
| `pays-cash-in-trade` | `true` iff a team **pays** cash to another team in a trade — table row I. |
| `includes-first-round-pick-trade` | `true` iff any operation trades, exchanges, or sells a first round draft pick (By-Laws §7.03). |
| `includes-trade-of-recently-signed-free-agent-contract` | `true` iff any operation trades a Standard NBA Contract that was signed by a Free Agent in the current Salary Cap Year (§8(d)(ii)). |
| `has-new-contract-service-under-7` | `true` iff a new Player Contract is signed by a player with fewer than seven Years of Service who is **not** a 5th Year Eligible Player re-signing with his Prior Team (Art. II §7(a)(i); see reading 2). |
| `has-new-contract-service-7-to-9` | `true` iff a new Contract is signed by a player with at least seven but fewer than ten Years of Service who is **not** signing a Designated Veteran Player Contract (Art. II §7(a)(ii); reading 2). |
| `has-new-contract-service-10-or-more` | `true` iff a new Contract is signed by a player with ten or more Years of Service (Art. II §7(a)(iii)). |
| `has-fifth-year-eligible-contract` | `true` iff a new Contract or Rookie Scale Extension is entered into by a 5th Year Eligible Player (four Years of Service as of the June 30 following his last covered Season) with his Prior Team (Art. II §7(a)(i) proviso). |
| `has-designated-veteran-player-contract` | `true` iff a Designated Veteran Player Contract is entered into: eight or nine Years of Service, rendered for the Team with which he first executed a Contract (or changed Teams only by trade in the first four Cap Years), with his Prior Team (Art. II §7(a)(ii) proviso). |
| `has-standard-length-new-contract` | `true` iff any new Player Contract is signed that is **not** between a Qualifying Veteran Free Agent and his Prior Team (Art. IX main clause). |
| `has-qualifying-veteran-free-agent-prior-team-contract` | `true` iff any new Contract is between a Qualifying Veteran Free Agent and his Prior Team (Art. IX proviso (a)). |
| `has-contract-governed-by-5-percent-limit` | `true` iff any new Contract is governed by Art. VII §5(a)(1): all Contracts other than those between Qualifying or Early Qualifying Veteran Free Agents and their Prior Team, **plus** such Contracts signed under §6(d)(4), §6(e)(4), §6(f)(3), §6(g)(4), or §8(e)(1). |
| `has-contract-governed-by-8-percent-limit` | `true` iff any new Contract is governed by Art. VII §5(a)(2): between a Qualifying or Early Qualifying Veteran Free Agent and his Prior Team, excluding the §5(a)(1) carve-outs above. |
| `over-38-contract-present` | `true` iff any Contract, Extension, or Renegotiation covers four or more Seasons including one or more Seasons commencing after the player reaches age 38 (Art. VII §3(a)(2), with §3(a)(2)(v) and (vii) age conventions). |
| `over-38-qualifying-veteran-free-agent-age-35-or-36-five-seasons` | `true` iff such a Contract is a five-Season Over 38 Contract between a Qualifying Veteran Free Agent aged 35 or 36 and his Prior Team (§3(a)(2)(ii), including its age-34-turning-35 deeming). |
| `qualifying-veteran-free-agent-hold-included` | `true` iff a Qualifying Veteran Free Agent who has not re-signed, signed elsewhere, or been renounced is carried in his Prior Team's Team Salary (§4(d)(1)). |
| `early-qualifying-veteran-free-agent-hold-included` | Same for an Early Qualifying Veteran Free Agent (§4(d)(2)). |
| `non-qualifying-veteran-free-agent-hold-included` | Same for a Non-Qualifying Veteran Free Agent (§4(d)(3)). |
| `offer-sheet-restricted-free-agent-service-1-or-2` | `true` iff an operation is an Offer Sheet signed by a Restricted Free Agent with one or two Years of Service (Art. XI §5(d)). |
| `non-taxpayer-mid-level-deemed-taxpayer-mid-level` | `true` iff the §6(f)(5) deeming applies: the team acquired no Contract by assignment with the NTMLE, used the NTMLE only for Contracts of at most two Seasons totalling no more than the Taxpayer Mid-Level amount, and then engaged in a transaction taking its Team Salary above the First Apron Level. See reading 6. |
| `sign-and-trade-qualifying-free-agent-deeming-applies` | `true` iff all three §6(j)(5) conditions hold: a Qualifying or Early Qualifying Veteran Free Agent signs with his Prior Team under §6(b)(1) or (3) in connection with a §8(e) trade; the Prior Team's Team Salary immediately after signing is above the Salary Cap; and the new Contract's first-Season Salary plus Unlikely Bonuses exceeds what §6(b)(2) would have permitted. |

### 4.2 Conditional booleans (18)

| Field | Present when | CBA-sourced definition |
|---|---|---|
| `fifth-year-eligible-meets-higher-max-criteria` | `has-fifth-year-eligible-contract` | `true` iff the player met at least one Higher Max Criterion as of the July 1 following his fourth Season: All-NBA first/second/third team or Defensive Player of the Year in the immediately preceding Season or in two of the preceding three; or NBA MVP in one of the preceding three Seasons (Art. II §7(a)(i)(A)–(B)). |
| `qualifying-veteran-free-agent-exception-available` | `uses-qualifying-veteran-free-agent-exception` | `true` iff the player is in fact a Qualifying Veteran Free Agent (Art. I (yy)) and is contracting with his Prior Team (§6(b)). |
| `early-qualifying-veteran-free-agent-exception-available` | `uses-early-qualifying-veteran-free-agent-exception` | `true` iff the player is in fact an Early Qualifying Veteran Free Agent (Art. I (t)) and is contracting with his Prior Team, and the Prior Team has not renounced its Early Qualifying rights (§4(d)(2)). |
| `non-qualifying-veteran-free-agent-exception-available` | `uses-non-qualifying-veteran-free-agent-exception` | `true` iff the player is in fact a Non-Qualifying Veteran Free Agent (Art. I (rr)) and is contracting with his Prior Team (§6(b)). |
| `minimum-player-salary-exception-salary-equals-minimum` | `uses-minimum-player-salary-exception` | `true` iff **every** Contract signed or acquired under the exception provides, for its first Season, exactly the Minimum Player Salary applicable to that player, with no bonuses of any kind (§6(i)). |
| `taxpayer-mid-level-used-before-row-a-to-f-transaction` | `uses-taxpayer-mid-level-exception` | `true` iff the team had already signed a Contract under the Taxpayer Mid-Level Salary Exception in the same Salary Cap Year and then engaged in a transaction in rows A–F of the Transaction Restrictions Table (§2(e)(2)(iii)(B); rows A–E for 2023-24 under (iii)(A)). See reading 7. |
| `aggregation-outside-december-15-to-trade-deadline` | `uses-aggregated-standard-traded-player-exception` | `true` iff the aggregating trade occurs outside the period from December 15 of the Salary Cap Year through that year's NBA trade deadline (§6(j)(4)(ii)). |
| `aggregation-replacement-count-less-than-traded-count` | `uses-aggregated-standard-traded-player-exception` | `true` iff the number of Replacement Players acquired is fewer than the number of aggregated Traded Players (§6(j)(4)(ii)). |
| `sign-and-trade-uses-non-taxpayer-or-room-mid-level-exception` | `includes-sign-and-trade` | `true` iff the signed-and-traded Contract is signed pursuant to the Non-Taxpayer Mid-Level Salary Exception or the Mid-Level Salary Exception for Room Teams (§8(e)(1)(iii)). |
| `sign-and-trade-assignee-team-has-room` | `includes-sign-and-trade` | `true` iff the acquiring team has Room for the player's first-Season Salary plus Unlikely Bonuses (§8(e)(1)(vii)). |
| `sign-and-trade-fifth-year-eligible-met-higher-max-criteria` | `includes-sign-and-trade` | `true` iff the signed-and-traded player is a 5th Year Eligible Player who met one of the Higher Max Criteria (§8(e)(1)(vi)). |
| `first-round-pick-sold-for-cash` | `includes-first-round-pick-trade` | `true` iff a team sells its first-round selection rights for cash or its equivalent (By-Laws §7.03). |
| `first-round-pick-trade-leaves-consecutive-drafts-without-pick` | `includes-first-round-pick-trade` | `true` iff the trade or exchange may leave the team without first-round picks in any two consecutive future NBA Drafts (By-Laws §7.03). |
| `free-agent-contract-trade-is-initial-sign-and-trade` | `includes-trade-of-recently-signed-free-agent-contract` | `true` iff the trade is the *initial* trade of a Contract signed in connection with a §8(e) agreement, to which the §8(d)(ii) bar does not apply. |
| `free-agent-contract-trade-before-december-15` | `includes-trade-of-recently-signed-free-agent-contract` | `true` iff the trade occurs before December 15 of the Salary Cap Year in which the Contract was signed (§8(d)(ii)). |
| `offer-sheet-first-two-years-at-maximum-allowable` | `offer-sheet-restricted-free-agent-service-1-or-2` | `true` iff the Offer Sheet provides the maximum allowable amount of Salary for the first two Salary Cap Years under Art. XI §5(d)(i). |
| `offer-sheet-third-year-at-maximum-allowable` | `offer-sheet-restricted-free-agent-service-1-or-2` | `true` iff the Offer Sheet provides third-year Salary at the §5(d)(ii) maximum. |
| `offer-sheet-uses-third-year-maximum` | `offer-sheet-restricted-free-agent-service-1-or-2` | `true` iff the Offer Sheet is extended in accordance with §5(d)(ii), which triggers the §5(d)(iii) averaging test for Room. |

### 4.3 Conditional decimal strings (67)

Salary cap and cap holds:

| Field | Present when | Definition |
|---|---|---|
| `ratio-max-post-transaction-team-salary-to-cap-no-exception` | `any-transaction-without-exception` | Worst case over teams transacting without an Exception: that team's Team Salary immediately after the transaction ÷ the Salary Cap (§2(b)(1)). |
| `ratio-post-transaction-team-salary-to-cap` | any of the three `*-hold-included` flags | Worst case over teams: Team Salary immediately after the instance's operations, **including** all Free Agent Amount holds, ÷ the Salary Cap (§4(a), §4(d)). |
| `ratio-post-transaction-team-salary-excluding-qualifying-veteran-free-agent-holds-to-cap` | `qualifying-veteran-free-agent-hold-included` | Same team, same moment, recomputed with every Qualifying Veteran Free Agent hold removed, ÷ the Salary Cap. The hold value is 150% of prior Salary (190% if prior Salary was below the Estimated Average Player Salary), or 250%/300% following a second Option Year of a Rookie Scale Contract, floored and capped by §4(d)(4)–(6). |
| `ratio-post-transaction-team-salary-excluding-early-qualifying-veteran-free-agent-holds-to-cap` | `early-qualifying-veteran-free-agent-hold-included` | Same, removing Early Qualifying holds, valued at 130% of prior Salary (§4(d)(2)). |
| `ratio-post-transaction-team-salary-excluding-non-qualifying-veteran-free-agent-holds-to-cap` | `non-qualifying-veteran-free-agent-hold-included` | Same, removing Non-Qualifying holds, valued at 120% of prior Salary (§4(d)(3)). |
| `ratio-post-signing-team-salary-with-over-38-reattribution-to-cap` | `over-38-contract-present` | Team Salary after the signing, computed **with** the §3(a)(2) pro-rata re-attribution of Over 38 Salaries applied, ÷ the Salary Cap. |
| `ratio-post-signing-team-salary-without-over-38-reattribution-to-cap` | `over-38-contract-present` | The same Team Salary computed **without** any §3(a)(2) re-attribution, ÷ the Salary Cap. |

Maximum Annual Salary (Art. II §7). "First-year amount" always means Salary plus Unlikely Bonuses in
the first Season covered by the Contract; "prior Salary" means the Salary for the final Season of the
player's prior Contract.

| Field | Present when | Definition |
|---|---|---|
| `ratio-max-first-year-salary-to-cap-service-under-7` | `has-new-contract-service-under-7` | Worst case first-year amount ÷ Salary Cap in effect when the Contract is executed. |
| `ratio-max-first-year-salary-to-prior-salary-service-under-7` | `has-new-contract-service-under-7` | The same Contract's first-year amount ÷ its prior Salary. Omit if the player has no prior Contract. |
| `ratio-max-first-year-salary-to-cap-service-7-to-9` | `has-new-contract-service-7-to-9` | As above for the 7-to-9 tier. |
| `ratio-max-first-year-salary-to-prior-salary-service-7-to-9` | `has-new-contract-service-7-to-9` | As above for the 7-to-9 tier. |
| `ratio-max-first-year-salary-to-cap-service-10-or-more` | `has-new-contract-service-10-or-more` | As above for the 10-or-more tier. |
| `ratio-max-first-year-salary-to-prior-salary-service-10-or-more` | `has-new-contract-service-10-or-more` | As above for the 10-or-more tier. |
| `ratio-fifth-year-eligible-first-year-salary-to-cap` | `has-fifth-year-eligible-contract` | 5th Year Eligible Player's first-year amount ÷ the Salary Cap in effect at execution. |
| `ratio-fifth-year-eligible-first-year-salary-to-prior-salary` | `has-fifth-year-eligible-contract` | The same amount ÷ prior Salary. |
| `fifth-year-eligible-contract-seasons` | `has-fifth-year-eligible-contract` | Number of Seasons covered, **excluding** any Option Year and, for a Rookie Scale Extension, excluding the last Season of the Rookie Scale Contract (§7(g)). |
| `ratio-designated-veteran-first-year-salary-to-cap` | `has-designated-veteran-player-contract` | Designated Veteran Player Contract first-year amount ÷ the Salary Cap. |
| `ratio-designated-veteran-first-year-salary-to-prior-salary` | `has-designated-veteran-player-contract` | The same amount ÷ prior Salary. |

Annual increases and decreases (Art. VII §5(a)):

| Field | Present when | Definition |
|---|---|---|
| `max-annual-change-as-fraction-of-first-year-salary-5-percent-group` | `has-contract-governed-by-5-percent-limit` | Worst case over §5(a)(1) Contracts and over Salary Cap Years after the first: \|Salary(y) − Salary(y−1)\| ÷ Salary(first Salary Cap Year), Salary excluding Incentive Compensation. |
| `max-annual-change-as-fraction-of-first-year-salary-8-percent-group` | `has-contract-governed-by-8-percent-limit` | The same quantity over §5(a)(2) Contracts. |

Contract length. Counts are inclusive of any Option Year (Art. IX final sentence).

| Field | Present when | Definition |
|---|---|---|
| `max-contract-seasons-standard` | `has-standard-length-new-contract` | Greatest aggregate Seasons among new Contracts that are not between a Qualifying Veteran Free Agent and his Prior Team. |
| `max-contract-seasons-qualifying-veteran-free-agent-prior-team` | `has-qualifying-veteran-free-agent-prior-team-contract` | Greatest aggregate Seasons among Contracts between a Qualifying Veteran Free Agent and his Prior Team. |
| `max-contract-seasons-non-taxpayer-mid-level` | `uses-non-taxpayer-mid-level-exception` | Greatest term, or remaining term if acquired by assignment, among Contracts under the NTMLE (§6(e)(2)). |
| `max-contract-seasons-taxpayer-mid-level` | `uses-taxpayer-mid-level-exception` | Greatest term among Contracts signed under the Taxpayer MLE (§6(f)(1)). |
| `max-contract-seasons-bi-annual` | `uses-bi-annual-exception` | Greatest term, or remaining term if acquired, under the Bi-annual Exception (§6(d)(2)). |
| `max-contract-seasons-room-mid-level` | `uses-room-mid-level-exception` | Greatest term, or remaining term if acquired, under the Room MLE (§6(g)(2)). |
| `max-contract-seasons-minimum-player-salary` | `uses-minimum-player-salary-exception` | Greatest term among Contracts signed or acquired under the Minimum Player Salary Exception (§6(i)). |
| `min-contract-seasons-early-qualifying-veteran-free-agent` | `uses-early-qualifying-veteran-free-agent-exception` | Smallest number of Seasons, **not** counting a Season covered by an Option Year, among Contracts signed under the EQVFA Exception (§6(b)(3)(i)). |

Veteran Free Agent Exception amounts:

| Field | Present when | Definition |
|---|---|---|
| `ratio-qualifying-veteran-free-agent-first-year-salary-to-maximum-annual-salary` | `uses-qualifying-veteran-free-agent-exception` | Worst case first-year amount ÷ the Maximum Annual Salary applicable to that player under Art. II §7 (§6(b)(1)). |
| `ratio-early-qualifying-veteran-free-agent-first-year-salary-to-prior-salary` | `uses-early-qualifying-veteran-free-agent-exception` | First-year amount ÷ (final-year Regular Salary plus Likely and Unlikely Bonuses of the prior Contract) — the 175% limb of §6(b)(3)(i)(A). |
| `ratio-early-qualifying-veteran-free-agent-first-year-salary-to-average-player-salary` | `uses-early-qualifying-veteran-free-agent-exception` | First-year amount ÷ the Average Player Salary for the prior Salary Cap Year (Estimated Total Salaries substituted if the Audit Report is incomplete) — the 105% limb of §6(b)(3)(i)(B). |
| `ratio-non-qualifying-veteran-free-agent-first-year-salary-to-prior-salary` | `uses-non-qualifying-veteran-free-agent-exception` | First-year amount ÷ (final-year Regular Salary plus Likely and Unlikely Bonuses of the prior Contract) — the 120% limb of §6(b)(2)(i). |
| `ratio-non-qualifying-veteran-free-agent-first-year-salary-to-minimum-annual-salary` | `uses-non-qualifying-veteran-free-agent-exception` | First-year amount ÷ the then-current Minimum Annual Salary applicable to the player — the 120% limb of §6(b)(2)(ii). |

Mid-level, bi-annual, room exception amounts. "Aggregate first-year amount" is the sum, over all
Contracts signed and acquired under that Exception in the Salary Cap Year, of first-Salary-Cap-Year
Salaries and Unlikely Bonuses (post-assignment where acquired). See reading 3.

| Field | Present when | Definition |
|---|---|---|
| `ratio-non-taxpayer-mid-level-aggregate-first-year-salary-to-cap` | `uses-non-taxpayer-mid-level-exception` | Aggregate first-year amount ÷ the Salary Cap (§6(e)(1); limit 9.12%). |
| `ratio-bi-annual-aggregate-first-year-salary-to-cap` | `uses-bi-annual-exception` | Aggregate first-year amount ÷ the Salary Cap (§6(d)(1); limit 3.32%). |
| `ratio-room-mid-level-aggregate-first-year-salary-to-cap` | `uses-room-mid-level-exception` | Aggregate first-year amount ÷ the Salary Cap (§6(g)(1); limit 5.678%). |
| `ratio-taxpayer-mid-level-aggregate-first-year-salary-to-taxpayer-mid-level-amount` | `uses-taxpayer-mid-level-exception` | Aggregate first-year amount ÷ the Taxpayer Mid-Level amount, which is $5,000,000 for 2023-24 and, for later years, $5,000,000 × (Salary Cap for that year ÷ Salary Cap for 2023-24) (§6(f)(1) table). |
| `ratio-post-taxpayer-mid-level-team-salary-to-first-apron` | `uses-taxpayer-mid-level-exception` | The team's Team Salary immediately following its use of the Taxpayer MLE ÷ the First Apron Level. §6(f)(1) requires this to **exceed** 1. |

Apron hard caps. Each is the acting team's Team Salary immediately following that transaction ÷ the
Applicable Apron Level named for that row in the §2(e)(4) Transaction Restrictions Table.

| Field | Present when | Table row |
|---|---|---|
| `ratio-post-bi-annual-transaction-team-salary-to-first-apron` | `uses-bi-annual-exception` | A — First Apron Level |
| `ratio-post-non-taxpayer-mid-level-transaction-team-salary-to-first-apron` | `uses-non-taxpayer-mid-level-exception` | B — First Apron Level |
| `ratio-post-sign-and-trade-acquisition-team-salary-to-first-apron` | `acquires-player-under-sign-and-trade-contract` | C — First Apron Level |
| `ratio-post-expanded-traded-player-exception-transaction-team-salary-to-first-apron` | `uses-expanded-traded-player-exception` | E — First Apron Level |
| `ratio-post-aggregated-traded-player-exception-transaction-team-salary-to-second-apron` | `uses-aggregated-standard-traded-player-exception` | H — Second Apron Level |
| `ratio-post-cash-trade-team-salary-to-second-apron` | `pays-cash-in-trade` | I — Second Apron Level |
| `ratio-post-sign-and-trade-traded-player-exception-team-salary-to-second-apron` | `uses-traded-player-exception-for-signed-and-traded-contract` | J — Second Apron Level |
| `ratio-post-taxpayer-mid-level-transaction-team-salary-to-second-apron` | `uses-taxpayer-mid-level-exception` | K — Second Apron Level |
| `ratio-post-deemed-taxpayer-mid-level-transaction-team-salary-to-second-apron` | `non-taxpayer-mid-level-deemed-taxpayer-mid-level` | K by §6(f)(5) deeming — Second Apron Level. See reading 6. |

Traded Player Exceptions. "Incoming" is the aggregate post-assignment Salaries of the Replacement
Players for the Salary Cap Year of acquisition; "outgoing" is the pre-trade Salary or aggregated
pre-trade Salaries of the Traded Player(s), after the §6(j)(6) protection adjustment. Each "excess
over base limit" is `incoming − base limit`, where the base limit **excludes** the $250,000
allowance — the pack applies the $250,000 itself so that the §6(j)(3) reduction to $0 is expressible.
Values may be negative.

| Field | Present when | Definition |
|---|---|---|
| `standard-traded-player-exception-incoming-excess-over-base-limit` | `uses-standard-traded-player-exception` | incoming − 100% of the Traded Player's pre-trade Salary (§6(j)(1)(i)). |
| `aggregated-traded-player-exception-incoming-excess-over-base-limit` | `uses-aggregated-standard-traded-player-exception` | incoming − 100% of the aggregated pre-trade Salaries (§6(j)(1)(ii)). |
| `room-traded-player-exception-incoming-excess-over-base-limit` | `uses-room-traded-player-exception` | incoming − the team's Room under the Salary Cap (§6(j)(1)(v)). |
| `expanded-traded-player-exception-incoming-excess-over-125-percent-outgoing` | `uses-expanded-traded-player-exception` | incoming − 125% of aggregated pre-trade Salaries — limb (z) of §6(j)(1)(iv). |
| `expanded-traded-player-exception-incoming-excess-over-200-percent-outgoing` | `uses-expanded-traded-player-exception` | incoming − 200% of aggregated pre-trade Salaries — limb (y)(A). |
| `expanded-traded-player-exception-incoming-excess-over-outgoing-in-2023-24-dollars` | `uses-expanded-traded-player-exception` | (incoming − 100% of aggregated pre-trade Salaries) × (Salary Cap for 2023-24 ÷ Salary Cap for the current Salary Cap Year) — limb (y)(B), restated so the pack can compare against the nominal $7,500,000. |
| `traded-player-exception-incoming-excess-over-base-limit-max` | `uses-any-traded-player-exception` | The greatest of the applicable variants' "excess over base limit" values, for the §6(j)(3) $0-allowance test. |
| `ratio-post-trade-team-salary-to-first-apron` | `uses-any-traded-player-exception` | The acquiring team's post-assignment Team Salary ÷ the First Apron Level (§6(j)(3)). |
| `aggregated-traded-player-count` | `uses-aggregated-standard-traded-player-exception` | Number of Traded Players whose Contracts are aggregated (§6(j)(4)(ii)). |
| `minimum-traded-player-count` | `uses-aggregated-standard-traded-player-exception` | Number of those Traded Players who are Minimum Traded Players as defined in §6(j)(4)(ii). |
| `sign-and-trade-deemed-traded-player-exception-incoming-excess-over-base-limit` | `sign-and-trade-qualifying-free-agent-deeming-applies` | incoming − 100% of the assignor's **deemed** outgoing Salary, where the deemed Salary is the greater of the Salary for the last Season of the preceding Contract or 50% of the first-Season Salary of the new Contract (§6(j)(5)). |

Sign-and-trade, cash, post-signing trade bar:

| Field | Present when | Definition |
|---|---|---|
| `sign-and-trade-min-contract-seasons` | `includes-sign-and-trade` | Smallest number of Seasons, excluding any Option Year, among §8(e)(1) Contracts (§8(e)(1)(ii)). |
| `sign-and-trade-max-contract-seasons` | `includes-sign-and-trade` | Largest number of Seasons, excluding any Option Year, among §8(e)(1) Contracts. |
| `ratio-sign-and-trade-first-year-salary-to-cap` | `includes-sign-and-trade` | First-Season Salary plus Unlikely Bonuses ÷ the Salary Cap in effect when the Contract is signed (§8(e)(1)(vi)). |
| `ratio-aggregate-cash-paid-or-received-to-cap` | `includes-cash-in-trade` | Worst case over teams of the greater of total cash **paid** and total cash **received** across all trades in the Salary Cap Year — not netted (§8(a)) — ÷ the Salary Cap. |
| `free-agent-contract-months-elapsed-at-trade` | `includes-trade-of-recently-signed-free-agent-contract` | Smallest number of whole and fractional months between signing and the proposed trade, over the affected Contracts (§8(d)(ii)). |

Offer sheets (Art. XI §5):

| Field | Present when | Definition |
|---|---|---|
| `ratio-offer-sheet-max-first-two-year-salary-to-non-taxpayer-mid-level-amount` | `offer-sheet-restricted-free-agent-service-1-or-2` | The greater of the first and second Salary Cap Year Salary plus Unlikely Bonuses ÷ the Non-Taxpayer Mid-Level Salary Exception amount for that Salary Cap Year (§5(d)(i)). See reading 10. |
| `ratio-offer-sheet-third-year-salary-to-maximum-allowable` | `offer-sheet-restricted-free-agent-service-1-or-2` | Third-year Salary ÷ the maximum the player could have received for the third Salary Cap Year absent §5(d)(i), assuming the first two years were at the Art. II §7(a) maximum (§5(d)(ii)). |
| `ratio-offer-sheet-fourth-year-change-to-third-year-salary` | `offer-sheet-restricted-free-agent-service-1-or-2` | \|Salary(year 4) − Salary(year 3)\| ÷ Salary(year 3) (§5(d)(ii)(A); limit 4.5%). |
| `ratio-offer-sheet-average-salary-to-new-team-room` | `offer-sheet-restricted-free-agent-service-1-or-2` | The average of the aggregate Salaries for every Salary Cap Year covered by the Offer Sheet ÷ the New Team's Room at signing (§5(d)(iii) read with §5(b)). See reading 11. |

---

## 5. Readings taken where the CBA text was ambiguous

Numbered so rule `rationale` fields can cite them.

1. **"The greater of (x) … or (y) 105% …" is a disjunctive ceiling.** Art. II §7(a) sets the maximum
   as the greater of a cap percentage and 105% of prior Salary. A Contract is therefore illegal only
   if it exceeds **both** limbs, so each maximum-salary rule is a conjunction of two ratio tests.
   Text relied on: "the greater of (x) twenty-five percent (25%) of the Salary Cap … or (y) one
   hundred five percent (105%) of the Salary for the final Season of the player's prior Contract".
   The same disjunctive reading is applied to §6(b)(2) (120%/120%) and §6(b)(3)(i) (175%/105%).

2. **The three service tiers are made disjoint from the two proviso classes.** Art. II §7(a)(i)
   contains a proviso raising 25% to 30% for a 5th Year Eligible Player, and §7(a)(ii) a proviso
   raising 30% to 35% for a Designated Veteran Player Contract. A single ratio field cannot carry
   two different ceilings, so the preprocessor partitions new Contracts: 5th Year Eligible Prior-Team
   Contracts go **only** into the `fifth-year-eligible-*` fields, Designated Veteran Player Contracts
   **only** into the `designated-veteran-*` fields, and the `service-under-7` / `service-7-to-9`
   fields carry the remainder. The alternative — leaving them in the tier and subtracting with a
   `not` — would have made the ceiling depend on a fact the tier rule does not read.

3. **"In the aggregate" is a sum over the Salary Cap Year, not a per-contract test.** §6(d)(1),
   §6(e)(1), §6(f)(1), and §6(g)(1) each say the Contracts signed and/or acquired "in the aggregate,
   provide for Salaries and Unlikely Bonuses … in the first Salary Cap Year totaling up to" the
   limit. The derived fields therefore sum across all Contracts under that Exception in the year,
   rather than taking a worst case.

4. **Contract-length counts include Option Years except where the text says otherwise.** Art. IX
   closes: "the maximum Contract and Extension lengths described herein are inclusive of any Option
   Year". So `max-contract-seasons-*` counts Option Years. Two provisions say the opposite and are
   encoded accordingly: §8(e)(1)(ii) ("at least three (3) Seasons (excluding any Option Year)") and
   §6(b)(3)(i) ("at least two (2) Seasons (not including a Season covered by an Option Year)").
   Art. II §7(g) also excludes Option Years and, for a Rookie Scale Extension, the last Season of
   the Rookie Scale Contract.

5. **The 5%/8% band is measured against the first year, not the previous year.** §5(a)(1)(i)(A) and
   §5(a)(2)(i)(A) both say the change may be "no more than five percent (5%) [eight percent (8%)] of
   the Salary for the first Salary Cap Year covered by the Contract", so the denominator of
   `max-annual-change-as-fraction-of-first-year-salary-*` is the first year's Salary even though the
   difference is taken year over year.

6. **`non_taxpayer_mid_level_exception_hard_cap_second_apron_level` is read through §6(f)(5).** The
   Transaction Restrictions Table has no Non-Taxpayer-MLE row at the Second Apron Level; row B is
   First Apron and row K (Taxpayer MLE) is Second Apron. The only text that produces a Second Apron
   hard cap from a Non-Taxpayer MLE signing is §6(f)(5): a team that used the NTMLE within Taxpayer
   MLE limits and then exceeds the First Apron "will be deemed to have used the Taxpayer Mid-Level
   Salary Exception instead of the Non-Taxpayer Mid-Level Salary Exception for all purposes under
   this Article VII". That deeming carries the row K restriction. This is the reading encoded.
   *Alternative rejected:* treating the annotation name as an error and leaving it unencoded, which
   would have cost recall on a genuinely supported provision.

7. **`taxpayer_mid_level_exception_hard_cap_first_apron_level` is read as §2(e)(2)(iii)(B).** There
   is likewise no Taxpayer-MLE row at the First Apron Level. The nearest concrete text is
   §2(e)(2)(iii)(B): "a Team may not engage in any transaction set forth in rows A through F of the
   Transaction Restrictions Table if it has previously signed a Player Contract pursuant to the
   Taxpayer Mid-Level Salary Exception during such Salary Cap Year" — and every one of rows A–F is a
   First-Apron-Level transaction. The rule is encoded as an outright prohibition (two booleans, no
   ratio) rather than as a numeric hard cap, because the text bars the transaction regardless of the
   resulting Team Salary. *Alternative rejected:* §6(f)(1)'s requirement that Team Salary after use
   *exceed* the First Apron — that is a floor, not a cap, and it is encoded inside
   `taxpayer-mid-level-exception` instead.

8. **`salary_space_consumption_*` are encoded as decisive-cap tests, not as attribution rules.**
   Art. VII §4(d) tells you *how much* an unsigned free agent counts against his Prior Team's Team
   Salary (150%/190%, 250%/300%, 130%, 120% of prior Salary). It states no prohibition of its own.
   Encoding it as "the included amount must equal the required amount" would produce a rule that can
   never fire, because the same preprocessor computes both sides. Instead each rule fires when the
   hold is *decisive*: the team is over the Salary Cap with the hold counted and at or under it with
   the hold removed. This is the only form in which §4(d) has an observable legality consequence a
   fact-comparison language can express. The attribution arithmetic itself is out of scope (§3).

9. **`defer_compensation_*` (Over 38) are encoded the same way.** Art. VII §3(a)(2) re-attributes
   Over 38 Salaries to earlier Salary Cap Years; like §4(d) it states no prohibition. Each rule
   fires when the re-attribution is decisive: Team Salary exceeds the Salary Cap with §3(a)(2)
   applied and does not without it. §3(a)(2)(ii) (a five-Season Over 38 Contract with a Qualifying
   Veteran Free Agent aged 35 or 36) is separated from the general §3(a)(2)(i) case because the
   benchmark vocabulary names it separately; §3(a)(2)(iv) (four or fewer Seasons at age 35 or 36, no
   re-allocation at all) is folded into the preprocessor's definition of
   `over-38-contract-present`, which must be `false` for such a Contract.

10. **`offer_sheet_…_no_more_than_mid_level_in_first_2_year` covers two years.** Art. XI §5(d)(i)
    literally restricts only "the first Salary Cap Year", leaving the second year bounded by the 5%
    rule in Art. VII §5(a)(1). The benchmark's identifier names the first *two* years, and §5(d)(ii)
    speaks of "the maximum allowable amount of Salary for the first two (2) Salary Cap Years pursuant
    to Section 5(d)(i)", which treats the §5(d)(i) ceiling as governing both. The derived field
    therefore takes the greater of the first two years' amounts.

11. **`offer_sheet_…_average_salary_more_than_2_year` is the §5(d)(iii) Room test.** Art. XI
    §5(d)(iii) provides that for an Offer Sheet extended under §5(d)(ii) — which necessarily runs
    more than two Salary Cap Years — "for purposes of determining whether the Team has Room for the
    Offer Sheet, the Salary for the first Salary Cap Year … shall be deemed to equal the average of
    the aggregate Salaries". Read together with §5(b) ("the New Team must have Room for the player's
    Player Contract at the time the Offer Sheet is signed"), the violation is the New Team lacking
    Room for that average. Encoded as `ratio-offer-sheet-average-salary-to-new-team-room > 1`.

12. **Variant annotation spellings are encoded as separate rule objects with identical conditions.**
    The benchmark's vocabulary contains the same provision under more than one name. Six pairs are
    byte-identical in their `when`: `salary-increase-and-decrease-ratio-for-qualiyfing-…` /
    `salary-increase-and-decrease-ratio-qualiyfing-…`; `qualifying-veteran-free-agent-exception` /
    `qualified-veteran-free-agent-exception`; `non-taxpayer-mid-level-exception` /
    `nontaxpayer-mid-level-exception`; `non-taxpayer-mid-level-exception-hard-cap-first-apron-level`
    / `nontaxpayer-mid-level-exception-hard-cap-first-apron-level`;
    `defer-compensation-qualifying-veteran-free-agent-38-year-old` /
    `defer-compensation-38-year-old-qualifying-veteran-free-agent-38-year-old`;
    `offer-sheet-…-4th-year-maximum-if-first-3-year-maximum` / `offer-sheet-…-4th-year-maximum-if-3-year`.
    A seventh pair is nested rather than identical: `stepien-rule-no-sell-or-no-consecutive-…` covers
    both limbs of By-Laws §7.03 while `stepien-rule-no-consecutive-…` covers only the
    consecutive-Drafts limb, so the narrower rule fires on a strict subset of the broader one's
    instances. **This inflates raw citation counts** for any instance in one of these families: both
    ids of a pair will always fire together. Citation precision and recall should be computed with
    that in mind — the honest options are to report the raw numbers alongside a
    variant-collapsed number, or to treat each pair as one citation.

13. **Transaction Restrictions Table rows F and G are not encoded.** Row F (Standard Traded Player
    Exception used after the end of the Regular Season in which it arose) and row G (Transition
    Traded Player Exception, 2023-24 only) both turn on the Regular Season calendar relative to when
    the exception arose. Neither has a benchmark citation name, and the facts contract carries no
    such dates. `taxpayer-mid-level-used-before-row-a-to-f-transaction` still refers to rows A–F as
    a set, because §2(e)(2)(iii)(B) names them as a set.

14. **Sign-and-trade conditions (i), (iv) and (v) are not encoded.** §8(e)(1) has seven conditions.
    Four have benchmark citation names and are encoded — (ii) term, (iii) mid-level bar, (vi) 25%
    cap for Higher-Max 5th Year Eligible Players, (vii) assignee Room. Conditions (i) (the free agent
    finished the prior Season on his Prior Team's roster), (iv) (first Season fully protected for
    lack of skill), and (v) (entered into before the first day of the Regular Season) have no
    citation name. Encoding them would emit rule ids that appear in no gold annotation and would
    depress measured citation precision without any corresponding recall gain, so they are recorded
    here as a known under-encoding rather than added.

15. **Nominal dollar constants are held in the pack; the scaling is done outside it.** $250,000
    (§6(j)(1)(i)–(v)) and $7,500,000 (§6(j)(1)(iv)(y)(B)) are fixed figures and appear as literals in
    the rules. The 2023-24 indexation of the $7.5 million allowance and of the $5 million Taxpayer
    Mid-Level amount is handled by restating the compared quantity — respectively
    `…-incoming-excess-over-outgoing-in-2023-24-dollars` and
    `ratio-taxpayer-mid-level-aggregate-first-year-salary-to-taxpayer-mid-level-amount` — so the
    multiplication happens in the preprocessor while the CBA's stated figure stays visible in the
    pack.

---

## 6. Reproducing the checks

```
judgment-pack spec validate packs/nba-transaction-legality.json          # exit 0
judgment-pack experimental evaluate packs/nba-transaction-legality.json \
    --facts <facts.json> --format json                                   # no --evidence
```

Observed behaviour on synthetic facts, for the harness author:

| Facts | Disposition |
|---|---|
| Every always-present boolean `false` | `outcome: legal` |
| `any-transaction-without-exception: true`, ratio `"1.04"` | `outcome: illegal`, one rule fired |
| Three independent violations | `outcome: illegal`, three rules fired, **no conflict** |
| `uses-non-taxpayer-mid-level-exception: true`, its amounts omitted | `unresolved`, reasons `["unknown"]`, handoff requested |
| `contains-provision-outside-pack-scope: true` | `unresolved`, reasons `["exception-escalation"]`, handoff requested |
