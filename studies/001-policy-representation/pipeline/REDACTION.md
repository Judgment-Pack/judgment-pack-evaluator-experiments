# Redaction: how the "cannot decide" condition was manufactured

**These abstention labels are constructed by this study. They are not RuleArena's.** Every
one of RuleArena's 216 NBA instances is decidable from the facts it ships; the benchmark has
no abstention condition and makes no claim about when a system should refuse to answer. To
measure escalation we built one ourselves, by deleting exactly one load-bearing fact from a
copy of each instance and labelling that copy `cannot_decide`. Everything below exists so
that a reader can check that construction rather than take it on trust: which fact was
deleted, why that choice was not the author's judgment, what could still go wrong with it,
and how to reproduce the artefact byte for byte.

The precedent is the standard one for manufactured unanswerability: SQuAD 2.0's contrast
sets, AbstentionBench's unanswerable variants, and HiL-Bench's removal of human-validated
blockers. Like those, our labels are only as good as the deletion procedure, so the
procedure is mechanical, seeded, and published.

## The pair

For each parsed facts document the operator emits two twins:

| variant | facts | expected decision |
| --- | --- | --- |
| `answerable` | unchanged | the gold answer (`legal` / `illegal`) |
| `redacted` | exactly one fact pointer deleted | `cannot_decide` |

One of each, always, per instance. Pairs are emitted or skipped as a unit; a lone twin is
never written. That balance is the whole defence of the escalation metric: an agent that
always escalates scores 50%, an agent that never escalates scores 50%, and only an agent
that notices *which* fact is missing can do better. The answerable twin also carries the
unmodified instance, so accuracy and citation metrics run on exactly the material the
benchmark shipped.

## Choosing the fact — why this is not the author's judgment

Three artefacts do the choosing, none of them written by us and none of them consulted for
the answer:

1. **The instance's gold `relevant_rules`.** RuleArena annotates every problem with the
   provisions that govern it. That list is third-party ground truth about which parts of the
   CBA are in play.
2. **`pipeline/loadbearing_map.json`.** For each rule id, the fact *roles* that rule must
   read in order to be evaluated at all. Every entry quotes the rule's text **verbatim** from
   RuleArena's own `nba/micro_evaluation.py` (the `RuleExtraction` field descriptions), with
   a pointer to the governing heading in `nba/reference_rules.txt`. The required-fact lists
   were read off that text and the CBA sections it cites. Nine rule ids that appear in the
   gold annotations but not in `micro_evaluation.py` are annotator spelling or threshold
   variants; each is recorded with an explicit `alias_of` naming the canonical field it
   inherits its text and roles from. The map covers all 61 rule ids RuleArena actually cites.
3. **The facts document itself,** which decides which of those roles are present and where.

The candidate set for an instance is the union, over the rules that instance cites, of the
required-fact pointers that actually resolve in that document. Among the candidates that
clear the guards below, the choice is **uniform under a seeded RNG** — there is no
preference for the "most load-bearing" fact, because ranking candidates would be exactly the
judgment call we are trying to avoid, and because a uniform draw spreads the redaction
across many kinds of fact instead of always hiding the same field, which a system could
learn to pattern-match without reasoning about the policy at all.

The RNG is keyed on `sha256(seed | instance_id)`, not on position in the corpus, so an
instance's chosen fact is the same whether you process all 216 or just that one, in any
order. (Tested.)

## Guards

A twin that had to relax any guard is still emitted, but marked `weak`, given
`in_primary_analysis: false`, and excluded from the primary analysis.

- **G1 — presence.** The pointer must resolve in the answerable document. We never "delete"
  a fact that was absent anyway, which would produce two identical twins.
- **G2 — participation.** The fact must belong to a team or player that actually takes part
  in an operation. A bench player's contract term matches a cited rule's shape but decides
  nothing here.
- **G3 — locality.** When gold says the answer is `illegal`, the deleted fact must be scoped
  to the gold `problematic_team`, to the gold `illegal_operation`, or to a player
  participating in that operation. Deleting a fact somewhere else plainly leaves the cited
  violation decidable.
- **G4 — non-survival.** The fact must not survive elsewhere: not resolved twice under
  different names in the same scope; not implied by a sibling key the map declares as
  carrying the same information (`salary_kind: "explicit"` tells you nothing while
  `first_year_salary` sits next to it); not superseded by a `facts.derived` leaf scoped to
  the same entity whose name carries one of the role's supersession tokens; and not spelled
  out verbatim inside any renderable prose string.

`facts.derived` is never itself a deletion candidate. Derived quantities are recomputable
from the surviving raw facts by any arm that can do arithmetic, so deleting one would not
make an instance undecidable — it would only test arithmetic, which this study explicitly
does not measure.

## Two strengths of claim

Strong twins carry a `strength_basis` so that a sceptical reading can narrow the set:

- **`universal`** (gold answer `legal`). The argument is airtight. A verdict of "no
  operation violates the rules" requires *every* cited rule to be checkable, so removing any
  one fact that any cited rule must read blocks the verdict. No policy reasoning is needed to
  see this.
- **`localized`** (gold answer `illegal`, guard G3 satisfied). The deleted fact is where gold
  says the violation is, and the rule that needed it can no longer be evaluated. **Residual
  assumption:** we cannot mechanically prove that no *other* cited rule independently
  establishes the same operation's illegality without the deleted fact. Proving that would
  require re-implementing the CBA, which is the very thing the study is testing, so we do not
  claim it. Report the primary result on all strong twins and the sensitivity result on the
  `universal` subset alone; if the two diverge, the divergence is the finding.

## Counts (seed 20260727)

Run against `pipeline/out/facts` as of this writing:

