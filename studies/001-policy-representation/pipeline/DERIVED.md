# `facts.derived` — the derived-field contract, as actually implemented

`derive.py` is the study's published deterministic preprocessor. It fills
`facts.derived` with the 124 fields that `packs/nba-transaction-legality.json`
reads through `/facts/derived/*` pointers, per the contract in
`packs/COVERAGE.md` §4.

Reproduce:

```bash
python pipeline/parse_nba.py --checkout rulearena/checkout --out pipeline/out/facts --strict
python pipeline/derive.py --facts pipeline/out/facts --out pipeline/out/facts --strict
python pipeline/redact.py                       # -> pipeline/out/twins
python pipeline/derive.py --facts pipeline/out/twins --out pipeline/out/twins
python pipeline/derive.py --readings            # the numbered readings, R1-R10
```

Python 3.10+, standard library only, no network. Two runs produce byte-identical
files; the transform is idempotent (any pre-existing `facts.derived` is discarded
and recomputed).

---

## 1. Result

| | |
|---|---|
| Instances processed | 216 (facts) / 432 (twins) |
| Always-present booleans emitted on every instance | **39 / 39** |
| Distinct contract fields emitted at least once | **123 / 124** |
| Fields emitted with a value that is not a JSON boolean or a JPS decimal string | **0** |
| Instances with at least one omitted conditional field | 95 / 216 |
| Omitted-field events over the 216 facts documents | 354, across 27 distinct fields |

An omitted field is not a bug. §4 of `COVERAGE.md` fixes the discipline:
**absent ⇒ `unknown` ⇒ escalate**. Omitting is how the pipeline says "I do not
know", and it is always preferred to inventing a number.

---

## 2. Where the arithmetic comes from

`reference_rules.txt` — the CBA excerpt RuleArena distributes — contains **no
dollar amounts at all**. Every threshold in it is a percentage or a formula. The
absolute figures come from the assumption block RuleArena itself prepends to
every NBA prompt (`rulearena/checkout/nba/auto_test.py`, `prompt_template`), so
the preprocessor uses exactly the numbers the benchmark gives its models:

| Constant | Value | Source |
|---|---|---|
| Salary Cap, 2024-25 | `$140,588,000` | benchmark stipulation |
| Salary Cap, 2023-24 | `$136,000,000` | benchmark stipulation |
| Average Player Salary, 2023-24 | `$9,700,000` | benchmark stipulation |
| Luxury Tax | `$170,814,000` | benchmark stipulation |
| First Apron Level | `$178,132,000` | benchmark stipulation |
| Second Apron Level | `$188,931,000` | benchmark stipulation |
| Non-Taxpayer Mid-Level amount | 9.12% × Cap = `$12,821,625.60` | Art. VII §6(e)(1) |
| Bi-annual amount | 3.32% × Cap = `$4,667,521.60` | Art. VII §6(d)(1) |
| Room Mid-Level amount | 5.678% × Cap = `$7,982,586.64` | Art. VII §6(g)(1) |
| Taxpayer Mid-Level amount | $5M × Cap ÷ Cap(2023-24) = `$5,168,676.47…` | Art. VII §6(f)(1) table |
| Traded Player Exception allowance | `$250,000` | Art. VII §6(j)(1)(i)–(v) |

`test_derive.py::test_benchmark_constants_match_rulearena_prompt` greps the
checkout so these cannot drift silently.

Arithmetic is `decimal.Decimal` at 40 digits of precision. Ratios are emitted as
decimal strings quantised to 12 fractional digits with trailing zeros stripped,
so every value matches the JPS §2.2 grammar `-?(0|[1-9][0-9]*)(\.[0-9]+)?`.

---

## 3. Fields that CANNOT be computed from the available facts

### G-MIN — the Minimum Player Salary / Minimum Annual Salary schedule

**Not in the CBA excerpt. Not in the benchmark's stipulation block. Not
anywhere in the pinned checkout.** The excerpt refers to the Minimum Player
Salary repeatedly (§4(d)(4), §4(d)(5), §6(b)(2)(ii), §6(i)) but never states a
figure, and RuleArena's prompt does not supply one either.

108 of 727 player contracts and 12 of 380 operation contracts in the corpus are
stated as "minimum applicable player salary". **77 of 216 instances contain at
least one.**

Consequences, all of them deliberate omissions:

| Field | Status |
|---|---|
| `ratio-non-qualifying-veteran-free-agent-first-year-salary-to-minimum-annual-salary` | **Never emitted, on any instance.** This is the one field of the 124 with zero coverage. Its rule's other limb (120% of prior Salary) is still emitted, so where that limb is satisfied the rule still fires. |
| Any team-salary ratio for a team that signs, acquires or sends a minimum-salary contract | Omitted for that instance |
| `standard-` / `aggregated-` / `room-traded-player-exception-incoming-excess-over-base-limit` where a traded player is on a minimum contract | Omitted |
| `max-annual-change-as-fraction-of-first-year-salary-{5,8}-percent-group` for a minimum contract | Omitted |

