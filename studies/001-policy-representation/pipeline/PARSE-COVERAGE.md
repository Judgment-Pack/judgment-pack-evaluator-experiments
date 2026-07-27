# Parse coverage — RuleArena NBA slice → facts/v1

Produced by `pipeline/parse_nba.py`. Regenerate with:

```
python parse_nba.py --checkout <study>/rulearena/checkout --out <study>/pipeline/out/facts --strict
```

Source: RuleArena (ACL 2025), commit `3b9e2256294644beca66732babc5e1055855a576`,
`nba/annotated_problems/comp_{0,1,2}.json`, treated as read-only.

**No language model, no fuzzy matching, no network is involved in extraction.**
Every value comes out of an anchored regular expression over the benchmark's
templated prose.

---

## 1. Headline numbers

| Quantity | Value |
|---|---|
| Instances | **216** (comp_0 = 81, comp_1 = 89, comp_2 = 46) |
| Facts documents emitted | 216 |
| Instances fully parsed (zero residue) | **216 / 216 = 100.0 %** |
| Source sentences consumed | **2 793 / 2 793 = 100.0 %** |
| — `team_situations` | 735 / 735 |
| — `player_situations` | 1 522 / 1 522 |
| — `operations` | 536 / 536 |
| Unparsed residue entries | **0** |
| Instances carrying a documented ambiguity caveat | **8 / 216 = 3.7 %** (§5) |
| JPS decimal-string violations | 0 |
| JSON numbers anywhere under `facts` | 0 |

`--strict` exits 0 on the pinned commit.

"Fully parsed" means the grammar consumed the sentence end-to-end with no
leftover characters. It does **not** mean the sentence was unambiguous — see §5,
where 8 instances are flagged because the English itself under-determines the
structure. Those 8 are parsed under a stated reading and marked in the output;
they are not silently resolved.

### What is *not* in the output, on purpose

`facts.derived` is emitted as `{}` for every instance. This parser computes
nothing: no salary escalation, no cap/apron comparison, no minimum-scale lookup,
no years-of-service arithmetic, no post-transaction team salary. `derive.py`
(a separate deterministic preprocessor, not written here) owns that key.

---

## 2. Output contract

One file per instance, `out/facts/comp_<n>_<iii>.json`, plus `out/facts/index.json`.

```jsonc
{
  "contract_version": "facts/v1",
  "instance_id": "comp_0#000",
  "facts": { "teams": {…}, "players": {…}, "operations": […], "derived": {} },
  "gold":  { "answer": bool, "illegal_operation": "A"|null,
             "problematic_team": "A"|null, "relevant_rules": [ … ] },
  "provenance": { "source": "rulearena", "commit": "3b9e225…", "file": "comp_0.json",
                  "index": 0, "source_declared_counts": {…}, "raw": {…} }
}
```

`provenance.raw` carries the three verbatim sentence lists, so any consumer can
re-derive or audit a field without re-reading the checkout.

### Fields the parser guarantees

Present whenever — and only whenever — the source sentence states them.

**Teams** (`facts.teams.<A-Z>`)

| Pointer | Type |
|---|---|
| `salary` | decimal string |
| `draft_picks.own_first_round_years_ahead` | decimal string |
| `draft_picks.own_first_round_missing_years[]` | `"YYYY"` strings |
| `draft_picks.acquired_first_round_picks[].{from_team,year}` | strings |
| `players_signed_before_new_season` | decimal string |
| `traded_player_exceptions[].{amount,cap_year}` | decimal string / `"YYYY-YYYY"` |
| `bi_annual_exception_used_cap_year` | `"YYYY-YYYY"` |

**Players** (`facts.players.<A-Z>`)

