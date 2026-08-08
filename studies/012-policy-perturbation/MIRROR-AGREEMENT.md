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

## The isolation, stated exactly

Study 011's builder was an agent with file access under an instruction not to
read anything but the policy. This study's isolation is **structural rather
than behavioral**: each reader runs as one `codex exec` call in an empty
scratch directory outside every worktree, under a read-only sandbox, with the
arm's `POLICY.md` bytes inlined verbatim in the prompt — there is no study
file within reach to consult, no second turn, and no tool surface that could
fetch one. What the prompt supplies beyond the policy bytes is interface, not
reading: the record shape (`sanctionsHit` bool, `registeredCountry` string,
`handlesPersonalData` bool, `riskScore` decimal string) and the three outcome
tokens (`clear`, `manual-review`, `reject`), which name the policy's own three
outcomes in the harness's spelling. 011's honesty clause carries over
unchanged: isolation of an agent is a claim about a process, not a proof —
what rests on it here is bounded by the sandbox and the empty directory, and
the full prompt text is published below so a reader can see exactly what the
model was given.

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

*(Recorded per attempt as each reader runs; the agreement is
`harness/integrity.py`'s `verify_mirror2()` — the registered mirror at the
arm's pinned `(T_low, T_high)` against the reader's module, elementwise over
the arm's own 280-cell grid. Raw reader output is retained under
`analysis/mirror2-attempts/`.)*
