# Pipeline status — what runs today

Handover state as of 2026-07-27. Blunt on purpose: everything below is either **verified by running
it**, or listed as a gap. No arm has been run against a real model except the two-instance Codex
pilot recorded in §5, which is plumbing validation and is not evidence about anything.

## 1. Substrate — verified

| Check | Result |
| --- | --- |
| `rulearena/fetch.sh` clones at the pinned commit and verifies the SHA | ✅ run |
| Pinned commit | `3b9e2256294644beca66732babc5e1055855a576` |
| Licence | MIT, copied to `rulearena/LICENSE-RuleArena`; fetched, never vendored |

## 2. Parser — verified, 100 % coverage

`python pipeline/parse_nba.py --checkout rulearena/checkout --out pipeline/out/facts --strict`

| Check | Result |
| --- | --- |
| Instances parsed | **216 / 216 (100 %)**, comp_0 = 81, comp_1 = 89, comp_2 = 46 |
| Source sentences consumed | **2 793 / 2 793**, zero unparsed residue |
| JSON numbers anywhere under `facts` | **0** — every value is a JPS-grammar decimal string |
| Instances with a documented ambiguity caveat | 8 / 216, listed in `pipeline/PARSE-COVERAGE.md` §5, parsed under a stated reading rather than silently resolved |
| LLM involved in extraction | **none** — anchored regular expressions only |

This is the property the whole substrate choice rests on, and it holds.

## 3. Pack — verified, with one large caveat

`judgment-pack spec validate packs/nba-transaction-legality.json` → **exit 0**.

| Property | Value |
| --- | --- |
| Outcomes | `legal`, `illegal` |
| Rules | 61 |
| Coverage of the benchmark's `relevant_rules` vocabulary | **61 / 61 (100 %)** |
| `/facts/derived/*` fields required | **124** |
| Authored from | `nba/reference_rules.txt` + the rule-name list only; no instance, gold answer, or answer distribution read |

**The 124 derived fields are the finding, not a footnote.** JPS compares facts and has no arithmetic,
so every computed quantity the CBA needs — post-transaction team salary, apron comparisons, maximum
salary tiers, escalation arithmetic — must be supplied to the pack rather than derived by it. That
number is the honest measure of how much of this decision the format cannot express on its own, and
it belongs in the report whatever the arms show.

## 4. Redaction — verified

`python pipeline/redact.py --facts pipeline/out/facts --out pipeline/out/twins --seed 20260727`

| Check | Result |
| --- | --- |
| Twins emitted | **216 answerable + 216 redacted**, exactly paired |
| Load-bearing fact selection | from the instance's gold `relevant_rules` via `pipeline/loadbearing_map.json`, seeded — not author judgment |
| Leak control | each twin carries a `render_policy` naming pointers a prompt renderer must **not** show (the facts document echoes RuleArena's original prose and carries gold/provenance; rendering those would hand the deleted fact straight back to the prompt arms) |

## 5. Harness — verified on mock and on one real backend

- **Mock, arm A, 3 instances** — ✅ rows well-formed, 0 parse failures.
- **Codex (`gpt-5.6-sol`), arm A, one twin pair** — ✅ 2/2 parsed, 0 errors, and both matched
  expectation: the answerable twin → `illegal` (gold), the redacted twin → `cannot_decide`.
  **n = 2. This is plumbing validation and says nothing about any hypothesis.** It does show the
  baseline arm is not crippled, which is the thing to keep checking.

Every result row records `row_id`, `instance_id`, `variant`, model id and params, `facts_sha256`,
`prompt_sha256`, `policy_sha256`, the harness commit, and whether the tree was dirty.

Two integration bugs were found and fixed while running the above, both of which would have
corrupted the analysis silently:

1. `run.py` loaded the pipeline's sidecar `manifest.json` as if it were an instance.
2. Rows were keyed by `instance_id`, so the **answerable and redacted twins of one instance
   collided** — destroying the paired design and the resume check. Rows now carry `row_id`
   (the twin id) alongside `instance_id` and `variant`.

## 6. Gaps — what is not done

| Gap | Consequence | Owner |
| --- | --- | --- |
| **`pipeline/derive.py` does not exist** | Arm B cannot run on real instances: the pack requires 124 `/facts/derived/*` fields and the parser deliberately emits `derived: {}`. **This is the critical path.** | next session |
| Arm A′ prose not yet rendered from the pack | A′ — the arm that separates "structure helps" from "analysis helps" — cannot run | next session |
| Anthropic backend never executed | no `ANTHROPIC_API_KEY` on this machine; the backend is written and fails loudly rather than falling back to mock | needs a key |
| Eligibility gate not yet computed | the preregistration requires freezing the eligible-instance set **before** any scored run | before runs |
| Pack not yet hashed into `packs/` | the preregistration requires the hash committed before the first run | before runs |
| `score.py` exercised only on fixtures | metrics unverified against real multi-arm output | after derive.py |

## 7. Reproducing everything above

```bash
cd studies/001-policy-representation
rulearena/fetch.sh
python pipeline/parse_nba.py --checkout rulearena/checkout --out pipeline/out/facts --strict
python pipeline/redact.py --facts pipeline/out/facts --out pipeline/out/twins --seed 20260727
judgment-pack spec validate packs/nba-transaction-legality.json
python harness/run.py --arm A --backend mock --instances pipeline/out/twins \
  --trials 1 --seed 1 --limit 3 --out results/smoke-mock-A.jsonl \
  --policy rulearena/checkout/nba/reference_rules.txt
```

`pipeline/out/` is generated and gitignored — every byte is reproducible from the pinned commit plus
the scripts above. The DOI'd corpus release will include the generated artifacts; the repository
does not carry them.