| Pointer | Type |
|---|---|
| `draft.{round,pick,age_at_draft}` | decimal strings (`round` ∈ `"1"`,`"2"`) |
| `draft.{team,year}` | strings |
| `contract.years` | decimal string |
| `contract.signed_with_team` | `"A"`… |
| `contract.salary_kind` | `explicit` \| `minimum` |
| `contract.first_year_salary` | decimal string (iff `explicit`) |
| `contract.minimum_salary_phrase` | verbatim phrase (iff `minimum`) |
| `contract.annual_change_pct` | **signed** decimal string (`"-5"` for a decrease) |
| `contract.annual_change_direction` | `increase` \| `decrease` |
| `contract.annual_change_applies_to` | `all_years` \| `first_two_salary_cap_years` |
| `contract.signed_during` | `{kind: moratorium_period\|cap_year, year}` |
| `contract.options[].{option_holder,which_years}` | `player`\|`team` / `last_year`\|`last_two_years`\|`second_year` |
| `contract.bi_annual_exception` | bool |
| `awards[].{cap_year,award}` | award ∈ `all_nba_{first,second,third}_team`, `all_nba_defensive_{first,second,third}_team` |
| `player_option_declined`, `tested_free_market` | bool |
| `transactions[].{type,from_team,to_team,counterparty_players[],during}` | strings |

**Operations** (`facts.operations[]`)

| Pointer | Type |
|---|---|
| `label` | `"A"`… (always present) |
| `raw` | verbatim source sentence (always present) |
| `parsed` | bool (always present) |
| `type` | closed set: `sign`, `sign_and_trade`, `multi_sign`, `trade`, `qualifying_offer`, `offer_sheet`, `match_offer_sheet`, `unparsed` |
| `team`, `player` | `"A"`… |
| `contract.*` | same salary-spec vocabulary as player contracts, plus `first_cap_year`, `percent_of_salary_cap`, `minimum_plus_amount`, `year_salary_overrides[].{which_year,salary}`, `stated_total_salary`, `stated_total_years`, `mle_cap_years[]` |
| `trade.{from_team,to_team,sends[],receives[]}` | `to_team` is `null` when the source omits it |
| `trade.{third_team,receives_clause_raw,third_team_asset_binding}` | three-team form only (§5) |
| `additional_legs[]` | same shape as `trade` |
| `timing.{month,day,year,raw}` | `day` decimal string |
| `signings[]` | `multi_sign` only |
| `caveats[]` | sorted slugs, present only when non-empty |
| `residue` | present only when `parsed` is false |

Asset objects in `sends` / `receives`:

```jsonc
{"kind": "player",     "player": "A", "current_team": "C"?}
{"kind": "draft_pick", "round": "1"|"2", "year": "2026"|null, "owner": "self"|"A"}
{"kind": "cash",       "amount": "5000000"}
```

### JPS decimal-string discipline

Every value any rule might ORDER-COMPARE is a JSON **string** matching
`-?(0|[1-9][0-9]*)(\.[0-9]+)?`. Thousands separators and `$` are stripped;
percentages lose the `%` and a decrease becomes a negative (`7% decrease per
year` → `annual_change_pct: "-7"`). `21th` → `"21"`. Booleans stay booleans.
There is **no** JSON number anywhere under `facts` — the test suite asserts this
over all 216 documents. `which_year` (`"2"`,`"3"`,`"4"`,`"last"`) is an *enum*,
not a comparable quantity, and is deliberately excluded from the decimal check.

Every key is a plain identifier or a single capital letter, so no RFC 6901
escaping (`~0`/`~1`) is ever required; arrays are index-addressed. The test suite
resolves every pointer in every document.

---

## 3. Template variants handled

Counts are sentences matched over the whole corpus. `CAPY` abbreviates
`[0-9]{4}-[0-9]{2,4}`; `MONEY` abbreviates `[0-9]+(?:,[0-9]{3})*`.

### 3.1 `team_situations` — 735 / 735

| # | Variant | Hits | Regex |
|---|---|---|---|
| T1 | team salary | 551 | `\ATeam ([A-Z]) has a team salary of \$(MONEY)\Z` |
| T2 | first-round pick inventory (with optional `except …` and optional `and Team X's pick(s) in …`) | 172 | `\ATeam ([A-Z]) has all its first-round draft picks in the following ([0-9]+) years(?: except ((?:[0-9]{4})(?: and [0-9]{4})*))?(?: and Team ([A-Z])'s first-round draft picks? in ((?:[0-9]{4})(?: and [0-9]{4})*))?\Z` |
| T3 | multi-team pick inventory | 4 | `\A((?:Team [A-Z], )+(?:and )?Team [A-Z]) have all their first-round draft picks in the following ([0-9]+) years\Z` |
| T4 | roster size before the new season | 6 | `\ATeam ([A-Z]) signs ([0-9]+) players before the new season\Z` |
| T5 | traded-player exception held | 1 | `\ATeam ([A-Z]) got a \$(MONEY) Traded Player Exception during (CAPY) Salary Cap Year\Z` |
| T6 | bi-annual exception already used | 1 | `\ATeam ([A-Z]) used its bi-annual exception to sign a player in the (CAPY) Salary Cap Year\Z` |

