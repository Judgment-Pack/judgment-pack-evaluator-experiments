# Five clean-room second mirrors — §6 C10's instrument, pre-assigned

Study 011 built this instrument once, after its data, as a post-hoc answer to
its census's circularity caveat. This study inherits the circularity five ways
— five policy texts, three of them substantive authored prose from the team
holding the prediction — so §6 C10 registers the instrument **before any
call**: per arm, an independent reader is given that arm's `POLICY.md` bytes
and nothing else, writes `analysis/mirror2_<arm>.py`, and must agree with the
registered mirror elementwise on that arm's 280-cell landmark grid.
`harness/integrity.py` refuses the batch while any arm's clean-room mirror is
missing or disagreeing. Every attempt is retained and published, including
every failed one; a study that keeps only the readers that agreed has measured
nothing.

## Pre-assignment — recorded before any reader ran

§6 C10 clause 1: the reader identities and the commission order are recorded
here, and committed, before the first reader runs. Round 2's reason: with no
pre-designation, "commission a reader, and if it fails, commission another" is
available and invisible — and the arm most likely to need a second reader is
arm E, the one arm whose derivability is the study's central question.

| arm | reader vendor | model | harness | commission order |
| --- | --- | --- | --- | --- |
| A | OpenAI | `gpt-5.6-sol` | `codex-cli 0.145.0`, `exec --ignore-user-config --sandbox read-only`, empty working directory, fresh CODEX_HOME, policy bytes inlined in the prompt | 1 |
| B | OpenAI | `gpt-5.6-sol` | same | 2 |
| C | OpenAI | `gpt-5.6-sol` | same | 3 |
| D | OpenAI | `gpt-5.6-sol` | same | 4 |
| E | OpenAI | `gpt-5.6-sol` | same | 5 |

One reader identity serves all five arms, as in Study 011; each arm's read is
a fresh session with no memory of any other. The reader's vendor lineage
(OpenAI) is distinct from the lineage that drafted the registered mirror and
the arm texts (Anthropic-model sessions), so a shared misreading cannot come
from shared weights, whatever else it could come from.

## The isolation, stated exactly — corrected under round 3, finding 8

Study 011's builder was an agent with file access under an instruction not to
read anything but the policy. This study's readers ran closer to sealed, and
the first version of this section overclaimed how close; what follows is what
the retained bytes support, no more.

Each reader ran as one `codex exec` call in an empty scratch directory
outside every worktree, under `--ignore-user-config` with a fresh
`CODEX_HOME`, with the arm's `POLICY.md` bytes inlined verbatim in the
prompt. The sandbox was `read-only`, which restricts what the process may
**write**, not what it may **read**: a reader that went looking could have
opened study files, so non-consultation is **behavioral evidence, not a
structural guarantee** — the retained transcripts show no tool call of any
kind in any of the five sessions, and each reader's consulted statement is
retained per attempt. The empty working directory and the fresh `CODEX_HOME`
close the passive paths (nothing to list where it stood, no operator
configuration reaching it); the active path is closed only by the evidence.

Beyond the policy bytes the prompt supplied 706 bytes of fixed interface text
— the framing line, the record shape (`sanctionsHit` bool,
`registeredCountry` string, `handlesPersonalData` bool, `riskScore` decimal
string), the three outcome tokens (`clear`, `manual-review`, `reject`), the
no-imports/no-I/O rules, and the request for a consulted statement —
identical for every arm and published verbatim below. It names the policy's
own three outcomes in the harness's spelling and carries no threshold, no
class, and no study term; C10's clause 2 is amended to register exactly this
suffix. 011's honesty clause carries over unchanged: isolation of an agent
is a claim about a process, not a proof, and what rests on it here is
bounded by the grid — 280 cells pin every inclusive/exclusive decision the
predicates name, whatever the reader consulted.

## The commission prompt, verbatim

Published before the runs; the same text serves every arm, with only the
policy bytes substituted:

```
Here is a policy document.

<the arm's POLICY.md bytes, verbatim>

Write a self-contained Python module that implements this policy as a single
function `verdict(vendor)`. `vendor` is a dict with exactly these members:
"sanctionsHit" (bool), "registeredCountry" (str, a two-letter uppercase
code), "handlesPersonalData" (bool), "riskScore" (str, a decimal string that
compares numerically). Return exactly one of the strings "clear",
"manual-review", "reject" — the policy's three outcomes. Use no imports
beyond the standard library, no I/O, no randomness. Cite each clause of the
policy next to the code that implements it. After the module, state in one
sentence what you consulted to write it. Output the module as one python
code block.
```

## Attempts and agreement

One attempt per arm, in the registered commission order, all on 2026-08-08;
raw reader output, the exact prompt sent, the extracted module and the
consulted statement are retained per attempt under
`analysis/mirror2-attempts/<ARM>/attempt-1/`. No attempt was discarded and no
reader was re-commissioned.

| arm | commissioned (UTC) | exit | module | agreement (`integrity.verify_mirror2()`) | consulted statement |
| --- | --- | --- | --- | --- | --- |
| A | 15:01:18Z | 0 | `analysis/mirror2_a.py`, 24 lines | **AGREES**, 280/280 at (40, 70) | "I consulted only the vendor screening policy provided in the prompt." |
| B | 15:01:35Z | 0 | `analysis/mirror2_b.py`, 26 lines | **AGREES**, 280/280 at (40, 70) | same |
| C | 15:01:47Z | 0 | `analysis/mirror2_c.py`, 26 lines | **AGREES**, 280/280 at (40, 70) | same |
| D | 15:01:59Z | 0 | `analysis/mirror2_d.py`, 27 lines | **AGREES**, 280/280 at (45, 72) | same — emitted inside the module as its closing comment rather than after the block; `attempt-1/consulted.txt` records the placement |
| E | 15:02:10Z | 0 | `analysis/mirror2_e.py`, 25 lines | **AGREES**, 280/280 at (40, 70) | same |

**The two derivations that were the point.** Arm D's reader, given a text
whose literals are 45 and 72, wrote comparisons at 45 and 72 — the rename is
readable. Arm E's reader, given a text with **no numeric content in any
clause body**, derived `Decimal("70")` and `Decimal("40")` from the
conventions paragraph's stated 0–100 scale and the two threshold definitions
("seven tenths of that full range", "four tenths of that same full range"),
and its module agrees with the registered mirror on every cell. **The
registered failure consequence — arm E re-authored as an ambiguity arm — does
not fire**: the denamed values are derivable by an independent reader from
the arm's bytes alone, which is precisely what this instrument existed to
establish before any call.

**What the agreement establishes, and what it does not** — 011's honesty,
restated for five arms: agreement shows each arm's reading is *reproducible
from that arm's own bytes by an independent reader*; it does not show the
reading is correct, and it cannot see a divergence that lives only in the
prose and never reaches a verdict. C8's census and inclusivity checks bound
that syntactically, the pre-freeze cross-vendor review reads the five texts,
and §7 and §9 record that no instrument closes it. The readers' speed and
brevity are visible in the retained transcripts; a reader that agrees for a
shallow reason is bounded by the same grid that catches a shallow
disagreement — 280 cells pin every inclusive/exclusive decision every
predicate names, and §2.4 records what no finite grid can pin.
