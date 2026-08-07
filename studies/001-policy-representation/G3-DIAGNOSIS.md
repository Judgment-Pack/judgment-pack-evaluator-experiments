# G-3 diagnosed — the 18 false `illegal` verdicts, one instance at a time

**What G-3 is.** Arm B calls 18 of the 37 gold-legal answerable instances
`illegal`. It was filed as gap G-3 in [`PIPELINE-STATUS.md`](PIPELINE-STATUS.md)
§7 — *"18 false `illegal` verdicts on gold-legal instances, undiagnosed … Most
likely cause is G-2: an over-eager exception assignment … Someone should walk
those 18 traces"* — and repeated in
[`RESULTS-FIRST-PROMPT-ARMS.md`](RESULTS-FIRST-PROMPT-ARMS.md) as *"A second,
undiagnosed error concentration (G-3) … The cause is unknown."* This file walks
the 18 traces and names a cause for each.

**The short answer.** The speculation in §7 is right in form and wrong in
weight. A `derive.py` mischaracterisation is decisive on 6 of the 18 — a wrong
Salary Cap Exception assignment on five of them, exactly as §7 guessed.
The pack's own encoding of four CBA provisions is decisive on 8. Two are cases
where the pack's `illegal` is defensible against the CBA excerpt and
RuleArena's gold is not. Two turn on a defined term the pinned excerpt never
defines. No instance traces to a parser fault.

**The other short answer, which matters more.** Applying diagnostic probes
for four of the five `derive.py` mechanisms found here (M2b has no probe, and
a probe is an isolation, not a repair — §6) *lowers* arm B's accuracy on the
answerable population, from 0.579 to 0.551, because the same defects were also
producing correct `illegal` verdicts on 12 gold-illegal instances. G-2's
caveat — "the score partly measures `derive.py`" — is not an additive
correction term. See §6.

---

## 1. Method

Arm B is deterministic; all five retained trials agree on all 18 rows, so trial
1 is the whole record. For each row:

1. The 18 row ids and their fired rules came from the retained k = 5 log
   (`results/pilot-B-runtime.jsonl`). All 90 retained envelopes for these rows
   carry `status: "evaluated"`, `disposition.kind: "outcome"`, `outcomeId:
   "illegal"`, a 62-entry trace and a null `error`.
2. The trace records *which* rules fired but not *why*, so the pack's condition
   semantics (`all` / `any` / `fact` with `equals`, `greater-than`,
   `less-than-or-equal`) were re-implemented over the instance document and run
   against every rule. **The re-implementation reproduces the runtime's fired
   set exactly on all 18 rows**, which is what licenses reading the condition
   trees as the explanation.
3. `derive.py` was imported and instrumented to expose the intermediate
   characterisations it never emits — each player's `under_contract`,
   `fa_class`, `prior_team` and `prior_salary`; each signing's assigned
   exception and claimed tier; each trade leg's Traded Player Exception variant
   with its incoming and outgoing totals.
4. Each fired rule's inputs were traced back to the raw facts and checked
   against `rulearena/checkout/nba/reference_rules.txt`, against RuleArena's own
   rule descriptions in `micro_evaluation.py`, and against the instance prose in
   `annotated_problems/`. Contract schedules and team salaries were recomputed
   by hand from the checkout prose for every instance discussed below.
5. **Each diagnosis was then verified by counterfactual through the same
   binary.** For a `derive.py` cause, the named reading was patched in memory,
   the instance re-derived from the pinned twin, and `judgment-pack 0.2.0`
   re-run on the result. For a pack cause, the named derived field was set to
   the value a correct encoding of the cited provision implies, and the binary
   re-run. Every claim of the form "field X is what produced `illegal`" in §3
   is a claim that the runtime returned `legal` on that document. The
   unpatched control is exact: re-deriving all 216 answerable twins from the
   pinned instance files and re-running the binary reproduces the recorded
   arm-B distribution to the row — 133 `illegal`, 60 `cannot_decide`, 23
   `legal`, accuracy 0.5787.

The counterfactual patches are **diagnostic probes, not proposed repairs**.
They are the smallest change that isolates a cause; several are deliberately
coarse and §6 shows what that costs.

**Classification rule for instances with more than one fired rule.** An
instance returns `legal` only when every fired rule is dispelled, so each
instance is classified by *the cause that survives every other correction* —
the last cause standing. Where two survive, the one that does not depend on an
undefined term is preferred. All contributing causes are listed in the table
and narrated in §3.

---

## 2. The 18, per instance

Rule keys are expanded in the legend below the table. Gold `relevant_rules`
lists run to 18 entries on the sign-and-trade instances; the column gives the
gold rules that bear on the disagreement, and the full lists are in
`pipeline/out/twins/<row_id>.json`.