T2 subsumes the six surface forms observed (`…7 years.`, `…except 2027.`,
`…except 2026 and 2028;`, `…and Team B's first-round draft pick in 2026.`,
`…and Team B's first-round draft picks in 2026 and 2028;`,
`…except 2025 and Team C's first-round draft pick in 2027.`).

### 3.2 `player_situations` — 1 522 / 1 522

| # | Variant | Hits | Regex |
|---|---|---|---|
| P1 | draft position | 710 | `\APlayer ([A-Z]) was the ([0-9]+(?:st\|nd\|rd\|th)) (first\|second)-round pick of Team ([A-Z]) in ([0-9]{4}) NBA draft when he was ([0-9]+) years old` |
| P2 | contract, spec in parens before team | 644 | `signed a ([0-9]+)-year contract \(([^)]*)\) with Team ([A-Z])(?: during ([0-9]{4}) Moratorium Period\| in ([0-9]{4}) Cap Year)?\Z` |
| P3 | contract, spec in parens after team | 32 | `signed a ([0-9]+)-year contract with Team ([A-Z]) \(([^)]*)\)(?: during …)?\Z` |
| P4 | contract, `providing` form | 34 | `signed a ([0-9]+)-year contract with Team ([A-Z]) providing (.*?)(?: during …)?\Z` |
| P5 | P1 + P3 in one sentence (`… years old and signed a …`) | 10 | P1 then P3 on the tail |
| P6 | P1 + P4 in one sentence | 7 | P1 then P4 on the tail |
| P7 | All-NBA award | 58 | `\AIn (CAPY) Salary Cap Year Player ([A-Z]) was named to (?:the )?All-NBA (Defending )?(First\|Second\|Third\|first\|second\|third) [Tt]eam\Z` |
| P8 | player option declined (± tested free market) | 13 | `\APlayer ([A-Z]) just decided not to exercise (?:the\|his) player option( and tested free market)?\Z` |
| P9 | traded to a team | 12 | `\APlayer ([A-Z]) was traded to Team ([A-Z]) during (?:the )?(CAPY) Regular Season\Z` |
| P10 | traded by X to Y for Z | 1 | `\APlayer ([A-Z]) was traded by Team ([A-Z]) to Team ([A-Z]) for Player ([A-Z]) during (?:the )?(?:(CAPY) Regular Season\|([0-9]{4}) Moratorium Period)\Z` |
| P11 | traded *with* another player | 1 | `\APlayer ([A-Z]) was traded with Player ([A-Z]) by Team ([A-Z]) to Team ([A-Z]) for Player ([A-Z]) during (?:the )?(CAPY) Regular Season\Z` |

P10 and P11 write the mirror-image transaction onto the counterparty players too.

### 3.3 Salary specifications (shared sub-grammar)

The parenthetical / `providing` body is not matched by one regex per sentence.
It is scanned as a separator-joined list (`SALARY_SEP = ,? and |, |,? with `),
longest-match-wins at each cursor position, and **whatever the scanner cannot
consume becomes residue**. This is what makes the 154 distinct surface forms of
`operations` collapse to a handful of productions.

