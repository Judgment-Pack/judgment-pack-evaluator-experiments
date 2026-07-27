# Upstream notes

Discrepancies found in RuleArena during this study, what we reported upstream, and how the study
treats each one. Empty means none found yet.

Policy: corrections go upstream first (issue or PR on `skyriver-2000/RuleArena`); only what cannot
be resolved upstream is worked around locally, and every workaround is listed here with the exact
instance ids it touches.

| Date | Instance ids | Observation | Reported upstream | How this study treats it |
| --- | --- | --- | --- | --- |
| 2026-07-27 | 21 of 216 (`n_operations`), 8 (`n_teams`), 3 (`n_players`) | Each annotated problem declares `n_teams`, `n_players`, and `n_operations`, but these disagree with the accompanying prose in 21 / 8 / 3 instances respectively. The prose is the substantive content; the counts appear to be stale generator metadata. | **To file** — issue on `skyriver-2000/RuleArena` with the instance list | The parser trusts the prose and quarantines the declared counts under `provenance.source_declared_counts`; nothing in the study validates against them. See `pipeline/PARSE-COVERAGE.md`. |
| 2026-07-27 | 4 (`comp_1#001`, `comp_1#002`, `comp_1#003`, `comp_2#000`) | Three-team "Simultaneously in this trade" sentences: the attachment of `to Team C` is not determined by the syntax, so the destination of some assets is genuinely ambiguous in the English. | **To file** — same issue | Parsed purely syntactically with `third_team_asset_binding: "unresolved"` and the raw clause preserved; flagged in `PARSE-COVERAGE.md` §5 rather than silently resolved. |
| 2026-07-27 | 77 of 216 contain a "minimum applicable player salary" contract | The Minimum Player Salary / Minimum Annual Salary schedule is referenced by instances but appears in neither `nba/reference_rules.txt` nor the stipulation preamble in `nba/auto_test.py`. A solver that refuses to invent the figure cannot compute those teams' salaries. | **To file** — question on `skyriver-2000/RuleArena`: is the schedule intended to be supplied, or are minimum contracts intended to be treated as immaterial? | Reported as a finding, not worked around: the preprocessor omits the field, the pack escalates. See `EXPRESSIVENESS-NOTE.md` finding 3. |
