# Clean-room brief — Study 002: encoding a qualitative policy as a judgment pack

You are running the **replication half** of an experiment. A previous study encoded 461 lines of
arithmetic-dense regulation (an NBA Collective Bargaining Agreement excerpt) as a Judgment Pack and
found that a substantial part of the *decision* could not live in the pack and migrated into a
preparation layer. This study asks whether the same thing happens on a **qualitative** policy — one
with almost no arithmetic.

**Your job is to encode, and to measure honestly what would not fit.** A result of "everything fit"
is a completely acceptable and useful outcome. Do not manufacture problems, and do not paper over
them either.

## Hard rules

1. **Read only `reference/`** — `policy.md` (the airline agent policy under test),
   `judgment-pack-core.md` (the specification), and the JSON Schema. Do **not** search the web, and
   do **not** read anything outside this directory. In particular there is a prior study's pack and
   report elsewhere on this machine: do not look for them. Your independence is the point.
2. **Do not use any MCP tool.**
3. You may run the installed `judgment-pack` CLI to learn the format and validate your work:
   - `judgment-pack spec examples` and `judgment-pack spec examples <name> --write /tmp/ex.json`
   - `judgment-pack spec schema 0.1.0-draft --write /tmp/schema.json`
   - `judgment-pack spec validate <file>` — your pack must exit 0
   - `judgment-pack experimental evaluate <pack> --facts <facts.json> --format json`

## What to build

### 1. The pack — `pack.json`

Encode the **"Cancel flight" decision** from `policy.md` §"Cancel flight" as a single judgment pack:
*given a cancellation request, may it be cancelled?* Use the outcomes the policy itself supports.
Where the policy says the agent "cannot help and transfer is needed", use the format's escalation
machinery rather than inventing an outcome for it.

Include the evidence the policy requires the agent to obtain. Cite the policy section in
`sourceRefs`. Where a fact being missing should stop the decision rather than default it, use
`onUnknown: escalate` — the format's uncertainty handling is the thing most under test here.

The pack must pass `judgment-pack spec validate` with exit 0.

### 2. A facts document — `facts.example.json`

One realistic input the pack can be evaluated against, and the evaluation output pasted into your
report. Money and any ordered-comparison value must be a JSON **string** matching the decimal grammar
`-?(0|[1-9][0-9]*)(\.[0-9]+)?` — the evaluator yields `unknown` for ordered comparison of JSON
numbers.

### 3. The measurement — `MIGRATION.md`

This is the actual deliverable. Count and classify **everything the pack could not hold itself**:

- **M1 — prepared facts.** Every fact your pack reads that is not stated directly by the requester
  but must be computed or looked up first. List each with its definition. Give a total.
- **M2 — prepared *determinations*.** Of those, which are not mere data but a *conclusion that
  applying the policy requires* — a classification the policy text does not state and that something
  outside the pack must decide. This distinction is the heart of the study: separate "a value someone
  measured" from "a judgment someone made". Give a count and justify each entry.
- **M3 — things the format cannot say at all.** Any place where you needed an expressive device the
  format lacks. Be specific and quote the policy sentence that needed it.
- **M4 — architectural constraints you hit.** Any place the resolution model (§8) forced a structural
  choice — for example how you had to arrange rules and outcomes so they do not conflict — that the
  policy itself did not dictate.
- **M5 — what fit cleanly.** Equally important. Which parts of the policy the format carried with no
  friction at all.

For every entry, quote the sentence of `policy.md` that produced it. Number the entries.

### 4. Interpretation decisions — `DECISIONS.md`

Every place the policy text was ambiguous and you chose a reading: numbered, with the text you relied
on, the alternatives, and why you chose as you did.

## Definition of done

`pack.json` validates at exit 0; one real evaluation is shown; `MIGRATION.md` gives the five counts
with quoted evidence; `DECISIONS.md` records the judgment calls. Commit nothing.

Report the five counts as a short table at the end of your final message.