| Production | Hits | Regex |
|---|---|---|
| `S_EXPLICIT` | 979 | `(?:an )?(?:annual )?salary (?:of )?\$(MONEY)(?: in the first (?:Salary )?Cap Year(?: \((CAPY)\))?)?` |
| `S_EXPLICIT_BARE` | 1 | `\$(MONEY)(?: in the first (?:Salary )?Cap Year(?: \((CAPY)\))?)?` |
| `S_ESCALATOR` | 1 040 | `([0-9]+(?:\.[0-9]+)?)% (increase\|decrease) per year( for the first two Salary Cap Years)?` |
| `S_MINIMUM` | 126 | `(?:a \|the )?minimum(?: applicable)?(?: player\| annual)? salary(?: in the first (?:Salary )?Cap Year(?: \((CAPY)\))?)?(?: plus \$(MONEY))?` |
| `S_OPTION` | 52 | `(?:with )?(?:the )?(last\|second\|first\|third)(?: (two\|three))? years? (?:is\|are\|being) (?:a )?(player\|team) options?` |
| `S_YEAR_OVERRIDE` | 20 | `(?:salary )?\$(MONEY) (?:for\|in) the (second\|third\|fourth\|last) (?:Salary Cap Year\|Salary year\|Salary Year\|Year)` |
| `S_PCT_OF_CAP` | 5 | `(?:annual )?salary equal to ([0-9]+(?:\.[0-9]+)?)% (?:of the\|×\|x) Salary Cap(?: in the first( two)? Salary Cap Years?(?: \((CAPY)\))?)?` |
| `S_BIANNUAL` | 4 | `(?:with )?bi-annual exception` |
| `S_MLE` | 2 | `(?:annual )?salary equal to the non-taxpayer mid-level exception(?: in the first two Salary Cap Years \((CAPY), (CAPY)\))?` |
| `S_TOTAL` | 1 | `totally \$(MONEY) for ([a-z]+) years` |

### 3.4 Asset lists in trades (shared sub-grammar)

Same scanner discipline; `ASSET_SEP = , and |,? and |, | with `.

| Production | Hits | Regex |
|---|---|---|
| `A_PLAYER` | 381 | `(?:[Pp]layer )?([A-Z])(?: in [Tt]eam ([A-Z]))?(?![a-z'])` |
| `A_OWN_PICKS` | 176 | `its (first\|second)-round draft picks? in ((?:[0-9]{4})(?: and [0-9]{4})*)` |
| `A_CASH` | 47 | `\$(MONEY)` |
| `A_BARE_PICKS` | 13 | `(first\|second)-round draft picks? in ((?:[0-9]{4})(?: and [0-9]{4})*)` |
| `A_TEAM_PICKS` | 4 | `Team ([A-Z])'s (first\|second)-round draft picks? in ((?:[0-9]{4})(?: and [0-9]{4})*)` |
| `A_OWN_PICK_NOYEAR` | 1 | `its (first\|second)-round draft pick(?! in)` |

`A_PLAYER` deliberately accepts a bare capital letter so that the elliptical
`trades Player A with Player C and D` yields three players, not two. The
negative lookahead `(?![a-z'])` stops it from biting into `Team B's` or a
sentence-initial word. Every player letter produced this way is cross-checked in
the test suite against `facts.players`; there are zero ghosts.

### 3.5 `operations` — 536 / 536

Top-level forms, in match order:

| # | Type | Hits | Regex |
|---|---|---|---|
| O1 | `qualifying_offer` | 37 | `\A[Tt]eam ([A-Z]) provides a qualifying offer for [Pp]layer ([A-Z])\Z` |
| O2 | `match_offer_sheet` | 20 | `\A[Tt]eam ([A-Z]) matches the offer(?: sheet)?(?: (?:from\|by) [Tt]eam ([A-Z])\| for [Pp]layer ([A-Z]))?\Z` |
| O3 | `offer_sheet`, dash form | (of 37) | `\A[Tt]eam ([A-Z]) provides [Pp]layer ([A-Z]) with an offer sheet - a ([0-9]+)-year contract providing (.+)\Z` |
| O4 | `offer_sheet`, `for … in a N-year contract` form | (of 37) | `\A[Tt]eam ([A-Z]) provides an offer sheet for [Pp]layer ([A-Z])(?: in a ([0-9]+)-year contract)? providing (.+)\Z` |
| O5 | `sign_and_trade` | 104 | split on `\A(.*?),? and ((?:immediately \|subsequently )trades .*)\Z`, then O7/O8 + O10 |
| O6 | `multi_sign` | 3 | split on `\A(.*?) and (signs (?:a [0-9]+-year contract with\|with) .*)\Z`, then O7 twice |
| O7 | `sign`, `providing` form | (of 239) | `\A[Tt]eam ([A-Z]) signs a ([0-9]+)-year contract with [Pp]layer ([A-Z]) providing (.+)\Z` |
| O8 | `sign`, parenthetical form | (of 239) | `\A[Tt]eam ([A-Z]) signs a ([0-9]+)-year contract with [Pp]layer ([A-Z]) \((.+)\)\Z` |
| O9 | `sign`, `signs with … with a N-year contract` form | (of 239) | `\A[Tt]eam ([A-Z]) signs with [Pp]layer ([A-Z]) with a ([0-9]+)-year contract providing (.+)\Z` |
| O10 | `trade`, two-sided | (of 96) | `\A(?:immediately \|subsequently )?trades (.+?)(?: to [Tt]eam ([A-Z]))? for (.+)\Z` |
| O11 | `trade`, one-directional leg | (of 96) | `\A(?:immediately \|subsequently )?trades (.+?) to [Tt]eam ([A-Z])\Z` |