| row_id | gold relevant_rules (bearing on the disagreement) | fired rule(s) | outcome | cause | mechanism |
| --- | --- | --- | --- | --- | --- |
| `comp_0-022__answerable` | `early_qualifying_veteran_free_agent_exception`, `salary_increase…_for_qualiyfing_or_early_qualifying…` | R-CAP, R-5PCT, R-NTMLE ×2 | `illegal` | **a** | Player A's declined player option is ignored, so he is still "under contract", has no free-agency class, and his own team's re-signing falls through the R5 waterfall to the Non-Taxpayer Mid-Level |
| `comp_0-024__answerable` | `qualifying_veteran_free_agent_exception`, `salary_increase…_for_…` | R-CAP, R-5PCT, R-NTMLE ×2 | `illegal` | **a** | same declined-option defect; Bird rights lost, $30,000,000 tested against the $12,821,625.60 mid-level |
| `comp_0-025__answerable` | `early_qualifying_veteran_free_agent_exception`, `salary_increase…_for_…` | R-CAP, R-5PCT, R-NTMLE ×2 | `illegal` | **a** | same declined-option defect |
| `comp_0-026__answerable` | `salary_cap_no_exceed_without_exception`, `salary_increase…_except_…` | R-CAP, R-5PCT, R-NTMLE ×2 | `illegal` | **c** | Team A is over the Cap with no Exception reaching $17,800,000, and gives 8% raises to a player whose Prior Team is Team D; both are violations on the excerpt's text |
| `comp_0-027__answerable` | `traded_player_exception_for_room_team`, `standard_traded_player_exception` | R-EXPTPE | `illegal` | **a** | Room is measured against Team B's *pre-trade* salary, so the Expanded TPE is assigned to a trade that fits §6(j)(1)(v) Room + $250,000 once the outgoing contract is removed |
| `comp_0-028__answerable` | `non_taxpayer_mid_level_exception`, `sign_and_trade_assignee_team_has_room` | R-EXPTPE, R-STROOM | `illegal` | **e** | assignee Team B can acquire the $12,400,000 contract under its Non-Taxpayer Mid-Level (a route R7 never considers), but §8(e)(1)(vii)'s "Room" requirement remains, and "Room" is undefined in the pinned excerpt |
| `comp_0-029__answerable` | `aggregated_standard_traded_player_exception`, `expanded_traded_player_exception_hard_cap_first_apron_level` | R-AGGTPE, R-250K, R-STROOM | `illegal` | **c** | Team A ends at $181,475,000, above the First Apron, so §2(e)(4) row E bars the Expanded TPE and §6(j)(3) cuts the allowance to $0; it takes back $3,475,000 more than it sends |
| `comp_0-032__answerable` | `sign_and_trade_qualifying_free_agent_half_salary…`, `expanded_traded_player_exception` | R-AGGTPE, R-STROOM, R-STDEEM | `illegal` | **b** | after the Room correction only R-STDEEM survives: it tests the §6(j)(5) deemed base at 100% + $250,000 only, though §6(j)(1)(iv) lets the assignor use the Expanded limb |
| `comp_0-054__answerable` | `offer_sheet…_3rd_year_maximum_if_first_2_year_maximum`, `offer_sheet…_4th_year_maximum…` | R-5PCT, R-OSMLE | `illegal` | **b** | R-OSMLE bounds the *first two* years by the mid-level where Art. XI §5(d)(i) bounds only the first; R-5PCT applies Art. VII §5(a)(1) to the year-3 step that Art. XI §5(d)(ii) governs |
| `comp_0-065__answerable` | `defer_compensation_38_year_old_qualifying_veteran_free_agent_38_year_old` | R-OVER38 | `illegal` | **b** | the Over-38 rule encodes only the §3(a)(2)(ii) five-season carve-out; §3(a)(2)(iv) bars re-allocation entirely for a 35-year-old Qualifying Veteran Free Agent re-signing with his Prior Team for four Seasons |
| `comp_0-073__answerable` | `offer_sheet…_3rd_year_maximum_if_first_2_year_maximum` | R-5PCT | `illegal` | **b** | same Art. XI §5(d)(ii) omission; the year-2→year-3 step is 1.3398 of the first-year Salary |
| `comp_0-074__answerable` | `salary_space_consumption_early_qualifying_veteran_free_agent`, `qualifying_veteran_free_agent_exception` | R-HOLD | `illegal` | **a** | Team B matches the Offer Sheet for Player B, but a match is not counted as a signing, so his $10,925,000 Free Agent Amount hold is retained and puts Team B over the Cap by itself |
| `comp_0-079__answerable` | `early_qualifying_veteran_free_agent_exception`, `salary_increase…_for_…` | R-CAP, R-5PCT, R-NTMLE ×2 | `illegal` | **a** | same declined-option defect |
| `comp_1-069__answerable` | `sign_and_trade_assignee_team_has_room`, `aggregated_standard_traded_player_exception` | R-STROOM | `illegal` | **e** | assignee Team B sheds $44,100,000 to take back $42,000,000 and is over the Cap throughout; §8(e)(1)(vii)'s "Room" is the only failing condition and the term is undefined in the excerpt |
| `comp_1-071__answerable` | `sign_and_trade_qualifying_free_agent_half_salary…`, `stepien_rule…`, `pay_or_receive_cash_maximum_in_a_year` | R-AGGTPE, R-STROOM, R-STDEEM, R-STEPIEN | `illegal` | **b** | R-STDEEM as in `comp_0-032`; R-STEPIEN additionally fires because a leg that sends a first-round pick *and receives one* is read as a sale for cash |
| `comp_1-072__answerable` | as `comp_1-071` | R-AGGTPE, R-STROOM, R-STDEEM, R-STEPIEN | `illegal` | **b** | as `comp_1-071` |
| `comp_1-078__answerable` | `sign_and_trade_qualifying_free_agent_half_salary…`, `expanded_traded_player_exception` | R-AGGTPE, R-STROOM, R-STDEEM | `illegal` | **b** | as `comp_0-032` |
| `comp_1-079__answerable` | as `comp_1-078` | R-AGGTPE, R-STROOM, R-STDEEM | `illegal` | **b** | as `comp_0-032` |