What is **not** blocked: `minimum-player-salary-exception-salary-equals-minimum`
is computed from the prose flag itself (a contract the source describes as "a
minimum applicable player salary" is at the minimum by construction; one carrying
`minimum_plus_amount` is not), and `max-contract-seasons-minimum-player-salary`
needs only the term.

Fixing G-MIN requires adding the Art. II §6 Minimum Annual Salary scale as a
declared, cited constant table. That would be a change to the benchmark's
information set, so it is **not** done here: arms A and A-prime do not get the
schedule either, and giving it only to the preprocessor would advantage arm B.

### G-AMBIG — the parser's two documented ambiguities

`parse_nba.py` refuses to resolve two structures, and `derive.py` refuses to
paper over them (reading R9). 8 of 216 instances are affected.

| Structure | Instances | Effect |
|---|---|---|
| `trade.to_team` is `null` ("Team A trades Player A for Player B.") | 4 | Every post-trade team-salary ratio and every TPE excess for that operation is omitted |
| `third_team_asset_binding: "unresolved"` (three-team "Simultaneously in this trade") | 4 | Same |

### G-HISTORY — provisions needing prior-Salary-Cap-Year state

`COVERAGE.md` §3 already declares these out of pack scope. `derive.py` therefore
never has to compute them, and `contains-provision-outside-pack-scope` is
`false` on all 216 instances (no operation in the corpus is unparsed or of an
unencoded type). The Bi-annual Exception is claimed only where the facts state it
explicitly (1 team, 4 player contracts); it is never inferred, because inferring
it needs the previous year's exception ledger.

---

## 4. Fields that require legal characterisation, not arithmetic — read this

This is the most important caveat in the file, and it is a study finding rather
than an implementation detail.

`COVERAGE.md` §4.1 asks for 13 `uses-*` booleans naming **which Salary Cap
Exception each transaction invokes**. RuleArena's prose never states one. Working
out that a team re-signing its own free agent above the Non-Bird limit is
claiming Bird rights, or that an over-the-apron team signing an outside free
agent must be on the Taxpayer Mid-Level, *is* the legal reasoning the benchmark
is testing. It is not computation.

`derive.py` performs it anyway, because the pack cannot: JPS has no arithmetic
and no way to search a space of exception assignments. The assignment is done by
an explicit, deterministic waterfall — reading **R5** for signings, **R7** for
Traded Player Exceptions — printed by `python derive.py --readings` and pinned by
unit tests. The full list:

```
R1  Years of Service = 2024 - draft year.
R2  Age during 2024-25 = age at draft + (2024 - draft year).
R3  Annual increases are linear on the first-year Salary (Art. VII 5(a)).
R4  Free-agency class from coverage of the three preceding Seasons:
    3+ -> Qualifying, 2 -> Early Qualifying, 1 -> Non-Qualifying.
R5  Signing exception waterfall: explicit Bi-annual flag; then a Contract at the
    minimum -> Minimum Player Salary Exception; then the Prior Team re-signing
    its own free agent -> the lowest 6(b) tier whose limb covers the amount;
    then Room; then below the Cap with insufficient Room -> Room Mid-Level;
    then above the First Apron -> Taxpayer Mid-Level; otherwise Non-Taxpayer
    Mid-Level.
R6  "Without an Exception" = no tier in R5 can accommodate the amount.
R7  TPE variant per acquiring team: Room TPE if below the Cap and incoming fits
    Room + $250,000; Aggregated Standard if two or more players go out;
    Expanded if incoming exceeds 100% of outgoing plus $250,000; else Standard.
R8  A team carries a Free Agent Amount hold for each of its own free agents
    named in the instance who is not signed by anyone in the instance.
R9  Unstated trade destination or unresolved three-team binding -> omit.
R10 An operation with no stated date is in the 2024 offseason, outside the
    December 15-to-deadline aggregation window.
```

**What this means for interpreting the study.** Arm B's accuracy is jointly
produced by the pack and by R5/R7. A wrong exception assignment shows up as an
arm-B error even when the pack's encoding of the provision is correct. The same
`facts.derived` block is given to arms A and A-prime, so the *comparison* is not
biased — all three arms are handed the same characterisation — but the absolute
numbers are not a clean measure of the pack alone. Any write-up must say so.