Suffix productions stripped before the above:

| Suffix | Regex |
|---|---|
| execution date tacked onto a signing | `, execute the transaction (in .+)\Z` |
| transaction date | `(?: (?:in\|on) (?:the )?(<month>)(?: of)?(?: ([0-9]{1,2}(?:st\|nd\|rd\|th))?,?)?(?: ([0-9]{4}))?)\Z` |
| three-team continuation | split on `\. Simultaneously in this trade, ` |

Resulting distribution: `sign` 239, `sign_and_trade` 104, `trade` 96,
`qualifying_offer` 37, `offer_sheet` 37, `match_offer_sheet` 20, `multi_sign` 3.

---

## 4. Typo normalisation table

The corpus is template-generated but hand-edited, and carries a handful of
misspellings. Each is corrected by a tightly-anchored regex before parsing.
**No entry changes a value; all change spelling, a doubled noun, or two dropped
words.** The test suite asserts that every rule fires at least once and that no
rule matches more than 10 sentences, so the table cannot quietly grow into a
general rewriter.

| Regex | Replacement | Sentences touched | Example |
|---|---|---|---|
| `\bcontrct\b` | `contract` | 3 | `signs a 3-year contrct with Player C` |
| `\bproving annual salary\b` | `providing annual salary` | 3 | `proving annual salary $25,000,000` |
| `\btraeds\b` | `trades` | 2 | `Team B traeds its first-round draft pick in 2029` |
| `\bsignes with\b` | `signs with` | 2 | `Team B signes with Player B` |
| `\bminimal annual salary\b` | `minimum annual salary` | 1 | `providing minimal annual salary` |
| `execute the transaction in in ` | `execute the transaction in ` | 1 | doubled preposition |
| `\A(Player [A-Z]) and signed a ` | `\1 signed a ` | 2 | `Player A and signed a 3-year contract …` |
| `signs a contract ([0-9]+-year contract)` | `signs a \1` | 3 | `signs a contract 2-year contract with Player B` |
| `in the first Salary year \(` | `in the first Salary Cap Year (` | 6 | dropped `Cap` |
| `for its (first\|second)-round ([0-9]{4})` | `for its \1-round draft pick in \2` | 1 | `for its first-round 2028` |

The seventh rule is anchored at `\A` precisely so it cannot touch the 17
**legitimate** occurrences of `… years old and signed a …` (variants P5/P6).

---

## 5. Documented ambiguities — read this before using the output

These are cases where the *English is under-determined*, not cases where the
parser is weak. Each is fully consumed, flagged with a machine-readable slug in
`facts.operations[].caveats` and in `index.json → instances[].caveats`, and
listed here in full. **Nothing here was guessed silently.**

### Ambiguity #1 — three-team "Simultaneously in this trade" (4 instances)

Slugs: `three_team_simultaneous_trade`, `three_team_trade_destination_binding`.
Instances: `comp_1#001`, `comp_1#002`, `comp_1#003`, `comp_2#000`.

Representative sentence (`comp_1#002`):

> A. Team A signs a 4-year contract with Player A providing annual salary
> $35,100,000 in the first Salary Cap Year (2024-2025) and 5% increase per year,
> **and subsequently trades Player A to Team B for Player B and Player C and its
> first-round draft picks in 2025 to Team C. Simultaneously in this trade, Team B
> trades Player D and E and its first-round draft picks in 2030 to Team C.**

The trailing `to Team C` may attach to (a) only the last conjunct
(`its first-round draft picks in 2025`), or (b) the whole `for …` list. And
`its` in the `for` clause may denote Team A (the subject) or Team B (the nearest
team). The surface syntax does not decide it, and no amount of regex will.

**What the parser does, and does not do.** It puts the *entire* `for …` list in
`trade.receives` — a purely syntactic reading with no interpretation — and adds:

```jsonc
"trade": {
  "third_team": "C",
  "third_team_asset_binding": "unresolved",
  "receives_clause_raw": "Player B and Player C and its first-round draft picks in 2025 to Team C"
}
```

plus `additional_legs[]` for the `Simultaneously …` sentence. A consumer that
needs the true asset routing must decide from `receives_clause_raw`; the parser
refuses to. **Note that `receives` for these four operations is therefore known
to over-collect**: at least the `owner: "self"` draft picks in it are almost
certainly outbound, not inbound.

### Ambiguity #2 — trade with no destination team stated (4 instances)

Slug: `trade_destination_team_not_stated`. Instances and verbatim text:

| Instance | Sentence |
|---|---|
| `comp_0#006` | `A. Team A trades Player A for Player B.` |
| `comp_0#007` | `B. Team A immediately trades Player A and Player C for Player B.` |
| `comp_0#021` | `A. Team A trades player A for Player B.` |
| `comp_1#082` | `B. Team A trades its first-round draft picks in 2028 for Player D in team C.` |

The counterparty is inferable from context (in `comp_1#082`, Player D's
`current_team` is C) but is never *stated*. `trade.to_team` is set to `null`.
It is not back-filled.

### Not an ambiguity, but a corpus defect you must know about

`n_teams`, `n_players` and `n_operations` in the source records **disagree with
the prose** in 8, 3 and 21 of the 216 instances respectively. Examples:
`comp_0#016` declares `n_teams: 1` but lists two team-salary sentences;
`comp_0#054` declares `n_players: 2` but describes one player. The parser trusts
the prose and copies the declared counts verbatim to
`provenance.source_declared_counts` for traceability. **Do not use those counts
to validate anything.**

### Things the parser records rather than resolves

* `minimum applicable player salary`, `the minimum salary`, `minimum salary`,
  `minimum annual salary` all map to `salary_kind: "minimum"`, but the literal
  phrase is preserved in `contract.minimum_salary_phrase` (8 distinct phrasings
  observed). Whether these denote the same CBA quantity is a policy question,
  not a parsing question, and is left to the downstream arms.
* `trade.to_team` is `null` where unstated; asset `year` is `null` for the one
  `its first-round draft pick` with no year.
* Three `offer_sheet` operations (`comp_1#083`, `comp_1#084`, `comp_1#085`) never
  state a contract length, so `contract.years` is absent. `comp_1#085` states
  `totally $40,000,000 for four years`, captured as `stated_total_years: "4"`,
  which is *not* promoted to `years`.
* Teams that appear only as a draft-origin or trade counterparty get an empty
  `facts.teams.<X>` slot so every referenced letter is pointer-addressable; 424
  such slots carry no `salary` because the source never gives one.

---

## 6. Residues

**None.** Zero sentences, and zero sentence fragments, failed to parse across all
216 instances.

Had there been any, each would appear in `out/facts/index.json` under
`.residues` as:

```jsonc
{"instance_id": "comp_1#042", "section": "operations",
 "text": "<verbatim source sentence>", "unconsumed": "<the fragment the grammar could not eat>"}
```

and the owning instance would carry `parsed_fully: false` in
`index.json → instances[]`. The scanner design makes silent loss structurally
impossible: `scan_list` returns its unconsumed tail, and every caller propagates
that tail into a residue record rather than discarding it.

---

## 7. Tests

`pipeline/tests/test_parse_nba.py` — 26 tests, stdlib + pytest only:

* corpus is exactly 216 (81 / 89 / 46) and every instance yields the contract shape;
* hand-checked round trips (sign-and-trade with elliptical player list, per-year
  salary schedule with stated total, percent-of-cap offer sheet, draft-pick
  inventory, negative escalator);
* every numeric field is a JPS decimal string; no JSON number anywhere under
  `facts`; the parser's own validator agrees;
* every node in every document resolves through a from-scratch RFC 6901
  resolver (>25 000 pointers), and no key needs escaping;
* determinism — two independent parses serialise byte-identically;
* residue list is empty and no operation is `unparsed`;
* operation types are a closed set; every player/team letter referenced by an
  operation has a slot;
* the typo table is narrow (every rule fires, none exceeds 10 hits) and
  `normalise` is idempotent.

```
$ python -m pytest tests/test_parse_nba.py -q
26 passed
```
