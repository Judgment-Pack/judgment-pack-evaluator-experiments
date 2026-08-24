# Ports — what Study 020 takes, from where, and what changed

Study 020 is an **instrument repair on Study 019** (`PREREGISTRATION.md` §7): it
asks 019's question of the same three representations with the instrument
repaired, and the machinery it counts with is inherited as **bytes**, not as
descriptions. This file records every port, its digest on both sides, and
exactly what was changed. `harness/integrity.py` machine-reads the table below
and binds each row **to the authority that row actually has** before any call is
made and before anything is scored.

**The chain, and why it is shorter than 019's while binding more.** Study 019
inherited seven files from Study 012 and could bind them only to the seven
destination cells 012's own `PORTS.md` published. Study 019 is **frozen**, and a
frozen study publishes a digest for every byte of its harness and every
registered artifact in one file, pinned by its own registry. That file is this
port's source-side authority, and `integrity.source_lock()` reads it first.

```
this file                                    (pinned in harness/PINS.json at port time)
    -> Study 019's harness/PINS.json              9ba6394db66f0e3723359c17f68e4a612870a015f3f973e1efad10fd522a759c
       Study 019's harness/STUDY-MANIFEST.sha256  79076e3181fd738b457a6c63d827be0769bb36d85b66ce35c37e6cf211d3e1a0
          (the digest 019's OWN registry pins for it under `studyManifest`,
           read from it and not chosen here)
       Study 019's harness/PORTS.md
          (the digest 019's OWN registry pins for it under `ownPorts` — the
           SECOND authority, for the seven rows 019 itself ported)
```

The port was taken at commit

```
commit e87e1311da11c28e929edf1e7e39f048e4ec0e6a
```

**Every harness row is WHOLE-FILE and by digest.** The source path and the
destination path are the same path — a row that renames a file is a row this
study is not taking by digest, and `verify_chain()` refuses it by name. The
source cell of every row must equal 019's own lock line for that path, and 019's
working file must hash to it. There is no partial row in this table:
`PREREGISTRATION.md` §7's "ported with no design change" list is the whole
harness, and the thirteen registered deltas are changes ON TOP of a complete
port rather than pieces of an incomplete one.

**Two source-side authorities, and the stronger one is named per row.** Every
row answers to 019's lock. The seven files 019 itself ported answer to BOTH —
019's own `PORTS.md` destination cell AND its lock line — and
`integrity.TIER_PORTS_PATHS` is that set: a row in that tier is bound TWICE on
the source side, and `verify_chain()` requires the two to AGREE, refusing a
disagreement rather than resolving it in either direction. That tier is not
folded away by the move to the lock, because two agreeing authorities are a
stronger binding than either alone.

**The count is a constant, not a sentence.** `integrity.REQUIRED_PORTS` fixes
the destination set at exactly the forty-six files this table names, and
`verify_chain()` requires the destination set to be exactly the forty-six files
above and refuses a second row for one destination — so a deleted row refuses
rather than quietly dropping a check. Study 019's round-1 finding R1-20 was this
sentence going stale at "five" while the constant held seven, so
`harness/tests/test_prereg_currency.py` reads the number out of the constant and
requires the document to spell the same one.

**This is a COMPLETE port of 019's executable harness surface AND of its
registered artifacts.** Every module 019's scorer, driver and wrapper execute is
here, and so are the gold suite, both mutant corpora and their manifests, both
reference implementations and their payloads, the off-gold certificate, the two
verification documents and the frozen policy prose — bound on both sides against
019's lock by `integrity.verify_ported_artifacts()`. What is still a PARTIAL
port of the study is everything 019 EARNED rather than built: its arms, its
results, its review record and its spent reviewer set, which do not carry and
are listed under **What does NOT carry** below.

**ONE INHERITED RESIDUE IN THE PORTED BYTES, recorded rather than repaired.**
019's frozen `design/mutants/refB/MANIFEST.json` embeds its generating
environment's ABSOLUTE toolchain paths — the OPA binary and the
`caps-filtered.json` capabilities file under an operator scratch directory,
`gen_mutants.py`'s own defaults, at a root its diagnostic scrubber does not
know. The bytes are the lock's bytes (the combined manifest digest reproduces
`mutantManifests.sha256AtSource` exactly), so §4.1's port-by-digest carries
them unchanged — but `design/mutants/regenerate.py --check` reproduces them
ONLY when invoked with the manifest's own recorded toolchain paths: from any
other seat the byte-comparison lands 375/376 with exactly this manifest
differing, every payload identical. That is what "reproduction" means for a
record that names its inputs, and it was measured, not reasoned: a run from a
different operating seat produced the 375/376, and the committed
`REGENERATION-CHECK.json` (376/376, both arms) is a run under the recorded
paths. The same class of leak 019's G10 scrubbed from the golden capture; a
repair belongs upstream in 019, not in a port that promises the lock's bytes.

**The commit is provenance, not authority.** Study 019 had one row —
`harness/make_manifest.py`, from Study 014 — bound to a recorded commit and to
nothing older, because Study 014 pinned none of its own harness sources. That
tier does not survive this port: the same file is bound here to 019's lock like
every other row. No row in this table is satisfied by "whatever that commit
happened to hold". The one thing still bound to the commit alone is the carried
`design/` tree, and it says so under **Carried UNPINNED** below.

**The lineage before 019 is HISTORY.** `harness/PINS.json`'s
`pinnedFrom.history` records Study 019's own `pinnedFrom` — Study 012's registry
digest `cff265e7…` and the Study 014 note — and `verify_chain()` checks that the
recorded history is the history 019's registry actually carries. It does not
walk into Study 012: a two-level walk would make this study's freeze depend on a
tree two studies away, and 019's own verification is what covers that level.