| | |
| --- | --- |
| facts documents read | 216 |
| pairs emitted | **216** (432 twins: 216 answerable, 216 redacted) |
| strong pairs, in primary analysis | **216** |
| — of which `universal` (gold = legal) | 37 |
| — of which `localized` (gold = illegal) | 179 |
| weak pairs, emitted but excluded | **0** |
| instances skipped | **0** |
| distinct fact roles deleted across the corpus | 23 |

Nothing was skipped: every instance cites at least one mapped rule whose required facts
resolve. Nothing came out weak: with `facts.derived` currently empty (see the caveat below)
and the render policy in force, no chosen fact survived elsewhere in its document.

The 179/37 `localized`/`universal` split is exactly RuleArena's own 179 illegal / 37 legal
gold distribution — the redaction procedure does not resample or reweight instances, so the
answerable half of the corpus has the class balance the benchmark shipped, and the
`universal` sensitivity subset is small by construction.

Most-deleted fact roles (full histogram in `out/twins/manifest.json`):

```
 24  player.prior_team                          10  operation.team
 23  player.draft_year                           6  player.age_at_draft
 22  player.contract.length_seasons              5  operation.counterparty_team
 19  player.contract.salary                      5  operation.draft_picks_traded
 17  player.contract.signed_year                 5  player.contract.increase_rate
 16  operation.new_contract.salary               5  team.first_round_picks_missing
 12  team.salary                                 4  operation.players_in
 11  operation.new_contract.change_direction     4  team.first_round_picks_owned
 10  operation.new_contract.increase_rate        3  team.first_round_picks_acquired
 10  operation.new_contract.length_seasons       ... 5 more roles with 1-2 each
```

### Two concrete before/after examples

**`comp_0#009`** — gold answer `legal`, so `strength_basis: universal`.

```
before : /facts/operations/1/contract/years = "4"
after  : /facts/operations/1/contract/years  absent
role   : operation.new_contract.length_seasons
needed by 5 cited rules, among them
    contract_length_at_most_4_year_except_qualifying_veteran_free_agent_5_year
    defer_compensation_qualifying_veteran_free_agent_38_year_old
    salary_increase_and_decrease_ratio_for_qualiyfing_or_early_qualifying_veteran_free_agent
```

Without the number of Seasons the contract covers, none of those five can be checked, so the
"no operation violates the rules" verdict cannot be reached. Correct behaviour: escalate.

**`comp_0#000`** — gold answer `illegal`, operation A, team A; `strength_basis: localized`.

```
before : /facts/operations/0/contract/years = "3"
after  : /facts/operations/0/contract/years  absent
role   : operation.new_contract.length_seasons
needed by
    sign_and_trade_3_to_4_year
    salary_increase_and_decrease_ratio_for_qualiyfing_or_early_qualifying_veteran_free_agent
```

The deleted fact is inside the very operation gold names as illegal. The sign-and-trade
length rule cannot be applied without it.

## Two things the harness must honour

1. **The render policy is not optional.** The facts documents echo RuleArena's original
   English in `facts.operations[].raw`, `facts.operations[].timing.raw`,
   `facts.operations[].trade.receives_clause_raw` and `facts.operations[].caveats[]`, and
   they carry `gold` and `provenance`. Rendering any of those into a prompt hands a redacted
   twin its deleted fact back in plain English and leaks the answer outright. The excluded
   pointers are declared in `loadbearing_map.json` under `render_policy` and copied into
   every twin as a top-level `render_policy` member, identical across both variants and all
   three arms. The operator reports how many pairs would be compromised: currently **62**
   pairs echo their deleted value in prose inside the excluded zone (and that undercounts,
   since the audit ignores values shorter than three characters). A renderer that shows those
   fields invalidates the redacted half of the corpus.
2. **Re-run after the preprocessor lands.** `facts.derived` is empty in all 216 documents at
   the time of writing, so guard G4's derived-supersession check had nothing to fire against
   and the operator prints a warning saying so. Once the deterministic preprocessor publishes
   derived quantities, re-run: twins whose deleted fact turns out to be recoverable from a
   published derived value will be reclassified `weak` and drop out of the primary analysis,
   and the counts in this document must be regenerated with them.

## Known limits

- The `localized` residual assumption, above. It is the largest one.
- `player.years_of_service` never resolves in the current facts documents; the service-tier
  rules therefore fall back to `player.draft_year`, its raw input. If the preprocessor later
  publishes years of service under `facts.derived`, deleting the draft year stops being
  load-bearing and G4 will catch it — another reason to re-run.
- The prose-leak audit ignores deleted values shorter than three characters (single-letter
  team labels, single-digit contract lengths), because substring matching on them is noise.
  Structural recovery of such values is covered by the sibling-key declarations instead, but
  cross-object inferences (deducing a player's team from which side of a trade he appears on)
  are not detected.
- The map's pointer templates are matched against whatever the parser emits. A role that
  resolves to nothing simply contributes no candidates rather than failing loudly; the
  manifest lists `roles_that_never_resolved_anywhere` so this stays visible.

## Reproduction

```
cd studies/001-policy-representation
python pipeline/redact.py \
    --facts pipeline/out/facts \
    --out   pipeline/out/twins \
    --seed  20260727
```

Same inputs and seed produce byte-identical output. `pipeline/out/twins/manifest.json`
records the seed, the SHA-256 of `loadbearing_map.json`
(`674fb09e8eb61b04…`), the per-pair selection trace including the RNG key, the render
policy, and every skip and weakness with its reason.

Tests: `python -m unittest discover -s pipeline/tests` (27 tests, no network, no dependency
on `pipeline/out`).
