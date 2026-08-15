# Calibration-pilot harness — NON-CITABLE, DESIGN-TIME TOOLING

**This directory is not the registered study harness.** Everything in it exists to validate
the measurement path before anything is registered, and to drive the labelled calibration
pilots of BRIEF §4.2. Every file carries the same label in its own header.

No number produced here may be cited in the preregistration or in any result document, except
as a pilot rate explicitly labelled non-citable (BRIEF §4.2 step 3: *"the frozen policy's own
pilot rate is registered as not an estimate of anything"*).

## What is deliberately absent

The registered harness is the ported Study 012 machinery (`authoring_call.sh`, `batch.py`,
`integrity.py`, `transcript_check.py`, `arm_assembly.py`, `score_rates.py`), imported by
digest with a two-sided `PORTS.md` table at preregistration time. This driver has none of:

- golden-context capture (two agreeing probes + an isolation negative control under recorded
  operator assent), or any isolation proof at all;
- transcript refusal checks, binary-digest refusal, `PINS.json` linear anchor order;
- the ITT population partition and its prose-vs-code partition test;
- E2's full ordered §8.4 drop-code table, E3, E4 (mutants, identity control, witness sets),
  E5, or any interval arithmetic;
- batch scheduling, arm balance, or the one-UTC-day rule.

It implements exactly one path: **call → extract → admit → evaluate over gold → score**.

## Files

| File | Role |
|---|---|
| `pilot_run.py` | `call` (one sequential codex invocation) and `score` (one arm's runs) |
| `assemble_prompt.py` | builds an arm prompt from the design materials |
| `make_mock_runs.py` | writes MOCK completions so the whole path runs with no model call |

## Self-test of record (2026-08-15, no model was called)

```
python3 make_mock_runs.py --outdir <dir>
python3 pilot_run.py score --arm A --outdir <dir>
python3 pilot_run.py score --arm B --outdir <dir>
python3 pilot_run.py score --arm C --outdir <dir>
```

| Arm | runs | admitted | perfect | drop codes |
|---|---|---|---|---|
| A | 5 | 2 | **1** | no-marker 1, unparseable 1, invalid-artifact 1 |
| B | 4 | 2 | **1** | unparseable 1, invalid-artifact 1 |
| C | 1 | 1 | **1** | — |

The `perfect` run in each arm is the positive control: `reference/refA/pack.json` and
`reference/refB/policy.rego`, copied verbatim into the registered marker/fence form, agree with
**all 76 gold rows** through this scorer. The negative controls are:

- **A-002** no marker at all → `no-marker`;
- **A-003** a truncated JSON document → `unparseable`;
- **A-004** parses but is not a conformant pack → `invalid-artifact`, diagnostic **codes**
  recorded (`JPS-STRUCTURE-REQUIRED-MEMBER`, …), never message prose;
- **A-005** the reference pack with one ordered-comparison operator mutated → admitted, **not
  perfect**, 2 row failures reported with gold ids and (expected, got);
- **B-002** a truncated policy → `unparseable` (all `rego_parse_error`);
- **B-003** the same mutation in Rego → admitted, 2 row failures;
- **B-004** a policy calling a denied built-in → `invalid-artifact` (`rego_type_error`). This
  is the capabilities **canary**: it shows the gate has power, rather than only that the
  reference passes it.

Both engines were driven exactly as the reference build drives them (arm A: facts + evidence
documents with decimal strings, cwd holding no `jpack.json`; arms B/C: the input document
rendered textually so the canonical decimals are exact JSON numbers, `TZ=UTC`, filtered
capabilities, `--fail --strict-builtin-errors --timeout 10s`).

## Not done here, on purpose

**No codex call was made.** The `call` subcommand is written and its argv is fixed —

    codex exec --skip-git-repo-check --sandbox read-only --color never -c 'mcp_servers={}' -

with the prompt on stdin — but running it is a pilot decision for the maintainer, and pilot
calls are counted and labelled in the budget (BRIEF §7).