**New here, and deliberately absent from the table.**
`harness/e4lib/presence_idiom.py`, `harness/e4lib/family.py`,
`harness/tests/test_score_presence_idiom.py`, `harness/tests/test_family.py` and
`harness/tests/test_sweep.py` are new in 020 (§7 deltas 3, 5 and §2.1's sweep):
nothing like them existed in 019, so a two-sided row would claim an inheritance
that does not exist. They are registered in `integrity.NEW_IN_020`, whose
membership is CHECKABLE rather than declared — 019's lock must not name the path
— and `REQUIRED_PORTS | NEW_IN_020` is checked against the harness directory, so
a harness file registered nowhere still refuses. `harness/PINS.json`,
`harness/PORTS.md`, `harness/SCAFFOLD.md`, `harness/POWER-PRESENCE-IDIOM.md`,
`harness/ADVISORIES.md` and `harness/STUDY-MANIFEST.sha256` are this study's own
for the same reason.

## The harness — 46 rows, two-sided

| source (Study 019) | 019's lock digest | destination (Study 020) | digest as landed | changed |
|---|---|---|---|---|
| `harness/authoring_call.sh` | `8b326083e805062fcd21f341d05fa20c97fc3629180a06134147c514fcfa08da` | `harness/authoring_call.sh` | `68cbf401e73f43aec40297e279fe51d0b39595bbdae40e3404b26f4718e3def6` | **BOTH LINES' CHANGES, merged.** *From the apparatus port:* **re-pointed.** Scratch/home/bin names `s020-…`; the CALL.json note names this study. No call-path logic touched. *From the sweep-driver line:* **complete port, FOUR registered differences, and the mechanics are unchanged.** Everything 019 registered is carried byte-for-byte: the `timeout --signal=TERM --kill-after=<grace> <ceiling>` outermost wrapper reading both values from `harness/PINS.json`, the closed exit-status set {0, 1, 10, 11, 12, 13} with the post-call phase flag and its ERR trap (R1-4), the per-arm prompt-digest gate, the byte-exact prompt idiom `PROMPT="$(cat FILE; printf x)"; PROMPT="${PROMPT%x}"` (R1-8), the scratch-path leak screen reading `harness/leak_tokens.py`'s `SCRATCH_TOKENS`, the author-side/apparatus-side split in both post-call helpers (R1-5), the credential traps, the resolve-before-create descent and the worktree repair. **(1) THE EFFORT-FLAG SEAT (§2.1, M-24/M-25).** The wrapper reads `codex.reasoningEffort` from the registry beside `codex.model`, passes it to the CLI by explicit flag and stamps it into `CALL.json` as `reasoningEffort`, so every retained slot records the condition it ran under whether or not a transcript witnesses it. The FLAG'S SPELLING is read from the registry rather than written into the shell, because §2.1 registers the spelling as resolved empirically at pin time and a spelling written here would be a guess the registry could not correct — and the resolution (2026-08-24, against the pinned binary, with no model call) made that seat TWO members rather than one: `codex exec --help` at `codex-cli 0.145.0` names **no reasoning-effort flag at all**, so the only spelling this build accepts is the config override `-c model_reasoning_effort=<tier>`. The wrapper therefore composes the argv token from `codex.reasoningEffortFlag` (`-c`) and `codex.reasoningEffortConfigKey` (`model_reasoning_effort`), and `CALL.json` stamps the tier, both members and the exact token. A single member could only have carried it by hard-coding the key in the shell — the guess §2.1 forbids — or by sending the bare tier after `-c`, which this build reads as a malformed override. **(2) THE TWO BRANCHES, both seated.** A null `codex.model` refuses exactly as in 019 — a null member reaches the shell as the string `None`, which `-m` would accept as a model name. A null `codex.reasoningEffort` refuses too, EXCEPT under `PIN_LABEL=SWEEP`, which is the one registered exemption (M-25) and which the wrapper accepts from the driver's `--sweep` mode and from nowhere else: running the sweep outside the harness is the 019 failure exactly, and a wrapper that could be talked into the exemption by an environment variable an operator sets by hand would reproduce it. Under the exemption with no setting threaded the flag is omitted, `CALL.json` records `reasoningEffort: null` with `reasoningEffortSource: "sweep-default"`, and the slot is stamped `citable: false`. **(3) THE SWEEP'S PER-CALL SETTING AND ITS OWN SLOT ROOT** (§2.1, and the difference the sweep DRIVER made necessary). The exemption alone runs one setting — the CLI's default — and §2.1 registers three, so the setting for each call is threaded in `SWEEP_EFFORT`, which `harness/batch.py` sets UNCONDITIONALLY beside `PIN_LABEL` under its `sweep` subcommand and nothing else does. It is refused under `PRIMARY`, and it is refused when it names a tier outside the registry's `sweep.settings` — the swept SET is registered before the sweep (§2.1, 2026-08-24), and a wrapper that would run an unregistered tier is a wrapper the cap clause cannot bind. Under the sweep label the slot is written at `sweeps/<UTC date>-effort-sweep/<setting>/arm-<ARM>/run-NNN` instead of `arms/<ARM>/authoring/run-NNN`, so R10-1's prior-authoring freeze gate cannot see the sweep's slots; the anchor guard and round 10 finding 6's resolve-before-create descent move with it and are ONE implementation over a computed component list rather than a second copy that could drift. The anchor is computed from the registry (`sweep.root`) and from the setting the driver threaded, never from the slot path's own text — the one component the wrapper cannot know, the dated label, is read from the path and checked against the registered shape. **(4) THE STUDY ID.** `s019-…` scratch, home and per-run binary names become `s020-…`; `$STUDY` is still the parent of the script's own directory, so the anchor and every guard built on it are unchanged. `tests/test_batch.py::WrapperExitPaths` drives all six statuses through the committed bytes under the real bash, and `tests/test_batch.py::TheEffortFlagSeat` drives both branches of (2) including the refusal when the exemption is claimed without the label, and `tests/test_sweep.py::SweepThreadingThroughTheWrapper` drives (3) through the same bash — the composed argv pair, the refusal of an unregistered tier and the refusal of a setting under `PRIMARY` |
| `harness/batch.py` | `0e5306847b1292fe81db99e6ee3b67d5fbed68497615f4e82df69e94d472d6fe` | `harness/batch.py` | `fc06b8665274dfe2d083965551dd087e06254b4ddf12cb4ed8d42551875c906d` | **BOTH LINES' CHANGES, merged.** *From the apparatus port:* delta 7 (§7): the schedule constants carry the port skeleton pending the registered round count; label rule wiring for --sweep. *From the sweep-driver line:* **complete port, FIVE registered differences.** Carried unchanged: the whole calling half (`check_registry()`, `preflight()`, `require_freeze()`, `invoke()`, `stamp_slot()`, `refuse_slot()`, the slot files, `seal_slot()`, the ledger records and chain, `reconcile_ledger()`, `run_batch()`), the golden-context capture with its `identities` provenance, the isolation negative control, the transcript binding at the seal (`transcript_verdict()`, `bind_transcript()`), the fail-closed status map and `wrapper_code()`'s refusal of an unregistered status (R1-4), the shortfall SCHEMA with its slot/seal inventory and both validators (R1-7), `require_lawful_destination()`, the `__main__`-guarded safe-import-path and untracked-source tripwires, and the four functions carried from Study 012's `harness/score_rates.py`. **(1) `CODE_PARTITION` GAINS `presence-idiom-unsound`** (§1a's table, §3.2, ruling M-14) on the AUTHORING side — the seventh admission code, valid, counted, scoring zero on every endpoint it reaches. It is built into `AUTHORING_CODES` rather than special-cased, so R1-4's import-time exhaustiveness check reaches it for free: a code the scorer can emit is a code the population rule names. **(2) `AUTHORING_CODE_ARMS` IS NEW**, because §1a's table gained a third column — *arms it can reach* — and a two-column partition cannot be diffed against a three-column registration. It is checked in both directions at import against the authoring tuples, and `tests/test_partition.py` diffs it against §1a's own table AND against `e4lib/admit.py`'s enforcing `ARM_REACHABLE_CODES`, so the B/C-only reach of the new code has three places that must agree. **(3) `CALIBRATION_ROOT` IS NEW** (§2a.2): the pre-freeze pilot runs through THIS driver and leaves authored slots behind, and 019's `DEVIATIONS.md` D-2 records a freeze gate that refused any tree containing prior authoring. Keeping the pilot out of `arms/` is what makes `make_manifest.prior_authoring_problems()` permit it STRUCTURALLY rather than by an exception list, while `make_manifest.calibration_problems()` REQUIRES the subtree at the freeze — both halves of §"The freeze and the primary attempt"'s rule, and `tests/test_manifest.py` drives each half against the other's tree. **(4) THE LABEL RULE'S SECOND TUPLE** reaches `require_freeze()` for free, because that gate was already `integrity.study_label()`'s and not one pin's (019's change 6): a null `codex.model` or `codex.reasoningEffort` now refuses a registered batch, and `tests/test_batch.py` drives the refusal pin by pin over both tuples. **(5) THE PRE-PILOT EFFORT SWEEP IS A MODE OF THIS DRIVER** (§2.1, M-8/M-20/M-24/M-25) — section D9, and the one addition Study 012 has no counterpart for at all. §2.1 registered `n = 3/arm across three settings — 27 calls`, run through this apparatus and never outside it, published in full, `citable: false`, with a per-setting abort rule and a call cap, and the harness had no mode that could run it. `batch.py sweep` is that mode: it carries §2.1's registered constants — `SWEEP_SETTINGS` (the maintainer's dated 2026-08-24 decision: `low`, `medium`, `high`), `SWEEP_PER_ARM`, the DERIVED 27-call cap, the 72 h budget and its priced `N = 60` branch — and `sweep_preflight()` refuses on any disagreement with `harness/PINS.json`'s own `sweep` block, because a registration carried in two places is only safe if a drift refuses. It runs a sequential ARM-INTERLEAVED, A-FIRST schedule (A first because the abort rule reads the setting's first arm-A call; interleaved because the budget projection needs a mean for every arm and reaches one after three calls rather than seven). It writes under `SWEEP_ROOT` and not `arms/`, which is what keeps R10-1's occupancy gate off it STRUCTURALLY. It runs M-24's WITNESS RESOLUTION as step zero over the first sweep call's own transcript — deciding the branch on `turn_context` alone, because gate 5 is a `turn_context` gate — and records which branch fired. It publishes `SWEEP.json` and `SWEEP.md` after EVERY call, so a sweep killed part way through has published what it spent. Its own preflight is NOT `preflight()`: `require_freeze()`, `check_registry()`, `require_golden()` and `require_isolation_negative()` all gate on values the sweep PRECEDES or PRODUCES, and the sweep reads the design-time pins under the registered sweep label instead — which leaves exactly M-25's own requirement, `codex.model` filled and `codex.reasoningEffort` exempt. It computes no rate and chooses no setting. `tests/test_sweep.py` drives all of it, both abort clauses through the stand-in CLI and the occupancy gate in both directions. **DELIBERATELY NOT CHANGED, and named so a reader does not mistake a carried byte for a settled question: the SCHEDULE CONSTANTS.** `SEQUENCES = 6`, `BLOCKS = 8`, `BLOCK_ORDER`, `TAIL`, `ROUNDS = 50`, `RUNS_PER_ARM = 50` and `REGISTERED_SLOTS = 150` are Study 019's, and §2 registers them as **wrong by construction at any other N** — `derive_order()`'s cached answer is the floor (1, 1) *at 50 rounds*. 020's N is a `TODO(prereg)` output of the pre-pilot sweep (§2.1), so `harness/PINS.json` carries `batch.n`, `batch.slots` and `batch.order` as NULL and `check_registry()` REFUSES that state — no batch can be spent against an unregistered shape. Re-deriving the order at the registered round count is §7's delta 7 and is `harness/SCAFFOLD.md` item S3; until it lands the constants are a PROVISIONAL planning shape and this cell is where that word is registered |
| `harness/e4lib/__init__.py` | `0887ba7f3916801d1e4bada096e0b135c745dfe2ac2dde290aa4d9402f3d6e0a` | `harness/e4lib/__init__.py` | `abb52bb99624e894c0599f62432bd8a9204111d0e19eb2e3c1f5fa3092944a8a` | delta 5 wiring: the family module exported |
| `harness/e4lib/admit.py` | `ac2c481e594690e009f10b325786bb98abbc4f933ee154364b4a6bd156cf21a8` | `harness/e4lib/admit.py` | `b9744854e053965bd477254db8997bb9c8be0b3b3905ab4cd565d25be1a16f59` | **complete port, TWO registered differences — §7's delta 3.** Carried whole: the SIX-code reconciliation table and its argument, the mechanical `v0-syntax` discriminator (two invocations of the pinned binary and no string matching), `admit_arm_a()`'s payload-not-exit-code reading, `admit_arm_rego()`'s error-CODES-not-prose recording, `ARM_REACHABLE_CODES` and `admit()`'s refusal of an arm-structural leak, and the standing no-repair rule. **(1) THE SEVENTH CODE.** `DROP_ORDER` gains `presence-idiom-unsound` LAST, and the position is load-bearing rather than cosmetic: the detector reads a policy the pinned binary has ALREADY accepted, so every earlier code describes an artifact that never reached it, and an artifact that is both unparseable and presence-idiom-unsound is unparseable because the earlier check is the one that refused. `ARM_REACHABLE_CODES` gains it for B and C only (§11.11's ceiling: arm A's format has no analogous single-operator trap on this surface), so an arm-A run that somehow produced it is a refusal here rather than a row in a published E2 table. **(2) THE KILL SWITCH IS READ AS DATA.** §3.2 registers the guard CONDITIONALLY — "if the detector cannot meet (i) and (ii) exactly, the guard is not registered at all" — and a conditional registration whose condition lives in prose is a condition nothing enforces. `guard_is_registered()` reads `harness/PINS.json`'s `presenceIdiomGuard.registered` and FAILS SHUT toward not-registered: a registry with no such member, or one whose member is anything other than `true`, does not emit the code. When the switch is off the detector still RUNS and its census still lands in `detail`, because §3.2's fallback is that the mechanism is carried as a Tier D descriptive finding — what is withheld is the CODE, not the measurement |
| `harness/e4lib/capabilities.py` | `5793fa83810f64ab0ba3f4098a0555ae6aea8b44e86334abc0d2a3fd25643296` | `harness/e4lib/capabilities.py` | `5793fa83810f64ab0ba3f4098a0555ae6aea8b44e86334abc0d2a3fd25643296` | ported by digest, byte-identical to 019 |
| `harness/e4lib/census.py` | `f7e603df0440785b55b10a61b5aef2cc0fbd42677e7e713a71013840f77d0601` | `harness/e4lib/census.py` | `ea363300c446cd98ad9dd25b03b4383b22a031b9873ecd3826eca1e391b466ed` | port note added to the module head; no code change |
| `harness/e4lib/decision.py` | `3edb743f5bfe738e28035889e3d7be22f1f0af80de61f74ae8998d8877d81921` | `harness/e4lib/decision.py` | `4e8238654bfbb18f72c8e8351df97841b280266ef10d2d1ca03e7c31f321422d` | delta 5 (§5): the ordered decision table over the IU family verdict |
| `harness/e4lib/domain.py` | `20016d0987344be7544b503b0856d13b70c62dd434d6e708652749cbc4a555f1` | `harness/e4lib/domain.py` | `20016d0987344be7544b503b0856d13b70c62dd434d6e708652749cbc4a555f1` | ported by digest, byte-identical to 019 |
| `harness/e4lib/e4.py` | `13646b0d2a11e4580c3a971505dcdf107572c60ac5cf9cf8bd9171b477ddea3f` | `harness/e4lib/e4.py` | `788d276401c89ed66f6b98bdc673026f05145daf9c5163a847907597dc1daee3` | deltas 1-2 (§7): per-language denominators and lattices kept, threshold arm removed |
| `harness/e4lib/engines.py` | `1382c0cb523aca8fb8e99a02838721d4831847aa307c628a3a20484b0f469c09` | `harness/e4lib/engines.py` | `bd9ff5a61fa2c0df1be59bef384a5ab795325bab5e3193c6126ecc29973c84d9` | **BOTH LINES' CHANGES, merged.** *From the apparatus port:* ported by digest, byte-identical to 019. *From the sweep-driver line:* **complete port, ONE registered difference.** `Toolchain`'s fail-closed resolution and digest enforcement (every path resolved to an absolute real path before it is hashed, and the resolved path is what is invoked), `clean_env()`, `_run()`'s single scrubbed-environment call site and one engine timeout, `jpack_json()`, `opa_check()`, `opa_test()` with R3-3's rule that `errored` OUTRANKS `failed` and that every reported failure is adjudicated, `opa_eval_document()`, `eval_pack()`/`eval_rego()`, `capabilities_canary()`'s both-directions control, and the discipline that no verdict and no kill is read from an exit code are all carried byte-for-byte. **(1) `opa_parse()` IS NEW** — `opa parse --format json` on one file, returning `(exit, stdout, stderr)`. It is HERE and not in `presence_idiom.py` for the reason every other invocation is here: the pinned binary is invoked from ONE module, under `_run()`'s scrubbed environment and the one timeout, so a second call site cannot acquire a second environment. It takes no capabilities file — `parse` performs no evaluation and accepts no `--capabilities` at the pinned version — and it is never scored: the detector reads the syntax tree and the syntax tree only. §6's `engine-execution-clean` control covers it, as it now covers E6's extra `opa test` invocation |
| `harness/e4lib/extract.py` | `4e853d688609dde4f3b0c98f33418218afed0c44048a9609b8234241b96aca9c` | `harness/e4lib/extract.py` | `4e853d688609dde4f3b0c98f33418218afed0c44048a9609b8234241b96aca9c` | ported by digest, byte-identical to 019 |
| `harness/e4lib/reviewer.py` | `0fc38aa4ebde113ec361f2986aab49d1925b4d962f1e1e554551d2ebba753b31` | `harness/e4lib/reviewer.py` | `cfb3a97e36d98ba7aafdc76471ad143b5bb295502ffa3181ab074e6d32e5afc1` | **complete port, ONE renamed member and no rule changed.** The sealed set's non-executing loader — the schema, the 6–10 cardinality, both languages, the registered `rm-<language>-NN.<ext>` filenames, containment on real paths and every payload's digest, all of which `make_manifest.reviewer_load_problems()` calls from `--check` and `--freeze` (R8-2) — is carried whole, as is the execute-once discipline and the rule that no reviewer mutant is paired, enters a witness group or moves any registered quantity. **(1)** The one edit is the rename that follows §7's delta 4: the executor reads `referenceIdentityPass` where it read `identityPass`, because 020 has two identity relations and this one is the reference relation. **The SET does not carry** (§4.3): 019's is spent, and `harness/PINS.json`'s `reviewerMutantSet.sha256` is null against a FRESH set authored during 020's review rounds. This module is the machinery, not the payload |
| `harness/e4lib/stats.py` | `e2ac82dd2248896ef8c3f72fbdd9a51ba92de3a67a4df24a6567a64c64c94c07` | `harness/e4lib/stats.py` | `09961a3f688d23a130566d0f3466e9b28c12f8c387f37d794df2a6b464658301` | delta 5 (§5): BCa intervals and the two permutation schemes with pinned B and seed |
| `harness/grid_gate.py` | `eea10546a2289129dd785ff9eddd546f83a1ac02ba508e51d4133567561bf75c` | `harness/grid_gate.py` | `eea10546a2289129dd785ff9eddd546f83a1ac02ba508e51d4133567561bf75c` | ported by digest, byte-identical to 019 |
| `harness/integrity.py` | `ba2175ad213abcd019e10dc7768aa16f5bcb7f52f77c5af1520c942fc81657e3` | `harness/integrity.py` | `7d837cadeee93935c023fa6d41682a2db900e5bc718799aac0a7784bf9edbf12` | **BOTH LINES' CHANGES, merged.** *From the apparatus port:* port chain to 019's lock (§7) plus NEW_IN_020 and the ports/new exhaustiveness check. *From the sweep-driver line:* **complete port, FOUR registered differences, all in the chain and the label rule.** Carried verbatim: `IntegrityError`, `digest()`, `_refuse_duplicate_keys()`, `load_json()`, `bare()`, `parse_ports()` and the `ROW` regex; `verify_interpreter()`; `_code_equal()`, `_const_equal()`, `verify_bytecode()` with R5-1's unconditional refusal of a TRACKED cache read from `git ls-files`; `_refuse_unsafe_import_path()`; `pin_is_filled()` with `PIN_PLACEHOLDERS`/`PIN_PLACEHOLDER_PREFIXES` and the salvage audit's whole stand-in rule; `CEREMONY_LIFECYCLE_PINS` and `ceremony_unfilled_pins()`; `PIN_SOURCES` and `unfilled_pin_sources()` (R7-8); and `verify_manifest()`. **(1) THE SOURCE STUDY IS 019 AND THE CHAIN HAS TWO SOURCE-SIDE AUTHORITIES.** `TWELVE`/`FOURTEEN` become `NINETEEN`; `TWELVE_PINS_SHA256` becomes `NINETEEN_PINS_SHA256`; `TIER1_TWELVE_PATHS`/`UNPINNED_SOURCES` become `TIER_PORTS_PATHS` and `TIER_MANIFEST_PATHS`; and `parse_manifest()` is new — an ADR 0004 exact-set manifest read as `{path: sha256}`, refusing a malformed line and a duplicated path rather than resolving either. A tier-PORTS row is bound TWICE on the source side and the two authorities must AGREE; a tier-MANIFEST row is bound to 019's manifest, which 019's own registry pins. **The commit-only tier is gone**, so no row is satisfied by a commit. **(2) `REQUIRED_PORTS` IS TWENTY DESTINATIONS, not seven**, because 020 ports 019's whole executable harness surface. `presence_idiom.py` is deliberately absent from it: it is new here, and a row would claim an inheritance that does not exist. `verify_chain()` also refuses a second row for one destination, which 019 stated in prose and left unchecked. **(3) THE LINEAGE BEFORE 019 IS CHECKED AS HISTORY.** `HISTORY_STUDIES` and the `pinnedFrom.history` comparison require this study's recorded lineage to be the lineage 019's own registry carries — Study 012's registry digest and the Study 014 note — and refuse a history this study wrote for itself. Study 012's tree is NOT read: a two-level walk would make this freeze depend on a tree two studies away. **(4) THE LABEL RULE READS TWO TUPLES (§7 delta 6, ruling M-25).** `FREEZE_PINS` loses `codex.model` and is seventeen members; `DESIGN_TIME_PINS` is new and holds `model` and `reasoningEffort`, both resolved by the pre-pilot sweep BEFORE the freeze. The move is not a relaxation — `label_pin_state()` reads both and a null in either labels the run PILOT — and the ONE exemption is one value and one label wide: `SWEEP_EXEMPT_PINS = ("reasoningEffort",)` under `SWEEP_LABEL`, with an UNKNOWN label context REFUSED rather than treated as "no exemption", because a typo that silently buys an exemption is the failure the argument exists to prevent. `tests/test_pins.py` drives every pin of both tuples and both directions of the exemption. **Not carried:** nothing. 019's module was itself a partial port and what it left behind in Study 012 is recorded in 019's own table, not re-litigated here |
| `harness/leak_tokens.py` | `5573f712eb89bd341862198f4e19fa58f1d7af4f69d269c1753ae66b39026c0c` | `harness/leak_tokens.py` | `21763f8ae76bbcce06507b17c387a60fe17b5ea5cdd133123e9b7ed70dae54d3` | **re-pointed.** `INSTRUMENT_TOKENS` names BOTH study titles (020's own, and 019's — 020's stimulus IS 019's bytes) and `WRAPPER_NAME_TEMPLATES` moves to `s020-…` with the wrapper |
| `harness/make_manifest.py` | `f30beaa3b186d29d7ddacb3e78d1ea3c30dcd6110fb9c8b193383811caeeb90d` | `harness/make_manifest.py` | `df90e935f9e8d766955950f99f4702621add0c7858546ef8c3a0a7246f1f545d` | **BOTH LINES' CHANGES, merged.** *From the apparatus port:* **§7 delta 11.** `CORRECTION-TARGETS.md` leaves the covered set by named constant and its pre-freeze obligation moves to `UNCOVERED_PRE_FREEZE_DOCUMENTS`, which `--freeze` refuses on. *From the sweep-driver line:* **complete port, FOUR registered differences.** Carried whole: ADR 0004's exact-set construction; `EXCLUDED_DOCUMENTS` as a MAPPING of path to reason with all five named exclusions (`DEVIATIONS.md`, `README.md`, `PREREG-REVIEW.md`, `harness/ADVISORIES.md`, `harness/PINS.json`) and R3-1's argument for each; `EXCLUDED_ARTIFACTS`; the one-level globs over `harness/*.py`, `harness/*.sh`, `harness/e4lib/*.py` and `harness/tests/*.py`; `pending_documents()`/`pending_payload_sets()`/`pending_pins()` and the `--freeze` refusal on each (R5-6); `tracked_bytecode()` and `tracked_paths()` with R10-2's fail-closed `IndexUnreadable`; `payload_closure_problems()` and `expected_payloads()` (R6-5); the reviewer-set closure and `reviewer_load_problems()` (R7-8, R8-2); `grid_assertion_problems()` (R8-8); `prior_attempt_problems()` (R9-2) and `prior_authoring_problems()` (R10-1). **(1) `REGISTERED_DOCUMENTS` IS THIS STUDY'S SET.** Kept: the preregistration, the policy prose, the gold suite, both mutant manifests, both reference documents and both reference payloads, the off-gold certificate, `harness/PORTS.md`, `CORRECTION-TARGETS.md` and the two `verification/` documents. **Added, and both are `GATE(pre-freeze)` obligations 020's own registration declares** — R7-9's lesson applied at the moment the obligation is written rather than when it lands: `harness/POWER-PRESENCE-IDIOM.md` (§3.2's power analysis, which decides whether the guard is registered at all) and `calibration/derive_floor.py` (§2a.4's committed threshold deriver, sealed before the pilot runs). **Added, and new in kind:** `design/RULINGS.md`, `design/BRIEF.md` and `design/PANEL-FINDINGS.md`, because §0.1 makes the design record an AUTHORITY over this registration — "where this document and the brief disagree, the rulings govern" — and a document that governs the registration is a document whose bytes must not move after the freeze. Study 019 had no equivalent: its design record settled nothing its preregistration then deferred to. **(2) `calibration_problems()` IS NEW, and it is a PERMISSION and a REQUIREMENT in one function** (§"The freeze and the primary attempt", 019's D-2). PERMITTED: `calibration/` is outside `prior_authoring_problems()`'s reach by construction, because that gate derives its paths from `batch.slot_path()` under `batch.ARMS_ROOT` and the calibration driver writes under `batch.CALIBRATION_ROOT` — a structural separation, not an exception list. REQUIRED: at the freeze the pilot must have RUN, so an absent subtree or one holding no pilot label REFUSES, which is the half a bare permission would have dropped. It joins `freeze_gate_problems()`, so `--check` reports it, `--freeze-gates` runs it and `--freeze` refuses on it. **(3) The head constants `RESULTS_DIR`/`PRIMARY_ATTEMPT_ROOT` are joined by `CALIBRATION_ROOT`**, asserted equal to `batch.CALIBRATION_ROOT` by `tests/test_manifest.py` rather than spelled twice. **(4) `SWEEP_ROOT` IS NEW** (§2.1), asserted equal to `batch.SWEEP_ROOT` the same way — and it is PERMITTED WITHOUT BEING REQUIRED, which `CALIBRATION_ROOT` is not. The permission is the calibration root's structural one: `prior_authoring_problems()` derives every path it refuses from `authoring_state_paths()`, which walks `batch.slot_path()` under `batch.ARMS_ROOT`, so a tree outside `arms/` is outside that gate by construction and needs no exclusion entry. There is deliberately NO `sweep_problems()` beside `calibration_problems()`: §2a registers the PILOT as a freeze precondition and nothing registers the sweep's TREE as one, so a freeze that refused while `sweeps/` was absent would be this module legislating a gate no section states. `tests/test_manifest.py::test_a_sweep_tree_does_not_trip_the_prior_authoring_gate_either` drives both halves and `tests/test_sweep.py` drives the gate in both directions |
| `harness/render_round_status.py` | `23a0720415c76417568b2a20c51fe8db64d78ff6e0697e6a36a7ba229e3800d0` | `harness/render_round_status.py` | `49763ccf5f38eac48215d28f82d1db8f589237dce54af5ba1cf7d7fc57df9ab1` | **BOTH LINES' CHANGES, merged.** *From the apparatus port:* **§7 delta 10.** The empty-of-rounds block is permitted and rendered; `SURFACES` narrows to `README.md` + `PREREGISTRATION.md`. Every other refusal ported unchanged. *From the sweep-driver line:* **complete port, TWO registered differences — §7's delta 10, exactly as it is registered.** Carried unchanged: every other refusal — duplicate members at every depth, closed object shapes, the closed verdict vocabulary bound to the review prompt's output line, the single-open-round rule, contiguity, and the marker-span reading — together with `--check`, `--write` and the rendered sentence's exact grammar. **(1) THE EMPTY-OF-ROUNDS BLOCK IS PERMITTED AND RENDERED.** 019's `parse_block()` refused a block registering ZERO rounds, because 019 first wrote its block after round 1 existed. 020 opens its review record BEFORE any round runs, so the zero-round state is a REGISTERED SHAPE rather than a malformed one, and the renderer produces "0 review rounds are on the record, 0 have returned a verdict — none has returned a verdict — and no round is open." The refusal it replaces is not deleted: an ABSENT block, a block that is not a list, and a block whose rounds are not contiguous from 1 still refuse, so "zero rounds" is distinguishable from "no record". **(2) `SURFACES` NARROWS TO TWO FRONT DOORS** — `README.md` and `PREREGISTRATION.md`. 019's third was `design/POLICY-DRAFT.md`, and 020's policy prose is ported FROZEN rather than drafted here (delta 10, and `harness/PINS.json`'s `policyProse` note), so a third front door would render a status sentence into a document this study does not author. **The first act of the port is `--write`**, which replaces the preregistration's hand-written status sentence with a rendered one — the failure mode ADR 0005 registers against, tolerated in the draft only because the renderer did not yet exist in this tree, and closed here |
| `harness/score.py` | `ddced312b2c4ae9ee67d491799066d24abbced6acea75da19056bdbcf03f5d6a` | `harness/score.py` | `41aa5f2e8128b4978b407c70d2d0a972d50bf26a050adf0216b318cbe4762cd7` | **BOTH LINES' CHANGES, merged.** *From the apparatus port:* deltas 1, 2, 4 (§7): survivor-vector write-time refusal, no-threshold cuts machinery, ownPolicyIdentity as a second named relation emitting E6. *From the sweep-driver line:* **complete port, THREE registered differences, and the single-publisher discipline is unchanged.** Carried whole: the argument surface, `integrity.verify()` as the first study-local call, the attempt record, the population rule reading `batch.CODE_PARTITION`, the ordered-codes and terminality machinery with `validate_shortfall()`/`verify_shortfall()` read from the driver rather than re-spelled, the fixed A−C-then-A−B sequence (R3-8, `registered_family()`'s now — `registered_contrasts()` does not exist), the E1/E2/E3/E4/E5 aggregations, the reviewer-set surface, `fill_intervals()`'s settlement of every inferential quantity behind the ordered rule (R2-12, R3-8), the rendered report's refusal to print anything inferential below a failed gate (R1-14), and the rule that no output embeds a timestamp or an absolute path. **(1) THE SURVIVOR-VECTOR SCHEMA (§7 delta 1, §5.2).** Every one of the FIVE sites that wrote a kill block now writes the same validated shape. Two of them wrote the literal `{"killedPaired": 0, "paired": n}` — a block with no survivor member and no `caseCount`, which is the pair of defects §5.2's definition 4 names and which produced exactly the same six 019 runs under both. Three called `e4lib.kill_rates({}, …)`, whose empty `survivorsPaired` with `killedPaired: 0` is BYTE-IDENTICAL to a suite that killed everything — the collision that scored 019's `run-025` and `run-046` a perfect 33/33 having killed nothing, and that moves the group-level ITT A−C contrast by 0.0526. All five now call `e4lib.unevaluated_kill_block()` or `e4lib.kill_rates(..., evaluated=ok)` and pass the result through `e4lib.validate_kill_block()`, which REFUSES the ambiguous shape at write time. `caseCount` is emitted for every admitted run with a suite and is 0 for a suite that parses to no cases. **(2) TWO IDENTITY RELATIONS, NAMED SEPARATELY (§7 delta 4, M-13).** `identityPass`/`identityFailures`/`identityFailureCount` become `referenceIdentityPass`/`referenceIdentityFailures`/`referenceIdentityFailureCount` — the 019 control, unchanged in behaviour and now unambiguous in name — and `ownPolicyIdentity` is a new per-run RECORD carrying the suite's score against the run's OWN authored policy. `own_policy_identity_block()` publishes E6 per arm together with the composition of the conjunction population 020 did NOT register (§1.2, §11.10). **It gates nothing**: no decision row, no control gate and no contrast reads it, and `tests/test_score_e4.py` asserts that as a property of the source rather than as a sentence. `artifactPath` joins `suitePath` and `scoredCases` in the set of members stripped before publication, because E6 needs the run's own policy on disk and must not publish where it sat. **(3) THE ADMISSION LAYER'S NEW CODE** reaches the scorer for free, because the scorer reads §1a's partition from `batch.CODE_PARTITION` and never spells a code: a run the presence-idiom detector flags is an AUTHORING outcome, stays in every ITT denominator, and scores zero. **MERGE NOTE, superseding a stale clause.** An earlier revision of this cell closed with "DELIBERATELY NOT CHANGED: the τ machinery" and "neither has landed" — written when it was true, carried past the union that made it false. Deltas 2 and 5 ARE landed in these bytes (`harness/SCAFFOLD.md` items S1, S2 and S4; the delta table below says all thirteen): no τ, no integer cut, no `highKill` member anywhere in this file, `contrast()`/`registered_contrasts()` replaced by `registered_family()` handing the per-arm records to `e4lib/family.py` in the same registered A−C-then-A−B sequence (R3-8), and the report prints the family table and no high-kill section. A register that calls a landed thing outstanding is the defect class this program hunts, so the correction is recorded here rather than silently rewritten |
| `harness/tests/conftest.py` | `5ff1a90ab864b4fe61c3ad618a050bee9803746a8c8b930677564e84d25cc13e` | `harness/tests/conftest.py` | `a892d1a04a7887142748de459265fdfa4287f97e40ebe50ae39533a2655c981a` | ported by digest, byte-identical to 019 |
| `harness/tests/test_batch.py` | `731749aa0daf365ce9ca98ae116e73a93da0c55be5b79e63c26626bd96c34d07` | `harness/tests/test_batch.py` | `4e7bcd5994c8bee5585da7adc9e39a9ad4280e9c71d9574947d2d6ba22988917` | **BOTH LINES' CHANGES, merged.** *From the apparatus port:* rebuilt for 020's registered surfaces (the delta owning its subject; see §7). *From the sweep-driver line:* the surfaces §2.1's pre-pilot effort sweep and §7 delta 6's label rule add |
| `harness/tests/test_census_replication.py` | `65c417fa4bbf754bc54da8e9d0943075874f4d736d4d7df3e877c6c1fd70385e` | `harness/tests/test_census_replication.py` | `65c417fa4bbf754bc54da8e9d0943075874f4d736d4d7df3e877c6c1fd70385e` | ported by digest, byte-identical to 019 |
| `harness/tests/test_design_regeneration.py` | `d85d169f3e41d81f77617078ebdc971e1edfa41d45b11db98578e3efee2d490a` | `harness/tests/test_design_regeneration.py` | `6a544e2bfddbd648ed03bffaacfaaf43259a389cdd04be88da340c6e3103ece6` | ported by digest, byte-identical to 019 |
| `harness/tests/test_grid_gate.py` | `256be828f023e3b991b1a0302110797257515cf15772cec9edae4224115f6bbf` | `harness/tests/test_grid_gate.py` | `256be828f023e3b991b1a0302110797257515cf15772cec9edae4224115f6bbf` | ported by digest, byte-identical to 019 |
| `harness/tests/test_leak_tokens.py` | `2ad01b4228fc8367d3e0ec6fccca6e8228eb622fda7807d5d0ae914b66459e1c` | `harness/tests/test_leak_tokens.py` | `bab813b2a5e76cd5ac3afcca92c7a64ff7dfc51e60be3976cbb02672a11bcb56` | ported by digest, byte-identical to 019 |
| `harness/tests/test_manifest.py` | `753bdd4287c7720c148e99bcd10f399ee5111d336171be865f4df01adf7bfdf1` | `harness/tests/test_manifest.py` | `385ffdc82c864573f22dd74edf21cef60edd1c2c8b043fa4871867d41aece967` | **BOTH LINES' CHANGES, merged.** *From the apparatus port:* **§7 delta 11's asserting tests**, including the exclusion asserted WHILE the file is absent. *From the sweep-driver line:* the surfaces §2.1's pre-pilot effort sweep and §7 delta 6's label rule add |
| `harness/tests/test_partition.py` | `1d3541d5a37a55ec0ddc98c400a9d4fa8465aed22fa1408eb7f6fd48ecb42fce` | `harness/tests/test_partition.py` | `104f288207c91cc81ae3c0010f9fd674da677443107fc55646b25350d65c4733` | **BOTH LINES' CHANGES, merged.** *From the apparatus port:* rebuilt for 020's registered surfaces (the delta owning its subject; see §7). *From the sweep-driver line:* the surfaces §2.1's pre-pilot effort sweep and §7 delta 6's label rule add |
| `harness/tests/test_pins.py` | `af927a517fabfb1a25c8141189128817e9b784648206b0e0d16ed65832ad4c14` | `harness/tests/test_pins.py` | `19bf97ca6d92deaf48961f4a2d637bb1f4617db2307cea00b0c49b023cc37817` | **BOTH LINES' CHANGES, merged.** *From the apparatus port:* rebuilt for 020's registered surfaces (the delta owning its subject; see §7). *From the sweep-driver line:* the surfaces §2.1's pre-pilot effort sweep and §7 delta 6's label rule add |
| `harness/tests/test_ports_chain.py` | `279f5c250e0aeff10c910dd3cd27331805e797be423ab02ba2a14327cac22cad` | `harness/tests/test_ports_chain.py` | `04407a4d5a3a2acecf79f8ef2a6ca01ff47d0d8d59111b9f32fe1396e7bdb8a4` | **BOTH LINES' CHANGES, merged.** *From the apparatus port:* rebuilt for 020's registered surfaces (the delta owning its subject; see §7). *From the sweep-driver line:* the surfaces §2.1's pre-pilot effort sweep and §7 delta 6's label rule add |
| `harness/tests/test_prereg_currency.py` | `aed98a18e1015f305cab9f8c344c7378a50ad56d6c75a2443dfba60089f6bbf0` | `harness/tests/test_prereg_currency.py` | `d924dde6d8429083aa0860f46666ccc95bf2b4f5d84243a0564901edcda0bdf2` | **BOTH LINES' CHANGES, merged.** *From the apparatus port:* **§7 delta 10's asserting tests** added. The rest of this file still reads Study 019's prose and is HANDED OFF, not ported clean. *From the sweep-driver line:* the surfaces §2.1's pre-pilot effort sweep and §7 delta 6's label rule add |
| `harness/tests/test_schedule.py` | `fcdfd6e535aafa649ff3c49cfd3d6886bf9f8501de27f50861b21728d4f3cd2c` | `harness/tests/test_schedule.py` | `257df54d7dd9d545e86a85a645c8542b3bbae703498cd47c87572869fbebccb2` | rebuilt for 020's registered surfaces (the delta owning its subject; see §7) |
| `harness/tests/test_score_admit.py` | `497b4ec0b9a627e19356859b6005a38b4199a87acac67b4c47e1c828b816342d` | `harness/tests/test_score_admit.py` | `852c2ae39690a62d5d84f4f5259370125f52ed1eefba043f12dd2a4d1bc17635` | **BOTH LINES' CHANGES, merged.** *From the apparatus port:* ported by digest, byte-identical to 019. *From the sweep-driver line:* the surfaces §2.1's pre-pilot effort sweep and §7 delta 6's label rule add |
| `harness/tests/test_score_attempt.py` | `3d0691fa58670d63575e879a3c19909799916440049a9b007a159278967199bf` | `harness/tests/test_score_attempt.py` | `39fa235b3b071bb80614afaff78ed469622ba88ce1d7f665e4e34c8111294ca3` | **BOTH LINES' CHANGES, merged.** *From the apparatus port:* rebuilt for 020's registered surfaces (the delta owning its subject; see §7). *From the sweep-driver line:* the surfaces §2.1's pre-pilot effort sweep and §7 delta 6's label rule add |
| `harness/tests/test_score_capabilities.py` | `578d3d34a4ac39e0fcf878671541f583024fc99a3e6a50fcdefb9501fcb830d2` | `harness/tests/test_score_capabilities.py` | `578d3d34a4ac39e0fcf878671541f583024fc99a3e6a50fcdefb9501fcb830d2` | ported by digest, byte-identical to 019 |
| `harness/tests/test_score_census.py` | `44d1814988dd382b414362805ece3046e97891c4ea2189b8b75f5fdf6e2c9bb9` | `harness/tests/test_score_census.py` | `df1132035dd006a6ffc17e8c5aaac5e9bdf9e65f52ee68acb64497bd60044774` | rebuilt for 020's registered surfaces (the delta owning its subject; see §7) |
| `harness/tests/test_score_decision.py` | `7a636d283853ce651f6ac2dbd63bad7cdee629e134023614a4ec163c307d8792` | `harness/tests/test_score_decision.py` | `5ed11bd372da779e901d47392dc6dc1d0434c772d195e297fa7b3c7b5adddeb9` | rebuilt for 020's registered surfaces (the delta owning its subject; see §7) |
| `harness/tests/test_score_domain.py` | `89f5acd0e74d037d72529b70234ffed88691fccafaaeef0d8b4cc6e14252c3cb` | `harness/tests/test_score_domain.py` | `89f5acd0e74d037d72529b70234ffed88691fccafaaeef0d8b4cc6e14252c3cb` | ported by digest, byte-identical to 019 |
| `harness/tests/test_score_e4.py` | `2940605e88894ba449a9ca9984f8a86cde4b795ce19ce404247a9771d3187e88` | `harness/tests/test_score_e4.py` | `32ad008918b6e405178ca1a9245ad7af54ce1787e60cb94c06c2826300c22c17` | rebuilt for 020's registered surfaces (the delta owning its subject; see §7) |
| `harness/tests/test_score_engines.py` | `30c0c28975762f8088c2bb20dd4e642cf09c7803b4f051e8d3e1d5a095b85d8d` | `harness/tests/test_score_engines.py` | `30c0c28975762f8088c2bb20dd4e642cf09c7803b4f051e8d3e1d5a095b85d8d` | ported by digest, byte-identical to 019 |
| `harness/tests/test_score_extract.py` | `93f52695a38a4cff9880cab278efe04f8f080cc169a160e3b8b08070a26bbeb1` | `harness/tests/test_score_extract.py` | `93f52695a38a4cff9880cab278efe04f8f080cc169a160e3b8b08070a26bbeb1` | ported by digest, byte-identical to 019 |
| `harness/tests/test_score_pipeline.py` | `ac622c003e3c04534337298ce392b81160c192e5c9addd75bc76565f29c49761` | `harness/tests/test_score_pipeline.py` | `0d577ae63db4730fa42bb82017d1f753cc91edca06f6a459bf58168ab7e3bb78` | ported by digest, byte-identical to 019 |
| `harness/tests/test_score_publication.py` | `188acebd75bbd31d7e2b38fa1fc243dcfa5074c559d1efb08b68a23ad842eebc` | `harness/tests/test_score_publication.py` | `2ec98dd6bd0d33b7ecc064dbd44fce4d0d6e1c88aa08a5f6d86c80df7cfe3c88` | rebuilt for 020's registered surfaces (the delta owning its subject; see §7) |
| `harness/tests/test_score_reviewer.py` | `771763d8e0cbea21ffa44aa45fe0b79111f1fc360f75f9601e7a86c6fa22c47c` | `harness/tests/test_score_reviewer.py` | `072776e64289654035fe80c90aea1538fca3d888dcefc8e9c51d5c72061c6aa7` | ported by digest, byte-identical to 019 |
| `harness/tests/test_score_stats.py` | `5c4e5a3c62d7db662b80e5afe75608e5b8cb9eebcaca630f18b40aecc4dee973` | `harness/tests/test_score_stats.py` | `928f2102a15e67dc1062a82e5a61db517030f15e9cc5a412821ae812c8543042` | rebuilt for 020's registered surfaces (the delta owning its subject; see §7) |
| `harness/tests/test_transcript_binding.py` | `9a6bbeee4444682647a02f76c88c2862b19fcc9d03b06c49427e6a18889a75ee` | `harness/tests/test_transcript_binding.py` | `9a6bbeee4444682647a02f76c88c2862b19fcc9d03b06c49427e6a18889a75ee` | ported by digest, byte-identical to 019 |
| `harness/transcript_check.py` | `17ab4655c703feb19b9df53096e71f55125d3178404ae9e8a4a96596f01f5ce7` | `harness/transcript_check.py` | `53b16836007aab006c1f4a1caa035a7566e60fb5692eac36f757afb378713895` | port note added to the module head; no code change |