**Rule key.**

| key | pack rule id |
| --- | --- |
| R-CAP | `salary-cap-no-exceed-without-exception` |
| R-5PCT | `salary-increase-and-decrease-ratio-except-qualiyfing-or-early-qualifying-veteran-free-agent` |
| R-NTMLE ×2 | `non-taxpayer-mid-level-exception` and `nontaxpayer-mid-level-exception` (the same provision under both of RuleArena's spellings — gap G-12) |
| R-EXPTPE | `expanded-traded-player-exception` |
| R-AGGTPE | `aggregated-standard-traded-player-exception` |
| R-250K | `traded-player-exception-250k-reduced-first-apron-level` |
| R-STROOM | `sign-and-trade-assignee-team-has-room` |
| R-STDEEM | `sign-and-trade-qualifying-free-agent-half-salary-for-traded-player-exception` |
| R-STEPIEN | `stepien-rule-no-sell-or-no-consecutive-first-round-draft-pick-trade` |
| R-OSMLE | `offer-sheet-for-1-or-2-year-service-player-no-more-than-mid-level-in-first-2-year` |
| R-OVER38 | `defer-compensation-38-year-old` |
| R-HOLD | `salary-space-consumption-qualifying-veteran-free-agent` |

Constants used throughout: Salary Cap $140,588,000; First Apron $178,132,000;
Second Apron $188,931,000; Non-Taxpayer Mid-Level $12,821,625.60 (9.12% of the
Cap); 2023-24 Salary Cap $136,021,000.

---

## 3. The mechanisms

Eleven distinct mechanisms produce the 18 verdicts. Five live in `derive.py`,
three in the pack, and three are disagreements about what the CBA excerpt says.

### M1 — a declined player option leaves the player under contract (`derive.py`)

Decisive on `comp_0-022`, `comp_0-024`, `comp_0-025`, `comp_0-079`.

`parse_nba.py` emits `players.<P>.player_option_declined: true` when the prose
says so. `derive.py` never reads it. `PlayerView.under_contract` is computed
from the contract span alone —

```
last_covered = prior_first_year + prior_seasons - 1
under_contract = last_covered >= 2024
```

— so a player whose final Salary Cap Year is an option year he has just
declined is still "under contract", `fa_class` stays `None`, and the R5
waterfall's `own_free_agent` test fails. The signing then falls past the Veteran
Free Agent tiers to the Mid-Level branch, where `pre > CAP` and
`pre <= FIRST_APRON` select the Non-Taxpayer Mid-Level. Three consequences fire
together:

* `uses-non-taxpayer-mid-level-exception` becomes true and the first-year
  Salary is tested against 9.12% of the Cap (R-NTMLE);
* `any-transaction-without-exception` becomes true under reading R6, because no
  Mid-Level tier accommodates the amount (R-CAP);
* the contract is placed in the 5%-increase group rather than the 8% group,
  because Art. VII §5(a)(2)'s 8% limb is available only to a Qualifying or
  Early Qualifying Veteran Free Agent re-signing with his Prior Team (R-5PCT).

On the corrected reading `comp_0-022`'s Player A is an Early Qualifying Veteran
Free Agent. §6(b)(3)(i)(A) takes "the Regular Salary for the final Salary Cap
Year covered by his prior Contract" — and once the declined option is honoured,
which is the whole point of this correction, the prior contract's final covered
year is 2023–24 at $16,800,000, so the limb is 175% × $16,800,000 =
$29,400,000, which covers the stated $28,700,000. (An earlier draft of this
note computed the limb from $17,600,000 — the declined option year itself,
which the correction removes; the adversarial check caught it. Both figures
cover $28,700,000, so nothing downstream changes.) `comp_0-024`'s Player A is a
Qualifying Veteran Free Agent and §6(b)(1) reaches the Art. II §7 maximum of
$42,176,400, which covers $30,000,000. Gold's `relevant_rules` name exactly
those two exceptions.

*Verified:* with `player_option_declined` consumed, `judgment-pack 0.2.0`
returns `legal` with an empty fired set on all four.

### M2 — Room is measured against the pre-trade Team Salary (`derive.py`)

Decisive on `comp_0-027`; contributing on `comp_0-032`, `comp_1-071`,
`comp_1-072`, `comp_1-078`, `comp_1-079`.

Reading R7 picks the Traded Player Exception variant with

```
room = CAP - pre            # pre = the team's salary *before* the trade
if room > 0 and incoming <= room + 250_000: variant = "room_tpe"
```

and `tpe_amounts` computes the Room-TPE base the same way. Art. VII §6(j)(1)(v)
speaks of "the Team's room under the Salary Cap" at the assignment, and the
outgoing contracts are assigned away in the same simultaneous trade. Netting
them changes the answer:

| instance | acquiring team | pre | out | in | Room (pre-trade) | Room (net of outgoing) | post-trade |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `comp_0-027` | B | 130,500,000 | 16,800,000 | 27,000,000 | 10,088,000 | 26,888,000 | 140,700,000 |
| `comp_0-032` family | B | 126,000,000 | 31,000,000 | 42,100,000 | 14,588,000 | 45,588,000 | 137,100,000 |

`comp_0-027`'s incoming $27,000,000 is inside $26,888,000 + $250,000, so the
trade is a §6(j)(1)(v) Room acquisition; `derive.py` instead assigned the
Expanded TPE, whose limit here is $24,551,817.73. The `comp_0-032` family is
starker: Team B ends at $137,100,000, **below the Salary Cap**, so it never
needs a Section 6 Exception at all, yet `derive.py` assigned the Aggregated
Standard TPE and the pack found an $11,100,000 excess.

The same pre-trade Room feeds `sign-and-trade-assignee-team-has-room`
(`self.room(dest) >= s.amount`), so on the `comp_0-032` family this one defect
fires two rules.

*Verified:* with Room netted of the team's simultaneously outgoing Salary in
both the variant selection and the Room-TPE base, `comp_0-027` returns `legal`;
on the `comp_0-032` family both R-AGGTPE and R-STROOM stop firing and only
R-STDEEM remains. Netting it in only one of the two places moves `comp_0-027`
from R-EXPTPE to `traded-player-exception-for-room-team` without changing the
verdict, which is why the defect has to be named in both.

### M2b — the Mid-Level Exceptions are never considered for an acquisition (`derive.py`)

Contributing on `comp_0-028`.

R7 chooses among Room, Aggregated, Expanded and Standard TPEs only. Art. VII
§6(e)(1) lets a team use the Non-Taxpayer Mid-Level "to sign **and/or acquire by
assignment**" one or more contracts. In `comp_0-028` the assignee Team B
acquires a $12,400,000 contract while $19,412,000 over the Cap; that is inside
the $12,821,625.60 Mid-Level, and Team B's post-transaction salary of
$167,000,000 is under the First Apron, so the §2(e)(4) row B hard cap is
satisfied. Gold's `relevant_rules` name
`non_taxpayer_mid_level_exception` and
`non_taxpayer_mid_level_exception_hard_cap_first_apron_level`, which is exactly
that analysis. `derive.py` instead labelled the leg an Expanded TPE, whose
limit is $11,050,000.

### M3 — the sign-and-trade deeming rule tests only the Standard limb (pack)

Decisive on `comp_0-032`, `comp_1-071`, `comp_1-072`, `comp_1-078`,
`comp_1-079`.

Art. VII §6(j)(5) deems the signed-and-traded player's Salary, *for purposes of
calculating the assignor's Traded Player Exception*, to be the greater of his
prior last-Season Salary and 50% of the new first-Season Salary. It says
nothing about which Exception the assignor may then use. The pack's R-STDEEM
compares the assignor's incoming Salary to that deemed base plus $250,000 and
nothing else — the §6(j)(1)(i) Standard limb.

On these five instances Team A's deemed base is
`max($29,000,000, 50% × $42,100,000) = $29,000,000` and it takes back
$31,000,000, a $2,000,000 excess. Under §6(j)(1)(iv) the assignor may instead
use the Expanded TPE: 125% × $29,000,000 + $250,000 = $36,500,000, which covers
$31,000,000. Team A's post-transaction salary is $173,000,000, under the First
Apron, so §2(e)(4) row E permits the Expanded TPE; gold's `relevant_rules`
name `expanded_traded_player_exception` and
`expanded_traded_player_exception_hard_cap_first_apron_level`.

*Verified:* with the M2 correction applied and the deemed-base field set to the
Expanded limb, `comp_0-032`, `comp_1-078` and `comp_1-079` return `legal`;
`comp_1-071` and `comp_1-072` need the M10 correction as well and then also
return `legal`.

One of these five carries a caveat about gold itself. `comp_1-079` is the only
record in the whole corpus whose gold has `answer: false` alongside a non-null
`illegal_operation` ("C") and `problematic_team` ("C") — the annotation asserts
a violation its own answer field denies. (Its operation C is a By-Laws §7.03
shape; on our reading Team C still holds Team B's 2026 pick afterwards, so the
`answer` field is probably the sound half and `illegal_operation` stale.) This
does not change why arm B said `illegal` — the Stepien fields are false here
and R-STDEEM's defect is what fired, so class (b) stands — but a row classified
*against gold* should record that gold is internally inconsistent on it. The
adversarial check surfaced this; a class (c) reading was considered and set
aside because the fired rule's ground is defective independently of which half
of the annotation one believes.

### M4 — the Arenas-provision offer sheet is read twice too strictly (pack)

Decisive on `comp_0-054` and `comp_0-073`.

Two separate misreads of Art. XI §5(d):

1. **R-OSMLE bounds two years where the text bounds one.** §5(d)(i) reads "no
   such Offer Sheet may provide for Salary plus Unlikely Bonuses **in the first
   Salary Cap Year** totaling more than the amount of the Non-Taxpayer Mid-Level
   Salary Exception … Annual increases or decreases shall be governed by Article
   VII, Section 5(a)(1)." RuleArena's own statement of the rule says the same
   ("Salary in the first Salary Cap Year"), despite the rule's name. The pack
   compares the **maximum of the first two years** to the mid-level amount.
   `comp_0-054`'s offer sheet is $12,821,625.60 then $13,462,706.88 — exactly
   first year at the mid-level and second year at the 105% that §5(a)(1)
   permits — and the ratio 1.05 fires the rule.

2. **R-5PCT is applied to a step §5(d)(ii) governs.** §5(d)(ii) allows the third
   Salary Cap Year of such an Offer Sheet to go to the player's maximum, with
   the fourth year bounded by 4.5% of the third. `comp_0-054` reads
   $25,000,000 then $26,000,000 (a 4.0% step, inside 4.5%; the maximum for a
   player with 2 Years of Service is 25% of the Cap, $35,147,000);
   `comp_0-073` reads $30,000,000 in the third year of a three-year sheet. Both
   third-year steps are inside §5(d)(ii), and both are counted by
   `max-annual-change-as-fraction-of-first-year-salary-5-percent-group` (0.8998
   and 1.3398) against the generic 5% rule.

The pack contradicts itself here. It carries
`offer-sheet-for-1-or-2-year-service-player-3rd-year-maximum-if-first-2-year-maximum`,
which reads `offer-sheet-first-two-years-at-maximum-allowable` — **true on both
instances** — and correctly does not fire. So one rule treats the first two
years as the lawful maximum while another calls the same two years an excess,
and a third applies §5(a)(1) to a step the first rule's own provision exempts.

*Verified:* with the first-two-year ratio set to the first-year ratio and the
5%-group maximum set to the value that excludes the §5(d)(ii)-governed step,
both return `legal`.

### M5 — `comp_0-029`: the pack's verdict is defensible (gold disputable)

Team A signs Player A at $8,000,000, sends Player A and Player C
($8,000,000 + $4,725,000 = $12,725,000) and receives Player B at $16,200,000,
finishing at $181,475,000. That is above the First Apron ($178,132,000), which
matters twice:

* §2(e)(2)(i)(A) read with row E of the §2(e)(4) table forbids acquiring a
  player under the **Expanded** TPE "if, immediately following such
  transaction, the Team's Team Salary … would exceed" the First Apron, so the
  limb that would cover $16,200,000 ($20,476,817.73) is not available;
* §6(j)(3) reduces the $250,000 allowance to $0, so the Aggregated Standard
  limit is exactly the $12,725,000 sent out (row H hard-caps that Exception at
  the Second Apron, $188,931,000, which is not breached).

Team A therefore takes back $3,475,000 more than any available Exception
permits. §6(j)(5) does not soften this: its condition (z) requires the new
Contract to exceed what a Non-Qualifying Veteran Free Agent could have received
(120% × $17,600,000 = $21,120,000), and $8,000,000 does not, so no deeming
applies — `derive.py` agrees, emitting
`sign-and-trade-qualifying-free-agent-deeming-applies: false`. Both fired TPE
rules read the excerpt correctly on correct inputs. Gold says legal.

For gold to be right, either the apron restriction would have to be tested
against the pre-transaction Team Salary rather than the post-transaction one, or
the §6(j)(3) allowance would have to survive a post-assignment salary above the
First Apron. The excerpt's wording is "immediately following such transaction"
and "post-assignment Team Salary" respectively, so neither reading is available
on the pinned text.

### M6 — `comp_0-026`: the pack's verdict is defensible (gold disputable)

Team A trades Player A ($17,600,000) away for two first-round picks, leaving it
at $157,400,000, then signs Player B to a 3-year contract at $17,800,000 with 8%
annual increases. Two independent violations on the excerpt's text:

* Team A is above the Cap and no Exception reaches $17,800,000 — the
  Non-Taxpayer Mid-Level is $12,821,625.60, the Taxpayer Mid-Level and Room
  Mid-Level are smaller and unavailable at this Team Salary, and a Traded Player
  Exception may only be used "to acquire one (1) or more players by
  assignment" (§6(j)(1)), not to sign a Free Agent.
* Art. VII §5(a)(2)'s 8% limb applies only to "Player Contracts between
  Qualifying Veteran Free Agents or Early Qualifying Veteran Free Agents and
  **their Prior Team**". Player B's Prior Team is Team D. RuleArena's own
  description of the 5% rule repeats the Prior-Team limb verbatim, and gold
  lists that rule among the instance's relevant rules — then answers legal.

### M7 — "Room" in §8(e)(1)(vii) is undefined in the pinned excerpt (ambiguous)

Decisive on `comp_0-028` and `comp_1-069`; contributing on `comp_0-029` and,
until M2 is corrected, on the `comp_0-032` family.

Art. VII §8(e)(1)(vii) conditions a sign-and-trade on "the acquiring Team
[having] Room for the player's Salary plus any Unlikely Bonuses provided for in
the first Season of the Contract". `reference_rules.txt` contains no definition
of "Room". The pack reads it as below-Cap space, which the excerpt's own usage
supports: Art. XI §5(c) lists "Room, a Veteran Free Agent Exception … or the
Minimum Player Salary Exception" as alternatives, and §6(j)(1)(v) says "the
Team's room under the Salary Cap". RuleArena reads it as capacity to absorb the
Salary, including under an Exception. Across the 216 answerable instances:

| assignee "has Room" | instances | gold illegal | gold legal |
| --- | ---: | ---: | ---: |
| false | 91 | 77 | **14** |
| true | 13 | 12 | 1 |

If the pack's reading were RuleArena's, none of those 14 could be gold-legal.
The flag carries essentially no signal about gold either way, which is what a
term the two sides read differently looks like.

`comp_1-069` is the clean case: R-STROOM is the only rule that fires on it.
Team B sheds $44,100,000 to take back $42,000,000, going from $168,000,000 to
$177,900,000 — over the Cap before and after, and so without Room on the pack's
reading, while comfortably able to absorb the contract under the Aggregated
Standard Traded Player Exception its own outgoing Salary creates.

*Verified:* reading the flag as satisfied returns `legal` on `comp_1-069`; on
`comp_0-028` it returns `legal` once the Mid-Level acquisition route of M2b is
recognised alongside it.

**What would disambiguate:** the CBA's Art. I definition of "Room" — whether it
encompasses capacity available under a Section 6 Exception — which is not in the
pinned checkout. No fact about these instances settles it; the missing input is
a definition, and both readings are defensible on the text that is present.

### M8 — the Over-38 rule omits §3(a)(2)(iv) (pack)

Decisive on `comp_0-065`.

Team A ($100,000,000) signs Player A — 16 Years of Service, age 35 in 2024-25, a
Qualifying Veteran Free Agent re-signing with his Prior Team — to a four-Season
contract at $35,000,000 with 7% increases. Re-attributing the fourth year pro
rata puts Team A at 1.0541 of the Cap; without re-attribution it is at 0.9603.
The pack fires on exactly that gap.

Art. VII §3(a)(2)(iv): "Notwithstanding Section 3(a)(2)(i) above, **there shall
be no re-allocation of Salaries** pursuant to this Section 3(a)(2) for any
Contract between a Qualifying Veteran Free Agent and his Prior Team covering
four (4) or fewer Seasons entered into by a player at age 35 or 36." Every limb
is satisfied. The pack encodes only the §3(a)(2)(ii) five-season case
(`over-38-qualifying-veteran-free-agent-age-35-or-36-five-seasons`, correctly
`false` here); §3(a)(2)(iv) appears in neither the rule nor the field contract.
RuleArena's own description of `defer_compensation_38_year_old` opens with the
carve-out — "Except a Qualifying Veteran Free Agent who is age 35 or 36" — and
gold cites it.

*Verified:* suppressing the re-attribution returns `legal`.

### M9 — a matched Offer Sheet is not a signing (`derive.py`)

Decisive on `comp_0-074`.

Reading R8 carries a Free Agent Amount hold for every own free agent "not
signed by anyone in the instance's operations", and `signed_players()` excludes
operations of kind `offer_sheet`. Nothing in `derive.py` handles the
`match_offer_sheet` operation type that `parse_nba.py` emits. In `comp_0-074`
Team B tenders a qualifying offer for Player B, Team A extends an Offer Sheet at
$10,000,000, and **Team B matches** — so Player B is under contract with Team B.
`derive.py` keeps his $10,925,000 hold (190% of a $5,750,000 prior Salary, the
below-average multiple) on Team B's books, which takes Team B from $140,000,000
to $150,925,000: 1.0735 of the Cap with the hold, 0.9958 without. R-HOLD is
written to fire on precisely that pattern — the hold, and only the hold, putting
the team over the Cap.

*Verified:* counting the matched player as signed returns `legal`. The probe
releases the hold without adding the matched Salary; adding it would not
re-fire the rule, whose second limb requires the hold-free ratio to be at most 1.

A second contributing cause sits underneath, which the one-cause-per-row table
does not name: R-HOLD's own premise — that a Free Agent Amount hold which alone
puts a team over the Cap makes the transaction illegal — is not stated by any
provision of the pinned excerpt. Art. VII §4(d) is an attribution rule, and a
ROFR Team matching its own Qualifying Veteran Free Agent has an Exception
(Art. XI §5(c)), so §2(b)(1) does not reach it. `packs/COVERAGE.md` decision 8
records this as a deliberate authored reading rather than a plain bug, which is
why the row is classified (a) on the derivation defect that feeds the rule; but
had `derive.py` been correct, the rule's premise would still have been the next
question. §6's discussion of `comp_0-005` ("releasing the hold leaves it with
no ground at all") is the same point from the other side. The adversarial check
asked for this to be named here rather than left implicit.

### M10 — a pick swap with cash attached is read as a sale (`derive.py`)

Contributing on `comp_1-071` and `comp_1-072`.

```
if any(a["round"] == "1" for a in leg.picks_out) and leg.cash_in > 0 \
        and not leg.incoming_players:
    return True
```

The test ignores `picks_in`. In `comp_1-071` Team A sends its 2025 first-round
and 2027 second-round picks to Team C and receives Team C's 2029 first-round
pick **and** $4,000,000; in `comp_1-072` Team C sends its 2028 first and
receives Team B's 2030 first **and** $3,500,000. By-Laws §7.03 forbids a team
to "sell its first round selection rights for cash or its equivalent"; a
first-for-first swap with cash consideration attached is not that sale, and
gold treats the cash under the separate 5.15%-of-Cap limit
(`pay_or_receive_cash_maximum_in_a_year`), which neither instance breaches.

*Verified:* requiring that no first-round pick come back on the same leg
removes R-STEPIEN from both traces. Neither instance changes verdict — the
other three rules still fire — which is why M10 is contributing rather than
decisive.

---

## 4. Cause-class tally

| class | count | instances |
| --- | ---: | --- |
| **(a)** `derive.py` mischaracterisation | **6** | `comp_0-022`, `comp_0-024`, `comp_0-025`, `comp_0-079` (M1); `comp_0-027` (M2); `comp_0-074` (M9) |
| **(b)** pack encoding error | **8** | `comp_0-032`, `comp_1-071`, `comp_1-072`, `comp_1-078`, `comp_1-079` (M3); `comp_0-054`, `comp_0-073` (M4); `comp_0-065` (M8) |
| **(c)** benchmark gold disputable | **2** | `comp_0-026` (M6); `comp_0-029` (M5) |
| **(d)** pipeline fact error | **0** | — |
| **(e)** genuinely ambiguous | **2** | `comp_0-028`, `comp_1-069` (M7) |

Counting *contributing* causes rather than decisive ones, `derive.py` is
implicated in 12 of the 18 (M1, M2, M2b, M9, M10) and the pack in 8 (M3, M4,
M8). The zero in class (d) is a positive result for `parse_nba.py`: every
contract schedule, team salary, draft year and pick inventory used above was
recomputed by hand from the checkout prose and agreed with the parsed facts.

The 6/8 split between (a) and (b) is a property of the tie-break convention as
much as of the code, and the adversarial check was right to insist this be said
plainly rather than in passing. The table classifies each row by the cause that
*survives every other correction* — fix everything else and ask what still
fires. Under the equally natural opposite convention — the *earliest* defective
step in the pipeline — `comp_0-032` and `comp_1-071/072/078/079` move from (b)
to (a) because M2's Room measurement feeds them first, and the split becomes
(a) 12 / (b) 3. Neither convention is wrong; the row memberships of (c), (d)
and (e) are the same under both; but any sentence quoting "8 pack encoding
errors" inherits the convention, and §6's accuracy arithmetic is the
convention-free statement of what the corrections actually do.

---

## 5. Where §7's guess was right and where it was wrong

G-3 predicted "an over-eager exception assignment (e.g. the Non-Taxpayer
Mid-Level assigned to a team that in fact had Room)". That is precisely M1 —
four instances where the Non-Taxpayer Mid-Level is assigned to a team that in
fact had Bird or Early Bird rights — and M2, where it is assigned to a team
that in fact had Room. So the mechanism was guessed correctly. The weight was
not: those account for 5 of 18, and the pack's own encoding accounts for 8.

