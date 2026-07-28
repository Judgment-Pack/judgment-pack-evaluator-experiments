# Issue 1 — data quality: declared counts disagree with prose; four genuinely ambiguous three-team trades

**Title:** NBA instances: declared `n_teams`/`n_players`/`n_operations` disagree with the prose in 32 instances; 4 three-team trades are syntactically ambiguous

**Body:**

Thanks for publishing RuleArena — we've been using the NBA subset (at commit `3b9e225`) as the
corpus for a policy-representation study and built a structured parser over
`nba/annotated_problems/comp_{0,1,2}.json` in the process. Two things surfaced that seem worth
reporting upstream. Both are reproducible from the pinned commit; happy to provide our parser
output if useful.

## 1. Declared counts vs prose (32 instances)

Each annotated problem declares `n_teams`, `n_players`, and `n_operations`, but these disagree with
the accompanying prose in 8, 3, and 21 instances respectively. The prose reads as the substantive
content; the counts look like stale generator metadata. Examples: `comp_0#016` declares
`n_teams: 1` but the prose gives two teams' salary computations; `comp_0#054` declares
`n_players: 2` but describes one player.

Full lists (declared → prose):

- `n_teams` (8): `comp_0#016` (1→2), `comp_0#018` (1→2), `comp_0#019` (1→2), `comp_1#024` (3→2),
  `comp_1#033` (3→2), `comp_1#035` (2→3), `comp_1#042` (2→3), `comp_2#017` (3→2)
  — counted as teams whose salary the instance computes.
- `n_players` (3): `comp_0#007` (2→3), `comp_0#054` (2→1), `comp_1#026` (5→6)
- `n_operations` (21): `comp_0#007` (3→2), `comp_0#038` (3→4), `comp_0#040` (1→3),
  `comp_0#041` (1→3), `comp_0#042` (1→3), `comp_0#043` (1→3), `comp_0#044` (1→3),
  `comp_0#045` (1→3), `comp_0#046` (1→3), `comp_0#047` (1→2), `comp_0#048` (1→2),
  `comp_0#049` (1→2), `comp_0#050` (1→2), `comp_1#007` (3→2), `comp_1#008` (2→3),
  `comp_1#029` (2→3), `comp_1#030` (2→3), `comp_1#041` (1→2), `comp_1#042` (1→2),
  `comp_1#043` (1→3), `comp_2#010` (4→5)

If the counts aren't intended to be load-bearing, a README note saying so would also resolve this
for downstream users.

## 2. Genuinely ambiguous three-team trade sentences (4 instances)

In `comp_1#001`, `comp_1#002`, `comp_1#003`, and `comp_2#000`, the "Simultaneously in this trade"
construction leaves the destination of some assets undetermined by the syntax. Representative
sentence (`comp_1#002`):

> …and subsequently trades Player A to Team B for Player B and Player C and its first-round draft
> picks in 2025 to Team C. Simultaneously in this trade, Team B trades Player D and E and its
> first-round draft picks in 2030 to Team C.

The trailing "to Team C" may attach to only the last conjunct or to the whole "for …" list, and
"its" may denote Team A (the subject) or Team B (the nearest team). Since the gold answers commit
to one reading, it would help evaluators to know which reading is intended — or to have the four
sentences disambiguated in the prose.

Context, for what it's worth: our study treats the counts as quarantined provenance and the four
ambiguous instances as explicitly unresolved rather than silently interpreted, so neither affects
our results; we're reporting because both seem cheap to fix at the source and other users may
resolve them silently in ways that change scores.