**What "changed" means in the last column.** `ported by digest, byte-identical
to 019` is exactly that: `sha256(source) == sha256(destination)`, and it is not
written for a file whose two digests differ. Every other cell names the
registration that forced it. A cell that opens **BOTH LINES' CHANGES, merged**
is a file where the apparatus port and the sweep-driver line each landed a
registered change and the merge kept both: the change list carries each one with
its own attribution rather than choosing between them.

## The registered artifacts — bound to the same lock, deliberately NOT rows

`PREREGISTRATION.md` §4.1 ports the gold bytes, both mutant corpora, both
references, the frozen policy prose, the off-gold certificate and the two
verification documents **by digest**. They are not rows above, and that is a
decision rather than an omission: 019's lock already publishes a digest for each
of them under the same study-relative path, so a second transcription of those
digests into a table here would be a copy that can drift from the lock it claims
to quote. `integrity.verify_ported_artifacts()` compares this tree against the
lock directly, in **both** directions over the payload trees — a mutant 019's
lock names and this tree does not carry, and one this tree carries that 019's
lock does not name, are the same defect and both refuse.

| artifact | 019-side authority |
|---|---|
| `policy/POLICY.md` | `c4a533cab4dc6b6fa5e5f3b92d999ebf130cfbfaa5811ace49087c16612173bc` |
| `gold/GOLD.json` | `1ca1e5dd86fc2c7766db126cc51a792ab1a9aa5c8c6831321c932ad249361ab8` |
| `mutants/MANIFEST-jps.json` | `5f553baa68a50daefc046823e0488ff6831d083969663cc5d125f5eddd212b6d` |
| `mutants/MANIFEST-rego.json` | `06cb8d2f46a3833253d1eb6dc314c5ab847412061f378dbfb19facfa1f29225b` |
| `reference/REFERENCE-A.md` | `0af62377357adc54e03b45f90724414ce67bad6414a2d0307cab2eb77a5354eb` |
| `reference/REFERENCE-B.md` | `21f9ae1906a462c398bd969d3da792f55aef834651e26d38b7b29da53a90dec7` |
| `reference/refA/pack.json` | `db9776070fbf5e193443ffb1f371b2524b4662f0877868306323b5c9e3701853` |
| `reference/refB/policy.rego` | `1f2e1ad1d423240dd262852f19057a8e906387d5a1b71db8b8a15bc010fc12e2` |
| `controls/off-gold-equivalence.json` | `66203266741fd2c769c794469d8050e732ac2c4e1b4df2e462f8e59055f3b6f3` |
| `verification/V7-COMPLETENESS.md` | `6a04d88417f632e634c9c6963c4bd97dcbe9f420c9e2e29a22cd3c401b2a7894` |
| `verification/V8-ASYMMETRY-LEDGER.md` | `b77d56b51ab1b8d55395c4215f1d18b8530d5094d25864345c36374cc308d750` |
| `mutants/jps/*.json` (183 payloads, each hashed individually) | `(019's lock, file by file)` |
| `mutants/rego/*.rego` (185 payloads, each hashed individually) | `(019's lock, file by file)` |
| `arms/A/PROMPT.txt` | `9d8b4f41c6cbb1c2ff5216c7758ad8f25d274802b5f07b2f54ac14d19e85d83a` (019's REGISTRY, `arms.A.promptSha256`) |
| `arms/B/PROMPT.txt` | `074c5b4a9837e887846f140bf45ca481956aea672d05e1ee49e7ed559f99b055` (019's REGISTRY, `arms.B.promptSha256`) |
| `arms/C/PROMPT.txt` | `576a8e8e6c890f2cb28100621a53438c09de5e9970a480f7997ebf096203567c` (019's REGISTRY, `arms.C.promptSha256`) |

The three arm prompts are the one class bound to 019's **registry** rather than
to its lock, because 019's manifest does not cover `arms/` and its registry pins
each prompt's digest under the member the call wrapper's own prompt-digest gate
reads. Binding them to the lock would have bound them to nothing.

## Carried UNPINNED, said plainly

`design/` is carried and is carried **without a digest binding**: Study 019's
manifest covers no path under `design/`, so the recorded port commit above is
the whole of that carry's source-side authority. This is the same shape of row
019 had for `harness/make_manifest.py` from Study 014, and it costs the same
thing — cross-vendor review of the diff is what covers it. What is carried:
`design/gold/`, `design/mutants/`, `design/reference/`, `design/prompts/`,
`design/cleanroom/`, `design/POLICY-DRAFT.md`, `design/POLICY-v0.md` and
`design/TOOLCHAIN-NOTES.md`.

## Reconciliation order, and why this file moves first

`harness/SCAFFOLD.md` step F6 carries Study 019's rule verbatim: **`PORTS.md`
before `PINS.json`, always — the registry pins the ports table and never the
reverse.** The order is linear and one-directional (ADR 0005):

```
the ported files      ->  this table's destination cells
this table            ->  harness/PINS.json's ownPorts.sha256
harness/PINS.json     ->  (unpinned; the manifest may not cover it)
covered files         ->  harness/STUDY-MANIFEST.sha256   (regenerated LAST)
the manifest          ->  harness/PINS.json's studyManifest.sha256  (at the freeze)
the freeze commit     ->  harness/PINS.json
```

Between a harness edit and the regeneration of this table
`integrity.verify_chain()` REFUSES — which is the correct state, not a broken
one: `harness/score.py` files that refusal as a pipeline problem and the attempt
is pipeline-invalid, so nothing is adjudicated against an unpinned ports table.

## The registered deltas, and where each one lives

`PREREGISTRATION.md` §7 registers thirteen deltas. **All thirteen have landed**
— the apparatus port carried the ones that rewrite the analysis, the
sweep-driver line carried the ones that rewrite the calling surface, and this
table names which file holds each and which test enforces it.

| delta | where it landed | enforcing test |
|---|---|---|
| **1 — the scorer's survivor-vector schema; the token collision is fixed** | `harness/e4lib/e4.py` (`NOT_EVALUATED`, `survivorVector`, `require_survivor_schema()`), `harness/score.py` (every kill-block write site, and `caseCount` for every admitted run with a suite) | `tests/test_score_e4.py`, driven with the mutation check §7 requires |
| **2 — no threshold** | `harness/e4lib/e4.py` (τ, the integer cut and `highKill` are gone; the per-language paired denominators and lattices stay), `harness/e4lib/stats.py`, `harness/e4lib/decision.py` | `tests/test_score_decision.py` asserts no registered decision path reads a cut, by name |
| **3 — the new admission code** | `harness/e4lib/presence_idiom.py` (new), `harness/e4lib/admit.py`, `harness/batch.py`'s `CODE_PARTITION` and `AUTHORING_CODE_ARMS` | `tests/test_partition.py` (the partition diff, extended to §1a's third column), `tests/test_score_presence_idiom.py` |
| **4 — the `ownPolicyIdentity` invocation** | `harness/e4lib/e4.py` (the two named relations), `harness/e4lib/engines.py`, `harness/score.py` | `tests/test_score_e4.py`, including the non-gating property |
| **5 — the eighteen-member family scorer** | `harness/e4lib/family.py` (new), `harness/e4lib/stats.py` (BCa and the two permutation schemes), `harness/e4lib/decision.py`, `harness/score.py`'s `registered_family()` | `tests/test_family.py`, `tests/test_score_publication.py` |
| **6 — `registeredLabelRule` restated** | `harness/integrity.py` (`DESIGN_TIME_PINS`, `SWEEP_EXEMPT_PINS`, `label_pin_state()`), `harness/batch.py` (`require_design_time_pins()`, the call-side half), `harness/PINS.json` | `tests/test_pins.py`, pin by pin and both directions of the sweep exemption |
| **7 — the schedule re-derived at the registered round count** | `harness/batch.py` (`_registered_batch_shape()`, `derive-schedule`; the file holds no round count of its own), `harness/PINS.json`'s `batch` block | `tests/test_schedule.py`, re-running the search at the registry's own N and at others |
| **8 — the freeze gate's `calibration/` rule** | `harness/batch.py` (`CALIBRATION_ROOT`, `calibration_freeze_problems()`), `harness/make_manifest.py` (`calibration_problems()`) | `tests/test_manifest.py`, each half driven against the other's tree |
| **9 — the fresh sealed reviewer set** | `harness/PINS.json`'s `reviewerMutantSet` (019's is SPENT), `harness/make_manifest.py`'s reviewer-set gates | `tests/test_manifest.py` |
| **10 — the empty-of-rounds review record** | `harness/render_round_status.py` (the zero-round block parses and renders; `SURFACES` narrows to two front doors) | `tests/test_prereg_currency.py::test_the_empty_of_rounds_block_parses_and_renders` |
| **11 — `CORRECTION-TARGETS.md` leaves the covered set** | `harness/make_manifest.py` (`UNCOVERED_PRE_FREEZE_DOCUMENTS`, and `--freeze` refuses on it) | `tests/test_manifest.py`, including the exclusion asserted WHILE the file is absent |
| **12 — `design/pilot/pilot_run.py` deleted, not ported** | absent from this tree by decision; the pre-freeze pilot runs through `harness/authoring_call.sh` and `harness/batch.py` under the calibration label | `tests/test_manifest.py`'s payload-closure gate; **What does NOT carry** below |
| **13 — the D-1 smoke restatement** | 019's `harness/tests/E2E-SMOKE.md` is 019's evidence and does not carry; 020 writes its own | **What does NOT carry** below |

**§2.1's pre-pilot effort sweep is not a §7 delta and is registered separately.**
`batch.py sweep` is the mode that runs it — 3 settings × 3 arms × 3 runs, the
derived 27-call cap, the 72 h budget, the arm-interleaved A-first schedule,
`SWEEP_ROOT` outside `arms/`, M-24's witness resolution as step zero — and
`harness/authoring_call.sh` carries the effort seat it needs. The flag's
spelling is READ FROM THE REGISTRY (`codex.reasoningEffortFlag` and
`codex.reasoningEffortConfigKey`) rather than written into the shell, because
the resolution against the pinned binary found that `codex exec --help` at
codex-cli 0.145.0 names no reasoning-effort flag at all and the only spelling
this build accepts is the config override `-c model_reasoning_effort=<tier>`.
`tests/test_sweep.py` drives all of it.


## What does NOT carry, and why

| not carried | why |
|---|---|
| `controls/reviewer-mutants/` | §4.3: 019's reviewer set is **spent** — first executed at 019's primary attempt. 020 registers a **fresh sealed set**, authored during review rounds. 019's is kept only as a published comparison. |
| `design/pilot/pilot_run.py` | §7 **delta 12**, and §2a.2: 020 runs one driver, and a second pilot driver in the tree is a second thing that can make a call. |
| `design/pilots/` | §2a.1: 019's pilot cannot be reused — the differences are five, not three — so 020 runs its own (C1–C5). Carrying 019's pilot outputs would put another study's calibration data where this study's belongs. |
| `harness/tests/E2E-SMOKE.md` | 019's end-to-end smoke transcript is 019's **evidence**. 020 writes its own; §7 **delta 13** restates the part of it that failed. |
| `controls/opa-capabilities.json` | 020's capabilities file is generated from the pinned binary and the registered denylist **at pin time** (§2), not copied. |
| `arms/*/authoring/`, `arms/BATCH.json`, `results/` | 019's batch and its scored attempt. §1a registers 020's prospective content as its own post-freeze runs, and `make_manifest.py`'s freeze gates refuse a tree that carries any of it. |
| Study 019's `design/pilot/pilot_run.py`, kept out of the tree | §7 **delta 12** and §2a.2: 019's pilot driver called codex with no `env=`, no `-m` and no `--ignore-user-config` — the five recorded differences §2a.1 enumerates — and a second calling path is what made 019's pilot measure a compute condition the registered batch never reproduced. |
| Study 019's `arms/`, `results/` and `reviews/` trees | 019's 149 retained slots, its primary attempt and its twelve review rounds are 019's record. They are READ by this study exactly once and for one registered purpose — §3.2's pre-freeze power analysis over the 76 retained arm-B/C policies, published in `harness/POWER-PRESENCE-IDIOM.md` — and nothing is copied. |
| Study 019's `DEVIATIONS.md` entries D-1…D-4 | 019's deviations are **already in the ported bytes** — D-1's stdin redirect and D-2's gate re-seating are what this port takes. The entries themselves are 019's record. |

## Assembled from this study's own work

Nothing yet, and the empty section is deliberate rather than omitted. Study 019
carried five modules assembled from its own `design/` prototypes and recorded
their as-assembled stamps here. Study 020 assembles none: it carries 019's
`design/` tree unpinned (above), and the two modules that are genuinely new —
`harness/e4lib/presence_idiom.py` and `harness/e4lib/family.py` — were written
against the registration, the pinned binary's own AST and §5.2's own text rather
than from a prototype, and each says so in its own docstring.

## The port's first act

`PREREGISTRATION.md` §7 delta 10 registers it: `harness/render_round_status.py
--write`, run over a review record that registers **zero** rounds, replacing the
front doors' hand-written status sentence with a rendered one. Run at the port,
it reported `nothing moved` — the hand-written sentences were already
byte-identical to the render — and `--check` returns 0. That is the delta doing
its job rather than a step being skipped: 019's parser would have **refused** the
same record, and the mutation check in
`harness/tests/test_prereg_currency.py::test_the_empty_of_rounds_block_parses_and_renders`
is what shows it.