A second correction to the record: **PIPELINE-STATUS §7 gives the denominator
as 50** ("18 of the 50 gold-legal answerable instances"). The pinned checkout
has 37 gold-legal instances among the 216 (comp_0: 24, comp_1: 12, comp_2: 1),
and the retained log shows 18 `illegal`, 10 `legal`, 9 `cannot_decide` on them.
`RESULTS-FIRST-PROMPT-ARMS.md`'s "18 of 37" is the correct figure.

---

## 6. What changes in the published claims

**Nothing in the headline result.** H1 on the registered population remains
B − A = −0.148 [−0.213, −0.088]; H4 remains −0.202; H2 and H3 are untouched.
This diagnosis re-attributes causes, it does not rescore anything, and the 18
instances are 8.3% of the answerable population. `RESULTS-FIRST-PROMPT-ARMS.md`
needs one sentence changed — "The cause is unknown" is no longer true — and
`PIPELINE-STATUS.md` §7 needs G-3 closed and its denominator fixed.

**G-2's caveat needs strengthening, and the quantity runs the wrong way.**
§7 G-2 says arm B's score "partly measures `derive.py` rather than the pack".
Four of the five `derive.py` mechanisms found here were patched as diagnostic
probes (M2b, the second Room reading, has none — it is contributing on rows
M3 dominates), all 216 answerable twins re-derived, and `judgment-pack 0.2.0`
re-run on each:

| pipeline | answerable accuracy | correct | gold-legal correct (of 37) | gold-illegal correct (of 179) |
| --- | ---: | ---: | ---: | ---: |
| as run (baseline, reproduces 0.579) | **0.5787** | 125/216 | 10 | 115 |
| + declined player option (M1) | 0.5926 | 128/216 | 14 | 114 |
| + Room net of outgoing Salary (M2) | 0.5787 | 125/216 | 11 | 114 |
| + pick swap is not a sale (M10) | 0.5787 | 125/216 | 10 | 115 |
| + matched Offer Sheet is a signing (M9) | 0.5694 | 123/216 | 11 | 112 |
| **all four together** | **0.5509** | 119/216 | 16 | 103 |

Correcting all four fixes exactly the six class-(a) instances and breaks twelve
gold-illegal ones, for a net loss of 2.8 points. The clearest case is
`comp_0-005`, a near-twin of `comp_0-074`: same three operations, same two
teams, an Offer Sheet of $30,000,000 instead of $10,000,000, gold `illegal`.
Its fired rule and its ratios are identical to `comp_0-074`'s — 1.0735 and
0.9958 — because both come from the same wrongly-retained $10,925,000 hold on
Team B. So the pack agreed with gold on `comp_0-005` through exactly the defect
that made it disagree with gold on `comp_0-074`, and releasing the hold leaves
it with no ground at all. The constraint that would make gold right there looks
like Art. XI §5(b) — the New Team must have Room for the Offer Sheet while it is
outstanding, and Team A is at $100,000,000 carrying a $34,500,000 hold for its
own Qualifying Veteran Free Agent, leaving $6,088,000 against a $30,000,000
sheet — which the pack does not encode at all. That last step is an inference:
gold cites the salary-space rule, not §5(b).