A cleaner design would push exception selection into the pack as an ordered set
of eligibility rules. JPS 0.1.0-draft cannot express it: choosing "the lowest
tier whose limb covers the amount" needs comparison against a computed limb, and
computing the limb needs arithmetic.

Two smaller characterisation choices, both documented as readings rather than
computations:

* **Designated Veteran Player Contract** (`has-designated-veteran-player-contract`)
  additionally requires a Higher Max Criterion, following Art. II §7(a)(ii)
  ("shall be eligible to enter into a Designated Veteran Player Contract … if the
  player has met at least one of the Higher Max Criteria"). `COVERAGE.md` §4.1
  states only the service and continuity limbs.
* **Higher Max Criteria** count All-NBA first/second/third team, Defensive Player
  of the Year and MVP. All-Defensive selections — which the corpus contains
  (`all_nba_defensive_second_team`, 3 occurrences) — are **not** a Higher Max
  Criterion and are treated as not qualifying.

---

## 5. Per-field notes where the implementation had to choose

| Field | Note |
|---|---|
| `contains-provision-outside-pack-scope` | `true` only for an unparsed operation or an operation type the pack does not encode. **`false` on all 216 instances.** |
| `any-transaction-without-exception` | Reading R6. A team can be simultaneously "using the Non-Taxpayer Mid-Level" and "without an exception" when the amount exceeds the limit; both rules resolve to `illegal`, so they agree rather than conflict. |
| `*-exception-available` | Computed by comparing the tier *claimed* under R5 against the player's actual Art. I class, ordered Non-Qualifying < Early Qualifying < Qualifying. Without the claimed/actual split these fields would be `true` by construction and their rules could never fire. |
| `qualifying-veteran-free-agent-hold-included` and siblings | Reading R8. Holds are counted only for free agents the instance actually names and nobody signs. |
| `over-38-*` re-attribution | Salaries from the later of the fourth Salary Cap Year and the first Season after the player's 38th birthday are pushed pro rata onto the earlier Seasons, and the first Season's share is what enters Team Salary. |
| `free-agent-contract-months-elapsed-at-trade` | Signing is placed at the 2024 Moratorium Period (July 1). An operation with no stated date, or one the source calls "immediately", is 0 months. |
| `aggregation-outside-december-15-to-trade-deadline` | Reading R10. Only 7 operations in the corpus carry an explicit date. |
| `ratio-offer-sheet-third-year-salary-to-maximum-allowable` | Denominator is the player's Art. II §7(a) Maximum Annual Salary escalated by two years of 5% increases, per Art. XI §5(d)(ii)'s "assuming the first two years were at the maximum". |
| `ratio-offer-sheet-average-salary-to-new-team-room` | Omitted when the New Team's Room is zero or negative — the ratio is undefined, per the §4 preamble. |
| `sign-and-trade-deemed-traded-player-exception-incoming-excess-over-base-limit` | Deemed outgoing Salary is `max(prior Salary, 50% of the new first-Season Salary)`, per Art. VII §6(j)(5). |
| Aggregation "worst case" | Where a field is a maximum over teams or contracts and **any** contributor is unknown, the whole field is omitted: an unknown contributor could be the maximum, so reporting the maximum of the known ones would understate it. |

---

## 6. Diagnostics

`pipeline/out/derive-report.json` (and `derive-report-twins.json`) records, for
every run:

* the constants used, including the two that are `null` (G-MIN);
* `field_presence` — how many instances carry each field;
* `omission_counts` — how many instances omitted each field;
* `non_conforming_values` — any emitted value that is not a boolean or a JPS
  decimal string (always empty; `--strict` exits non-zero if not);
* `per_instance` — the omitted-field list for every instance.

The ten most-omitted fields over the 216 facts documents:

| n | field |
|---:|---|
| 38 | `ratio-max-first-year-salary-to-prior-salary-service-under-7` |
| 31 | `ratio-post-sign-and-trade-acquisition-team-salary-to-first-apron` |
| 31 | `ratio-post-trade-team-salary-to-first-apron` |
| 29 | `ratio-post-aggregated-traded-player-exception-transaction-team-salary-to-second-apron` |
| 29 | `traded-player-exception-incoming-excess-over-base-limit-max` |
| 28 | `aggregated-traded-player-exception-incoming-excess-over-base-limit` |
| 28 | `standard-traded-player-exception-incoming-excess-over-base-limit` |
| 27 | `ratio-post-sign-and-trade-traded-player-exception-team-salary-to-second-apron` |
| 22 | `max-annual-change-as-fraction-of-first-year-salary-5-percent-group` |
| 20 | `ratio-non-qualifying-veteran-free-agent-first-year-salary-to-minimum-annual-salary` |

Every one of these traces to G-MIN or G-AMBIG.