So the accurate statement is not "arm B's score is the pack's score plus a
`derive.py` error term". It is: **arm B's 0.579 is jointly produced, the two
components' errors partly cancel, and neither is recoverable from the other by
subtraction.** Any decomposition of that number is unsupported.

The *observed* comparison between arms stands on even-handed inputs, for two
different reasons. The preprocessor defects M1, M2, M2b, M9 and M10 sit in the
derived block that all three arms received byte-identically. The pack's
encoding defects M3, M4 and M8 do not reach arm A, which reads the CBA
excerpt — but they do reach arm A′, whose prose is a mechanical projection of
this same pack, so they are a shared A′/B property rather than a B-only
handicap. Two things this does **not** establish: that identical wrong inputs
affected a prompted model and an executable pack identically (they need not),
and where a corrected-pipeline B − A or B − A′ contrast would land — only arm
B was re-run under the probes; the model arms were not, so that contrast is
unestimated. What the diagnosis disturbs outright is any reading of arm B's
absolute number as a measurement of the pack.

The probes above are minimal isolations, not repairs. A real repair — one that
computes Room per assignment, models a matched Offer Sheet including the Salary
it puts on the ROFR Team's books, and encodes Art. XI §5(b) — might well not
lose those twelve. That work is not done here and no claim is made about where
a repaired pipeline would land.

**One finding is new rather than a refinement.** `EXPRESSIVENESS-NOTE.md` and
G-1/G-2 frame the pack's limits as things JPS 0.1.0-draft *cannot express*.
Eight of these 18 turn on provisions the pack can express and encodes wrongly:
§6(j)(5) read as if the assignor's only Traded Player Exception were the
Standard one; Art. XI §5(d)(i) read as bounding two Salary Cap Years instead of
one, in direct contradiction to another rule in the same pack; Art. XI
§5(d)(ii)'s override left out of the generic 5% rule; Art. VII §3(a)(2)(iv)
absent entirely. Those are authoring defects, and a single-author pack with no
independent review is exactly where they would be expected. Any claim about
what a judgment pack achieves on this benchmark should carry that alongside the
expressiveness result.
