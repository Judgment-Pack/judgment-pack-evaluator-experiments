# Ports — what Study 019 takes, from where, and what changed

Study 019 runs one authoring call three ways and compares what each
representation's accompanying test suite pins down. The machinery it counts
with is inherited as **bytes**, not as descriptions, through a two-level chain
(PREREGISTRATION.md §7): this file records every port, its digest on both
sides, and exactly what was changed. `harness/integrity.py` machine-reads the
table below and binds each row **to the authority that row actually has**
before any call is made and before anything is scored.

The chain, with every link a pinned digest including both ends:

```
this file                            (pinned in harness/PINS.json at port time)
    -> Study 012's harness/PINS.json     cff265e7…  (pinned in harness/integrity.py and in PINS.json)
       Study 012's harness/PORTS.md      e754a583…  (the digest 012's OWN registry pins for it,
                                                     not one this study chooses)
```

The port was taken at commit

```
commit 019c95be9e86c575878015954dfec17e4f84e683
```

The **six** files taken from Study 012 answer to **012's own PORTS.md
destination cells**, which is a stronger binding than a commit: 012 published a
digest for each of them and this study's source cells must equal it. The
seventh file (`harness/make_manifest.py`, from Study 014) is bound to that
commit and to nothing older, because Study 014 pins none of its own harness
sources — §7 states what that costs, and cross-vendor review of the diff is what
covers it.

**This is a PARTIAL port and the table says so per row.** Destinations that
carry a subset of their source's bytes say so in their own cell, and every
deferred piece is listed in `harness/SCAFFOLD.md` by name and by source line
range: a partial row is not a licence to defer silently, and the freeze cannot
happen while any of them is open. `harness/batch.py` is no longer one of them —
SCAFFOLD items D1–D8 and G1–G2 have landed and its cell enumerates them.

**One row can carry more than one source, and this table says where and why.**
`harness/integrity.py`'s `REQUIRED_PORTS` fixes the destination set at exactly
the seven files it names — the two scorer rows joined it when SCAFFOLD item M1
closed, and round 1's R1-20 found this sentence still saying five and still
saying "must grow", which is why `harness/tests/test_prereg_currency.py` now
reads the count out of the constant rather than out of a reader's memory — and
`verify_chain()` resolves a row's source-side
authority *by its destination* — so a second row naming `harness/batch.py` as
its destination refuses, whatever it names as its source. Four functions Study
012 kept in `harness/score_rates.py` are nevertheless carried into
`harness/batch.py` (`C7_OUTCOMES`, `session_identity()`, `collect_slots()`,
`c7_record_shape_problems()`), because each is a precondition of the CALLS and
this study's scorer did not exist when the driver needed them. Their
provenance — source path, source digest, and what changed — is therefore
recorded **inside the row that owns the destination** rather than in a row of
its own. That is a real limitation of the table's shape, stated here rather
than worked around silently: a round that wants `harness/score_rates.py` on its
own row has to widen `REQUIRED_PORTS`, which moves `harness/integrity.py`'s own
destination digest and is a change to a reviewed file, not a bookkeeping edit.

**Two authorities, not one.** A row in the table below is a CROSS-STUDY port:
bytes inherited from another study, bound on both sides. Code assembled from
THIS study's own `design/` prototypes is a different thing and gets a different
treatment — the prototype's path and sha256 are cited in the assembled module's
own docstring, and the module says which line ranges it carried. The design
prototypes are this study's working code and were run against the real engines;
they are not another study's published bytes, so a two-sided row would claim an
inheritance that does not exist. The five assembled modules and their
prototypes are listed under "Assembled from this study's design prototypes"
below.

## The table

| source | source sha256 | destination (in this study) | destination sha256 | changed |
|---|---|---|---|---|
| `transcription/authoring_call.sh` | `d8877f3d78af54a7c43b8c53571b76ac4e0d540048f57ddcdaa7826f3c6b3fee` | `harness/authoring_call.sh` | `08d5e8bddfe21049cdf645bd9fa3ce01ed1c027af68260e60bc63b3e12d8fc47` | **complete port, EIGHT registered differences** (four at the port, a fifth at SCAFFOLD G3, and three from round 1 — the count is stated here rather than left for a reader to recount, which is what round 1's R1-20 found stale). (1) three arms A/B/C and `s019-…` scratch, home and per-run binary names; (2) the **registered per-call timeout ceiling**: `timeout --signal=TERM --kill-after=<grace> <ceiling>` is the outermost thing the scrubbed environment runs, the ceiling and the grace are read from `harness/PINS.json` (`batch.callTimeoutSeconds`, `batch.timeoutKillAfterSeconds`) and validated **before** the call, `CALL.json` gains `timeoutSeconds`, `timeoutKillAfterSeconds` and `timedOut`, and a ceiling hit exits **12** — its own status, and its branch is the FIRST of the three refusal branches, ahead of the session-count one as well as the generic nonzero one, because a call terminated at the ceiling frequently produces no session at all and 012's ordering would have filed exactly those runs as `slot-shape`: both codes are APPARATUS, so no denominator moves, but the registered per-arm timeout rate is what a control gate reads and undercounting it would let a batch pass a cap it breached (verified against a stand-in study and a stand-in CLI: exit 12, `timedOut: true`, the ceiling and the grace stamped); (3) a **null registry model refuses**: the model is named by explicit flag at batch time and is null in the registry until then, and a null member reaches the shell as the string `None`, which `-m` would accept as a model name; (4) the wrapper lives in `harness/` rather than `transcription/` — `$STUDY` is the parent of the script's own directory, the same expression at either location, so the anchor and every guard built on it are unchanged. The prompt-digest gate is **carried, not new**: per arm, read from `arms.<ARM>.promptSha256`, refusing an unregistered arm id and another arm's bytes; only the accepted id set changes. Everything else is 012's byte-for-byte, including the resolve-before-create descent, the slot-path equality guard, the credential traps and the worktree repair. **(5) SCAFFOLD G3 — the scratch-path leak screen reads `harness/leak_tokens.py`'s `SCRATCH_TOKENS` instead of `transcript_check.LEAK_TOKENS`.** The policy half of that list is DERIVED from the stimulus slice of the frozen-candidate prose by three registered rules — the prose's own bold and backticked terms, its clause ids, and the threshold numerals of comparison sentences together with their spellings — and `leak_tokens.check_power()` requires the derived list to catch every witness sentence the SOURCE'S OWN MARKUP identifies while a scrambled list of the same size catches strictly fewer. What the wrapper screens with is the UNION of the derived policy vocabulary and the design-time INSTRUMENT vocabulary (jpack, the preregistration, the mutant machinery), so the list can only grow and the screen can only tighten; `leak_tokens.check_negative_corpus()` proves no derived token fires on any name this wrapper constructs, over every arm and every registered slot index. The screen's SITE, its refusal text and its exit status are unchanged, and no other line of the file moves. **(6) R1-4 — the POST-CALL PHASE and exit status 13.** The wrapper runs under `set -euo pipefail`, and its three post-call stages (the completion extraction, the `CALL.json` write, the context digests) are plain commands under it: a helper that raised killed the shell with the helper's own status 1, which the driver's table reads as "a pre-call refusal; nothing was called and no slot was left behind" — while the call HAD been made and the slot HAD been retained. The file now sets `POST_CALL=false`, installs `trap 'on_unexpected_error "$?" "$LINENO"' ERR` under `set -E`, and flips the flag and re-installs the trap on ONE line immediately after `set -e` is restored, so no command runs in the window between them; the handler exits **1** before the call and **13** after it, and the status set is closed at {0, 1, 10, 11, 12, 13} on every path this process takes by itself. The trap comes OFF for the call region and only for it (`trap - ERR` before `set +e`), because bash runs an ERR trap on any failed command WHETHER OR NOT errexit is set — verified here, not assumed — and leaving it installed would have turned every ordinary nonzero call and every ceiling hit into a wrapper error before the three refusal branches could read `$EXIT`. **(7) R1-5 — an author protocol violation is not this wrapper's failure.** Both post-call helpers parse the transcript with `transcript_check`'s whitelist, so a run in which the model used a TOOL refuses inside them; exiting non-zero on that would file the AUTHOR's failure under an APPARATUS code and delete from every denominator exactly the runs §3's no-tools instruction exists to catch. Each helper now re-raises only when `transcript_check.REASON_CAUSE` puts the refusal on the apparatus side, and leaves its output unwritten on an author-side one; the slot is otherwise whole and the driver's binding files it as `author-protocol-violation`. **(8) R1-5 — the prompt reaches the model BYTE-EXACT.** `PROMPT="$(cat FILE)"` strips every trailing newline, so the argv the model received was not the bytes the digest gate two lines above had just pinned, and §3.1 gate 2 — the transcript's user message EQUALS the arm's prompt bytes — could never pass for a prompt file ending in one. Nothing noticed because round 1 found that gate was never invoked for a scored slot; the header has claimed "the prompt passed byte-exact" since 010. The idiom is `PROMPT="$(cat FILE; printf x)"; PROMPT="${PROMPT%x}"`. Every one of the three is held by a test that runs the committed bytes through the real bash: `tests/test_batch.py::WrapperExitPaths` drives all six statuses end to end, including the two distinct post-call stages, and `TranscriptBindingAtTheSeal` holds (7) and (8) |
| `harness/batch.py` | `6ee3bf3e2b217257fe38976df4610461c9ed9866db485678348b3ad8036fdcf3` | `harness/batch.py` | `f321b6db57a6b7f4d6bca754ad1d092e8ea7bf5bf448c7832d37d875092abce2` | **the schedule core, the code partition and the whole calling half.** Carried and edited: the registered-call-order constants (012 lines 341–375) and `williams()`/`schedule()`/`schedule_entries()`/`slot_path()` (012 lines 515–616). Changed: `ARMS = ("A","B","C")`, so `POSITIONS` 3, `SEQUENCES` 6, `RUNS_PER_ARM` 50, `REGISTERED_SLOTS` 150, all derived and none transcribed; **the schedule re-derived for three arms** as eight whole blocks of the six Williams sequences plus a registered two-sequence tail (50 rounds, because 50 is not a multiple of 6), with `derive_order()` performing the exhaustive 720 × 30 search that establishes the registered order attains the arithmetic FLOOR of both spreads — exact balance being unavailable at 3 arms over 50 rounds — and `schedule()` refusing an expansion that is not at that floor; `balance()` added as the counters both the search and the harness test read; `CALL_TIMEOUT_SECONDS = 2700` and `TIMEOUT_KILL_AFTER_SECONDS`; `WRAPPER_EXIT_MEANINGS` extended with status 12; and `APPARATUS_CODES`/`AUTHORING_CODES`/`CODE_PARTITION` — §1a's partition as a named constant, built rather than written out so a code on both sides refuses at import. **The calling half is now carried too** — SCAFFOLD items D1–D8 and G1–G2, ported by copy-and-edit from the 012 line ranges SCAFFOLD names: `check_registry()`/`verify_ported_bytes()` (638–741), `preflight()`/`require_freeze()` (742–870), `invoke()`/`stamp_slot()`/`refuse_slot()` (988–1124), the slot files, `files_digest()` and `seal_slot()` (1125–1284), the ledger records, chain, prefix and `write_ledger()` (1285–1488), `verify_seal_of()`/`slot_outcome()`/`slots_on_disk()`/`reconcile_ledger()` (1489–1719), `run_batch()` (1720–1831), the golden capture (871–910 and 1832–2078), the isolation negative control (911–987 and 2079–2235), and the shortfall surface with `main()` (2236–2507). Changed, beyond the five above: **(6)** `require_freeze()` gates on the REGISTERED LABEL RULE — every freeze pin non-null via `integrity.study_label()` AND the preregistration digest — where 012 read one member, because Study 014's round 3 found a registered run reachable with only the preregistration digest filled; **(7)** the no-new-slots marker is `ATTEMPT_ROOT` (`results/primary-attempt-001`, the root the scorer refuses to overwrite) and not a `RESULTS.json`; **(8)** `WRAPPER_CODES` is DERIVED from `WRAPPER_EXIT_MEANINGS` rather than written out beside it, which is the third branch SCAFFOLD records as owed — status 12 cannot be mapped in one table and missing from the other; **(9)** the atomic-write temporary keeps 012's registered constant path `arms/BATCH.json.partial` and needs NO exclusion entry here, because ADR 0004's exact-set manifest reaches no byte under `arms/` — `tests/test_batch.py` asserts both halves rather than leaving the second to be assumed; **(10)** four functions are carried from Study 012's `harness/score_rates.py` (sha256 `f4d4463f081439f147a341bb38d8a6b709b3860f73f6f4e524234a180ec23336`, 012's own destination digest for it): `C7_OUTCOMES` verbatim, `session_identity()` verbatim, `collect_slots()` with `ScoreError` becoming `BatchError` and the five-arm prose generalized, and `c7_record_shape_problems()` verbatim — see the note above the table for why they have no row of their own, and note that `harness/score.py` must read all four from here exactly as it must read `CODE_PARTITION` from here; **(11)** `require_lawful_destination()` is rewritten for ADR 0004: 012 asked whether a destination lay inside a registered `freeze.excluded` TREE, this registry has no such member, and the rule is therefore computed from `make_manifest`'s own constants — a destination is lawful when writing into it cannot add a covered entry — with 012's device/inode `_identity_overlap()` fail-closed clause carried unchanged; **(12)** `STUDY_CLI_STANDIN` names a CLI when `--cli-override` does not, resolved once per command by `resolve_cli()` so preflight's digest gate, the invocation and the ledger header see one value — it removes no gate, and `tests/test_batch.py` asserts it refuses under the committed registry; **(13)** 012's `verify_chain()` over the ledger is renamed `verify_ledger_chain()`, because this module imports `integrity`, whose `verify_chain()` is the PORT chain, and two functions of that name over two chains in one namespace is a name a reader has to disambiguate every time; **(14)** the module keeps a `plan` subcommand — the command it had while the calling half was unported — because it is the one way to read the registered order without a registry, a wrapper or a call. Carried unchanged and named so a reader does not have to diff for them: the `__main__`-guarded safe-import-path and untracked-source tripwires (012 lines 214–272), which refuse today for SCAFFOLD item T3's reason. **Round 1 adds three changes, all in the counting integrity this row already owns.** **(15) R1-4 — the partition is EXHAUSTIVE and the status map is FAIL-CLOSED.** `WRAPPER_EXIT_MEANINGS` gains status **13** (`post-call-failure`), the wrapper's new post-call phase; `APPARATUS_CODES` gains **`preflight-refused`** and **`post-call-failure`**, both of which the driver could already emit and neither of which any partition named — `score.population()` excludes only the codes it recognises as apparatus, so a sealed, ledgered slot wearing an unnamed code went into every per-arm denominator as an ordinary authoring run scoring zero. `WRAPPER_CODES.get(status, "wrapper-error")` is gone from both of its call sites: `wrapper_code()` raises on any status §2 does not register, an import-time loop refuses if any value of `WRAPPER_CODES` is outside `CODE_PARTITION`, and `refuse_slot()`, `ledger_record()` and `slot_outcome()` each refuse a code the partition does not name — so the sentinel cannot be written into a slot, into the ledger, or read back out of one. **(16) R1-5 — the full transcript binding runs on every completed slot.** `transcript_verdict()` is the ONE entry point (the driver's here, the scorer's from here), calling `transcript_check.classify()` with the arm's prompt, the golden capture, the retained completion, the `CALL.json` and the pinned model; `bind_transcript()` runs it between the schedule stamps and the seal and retains the verdict as `TRANSCRIPT.json` INSIDE the seal, so it is covered by the manifest and the chain. It records and never refuses — a per-slot verdict is a per-slot outcome and §1a owns what it costs — except on an `UnclassifiedRefusal`, which propagates. `AUTHORING_PROTOCOL_CODES` carries the one code this adds, `author-protocol-violation`, in a tuple of its own because it is NOT an admission code: `admit()` can never return it, `e4lib/admit.py`'s `DROP_ORDER` stays the six admission codes, and §1a registers it in its own sentence. **(17) R1-7 — the shortfall declaration is a SCHEMA carrying evidence.** `SHORTFALL_SCHEMA` and `SHORTFALL_SLOT_SCHEMA` register every member and its type; the declaration gains `declarationVersion`, the ledger's own file digest and chain head, and the full slot/seal INVENTORY — one row per slot with its place in §2's order, its path, its `SLOT-MANIFEST.json` digest, its wrapper exit and its §1a code. `validate_shortfall()` checks the schema, the registered constants, the prefix property against `schedule_entries()`, the partition membership of every code, and every count DERIVED from the inventory under it; `verify_shortfall()` compares it to the ledger slot for slot and to both ledger digests. `declare_shortfall()` runs both BEFORE it writes — a declaration this driver cannot validate is one it does not write — and `harness/score.py` runs the same two functions on read rather than spelling a member list of its own. **Still not carried:** anything that scores — admission, the rates, the verdicts and every `score_rates` surface beyond the four functions above |
| `harness/integrity.py` | `98e11a14f931e47ece6b5c975afe46a18ef784d8824785fab8632083c5014af1` | `harness/integrity.py` | `bfa696328d7c2d135f80c4929a26a9d1fa54036bda787e7f6d8055a9b51025c9` | **PARTIAL — the chain, the interpreter, the unreviewed-bytes gate, the label rule.** Carried **verbatim** (byte-sliced from the source, not retyped): `IntegrityError`, `digest()`, `_refuse_duplicate_keys()`, `load_json()`, `bare()`, `parse_ports()` and the `ROW` regex (012 lines 169–219); `verify_interpreter()` (1142–1160); `_code_equal()`, `_const_equal()`, `verify_bytecode()` (1163–1346); `_refuse_unsafe_import_path()` (1386–1414) — including its references to Study 012's README steps, which this study's runbook has not been written yet (SCAFFOLD item R5). Rewritten for the one-level chain: `verify_chain()` keeps every idiom of 012's — the unfinished-port placeholder scan — whose token is deliberately not quoted here, because this file is one of the two the scan reads and quoting it refuses the port, as it did once while this row was being written —, the registry's own `pinnedFrom` members checked against review-bound constants, the exact destination set, per-row source and destination digests — and drops the two levels this study does not have; the source-side authority is 012's own PORTS.md destination cell per row, and the one untiered row is bound to the recorded commit. New: `study_label()`, `freeze_pin_state()`, `unfilled_pins()` (the registered label rule, decided in one place) and `verify_manifest()`. **Not carried, deliberately:** the arm-artifact checks (C8), the family schema (C9), the clean-room mirror gate (C10), the 280-cell landmark grid, the policy parser, `sigma`, the census helpers — none of them names anything in this study — and the `[D-20]` whole-tree git manifest, superseded by ADR 0004's exact-set manifest, because carrying both would give one study two manifests that could disagree. Imports dropped with them: `itertools`, `importlib.util` at module scope, `Counter`, `Decimal`. **SCAFFOLD item M1, points 2 and 3 (closed here):** `REQUIRED_PORTS` registers SEVEN destinations rather than five — the two scorer modules below are as loud an addition as a deletion would be, which is the whole point of an exact set — and `TIER1_TWELVE_PATHS` gains `harness/e4lib/stats.py` -> 012's `harness/score_rates.py` and `harness/e4lib/census.py` -> 012's `harness/census.py`, so both rows are bound to 012's OWN destination cells exactly as the other four are. 012's source cell for its census (`analysis/diversity.py`, Study 011) is one level further back than this one-level chain reaches and is deliberately not read. Three head comments change `four` to `six` with it. **ROUND 1 adds two things and neither is a relaxation.** `FREEZE_PINS` grows from ELEVEN members to EIGHTEEN (finding R1-9): `opa.capabilitiesSha256`, `jpack.reproducibleBuildAttestation`, `codex.model`, `probePrompt.sha256`, `golden.sha256`, `isolationNegative.assent` and `reviewerMutantSet.sha256` join it, because `REGISTERED` was reachable while every one of them was null and a null capabilities digest was merely RECORDED as unenforced by the toolchain. `CEREMONY_LIFECYCLE_PINS` and `ceremony_unfilled_pins()` are new with them and exist for one reason, stated where it is used: the golden-context capture WRITES `golden.sha256` and the isolation negative control WRITES `isolationNegative.assent`, so the driver's pre-ceremony gate cannot demand the two values those commands exist to create. They are freeze pins regardless — `study_label()` reads the whole set — and the exemption applies at that one gate and nowhere else, which `harness/tests/test_pins.py` asserts in both directions |
| `harness/transcript_check.py` | `64542bc5d6d8f6682a29dee870aa07feb5757db3941c48af581a974c2423a5b2` | `harness/transcript_check.py` | `f371834cf9d08a049b705c553b14ddb385274742be1080b9ef0e6c032fc5ef4c` | **complete port, no check logic changed.** The `response_item` whitelist, the terminal-prompt rule, the leak denylist mechanism, the golden allowlist comparison, the completion byte binding, the `turn_context` model/cwd binding, the integer-exit-0 rule and duplicate-key rejection are 010's through 011 and 012, unchanged. Two SUBJECTS change: `LEAK_TOKENS` is this study's vocabulary and not 012's policy-family vocabulary; and the arm label is one of A/B/C. **SCAFFOLD item G3's residual is closed here:** the token list is no longer a tuple written out in this file. `LEAK_TOKENS = leak_tokens.SCREEN_TOKENS` — the same object the wrapper's scratch-path screen reads under its other name `leak_tokens.SCRATCH_TOKENS` — whose policy half is DERIVED from the stimulus slice of the frozen-candidate prose by the three registered rules and whose instrument half is `leak_tokens.INSTRUMENT_TOKENS`, named as design-time and separately power-checked. The study therefore holds ONE leak list and the freeze's re-derivation (when `policy/POLICY.md` supersedes the candidate) moves both screens at once, where two copies would have moved one. Power is demonstrated on both halves: `leak_tokens.check_power()` requires the derived list to catch every witness sentence the source's own markup identifies while a scrambled list of the same size catches strictly fewer, and the new `leak_tokens.check_instrument_power()` requires the instrument half ALONE to catch strictly fewer witnesses than the derived half and the union to lose none — so the screen's policy power provably comes from the prose and not from the curated tuple. `leak_tokens.design_time_gap()` becomes a standing assertion (nothing derived is missing from the screen; everything extra is exactly the instrument list) rather than a to-do list. No check logic moves: the whitelist, the terminal-prompt rule, the golden allowlist, the completion binding, the `turn_context` bindings and duplicate-key rejection are untouched, and the only other edit is the three-line `sys.path` preamble that makes `leak_tokens` importable the way the ceremony invokes these files. **Round 1 (R1-5) adds a third change, and it is a RULE rather than a subject: every refusal names its CAUSE.** No check moves — the same transcripts refuse and the same transcripts pass — but every `raise TranscriptError` site carries a `reason=` tag, `REASON_CAUSE` maps each tag to one side of §1a's partition and the code the scorer files it under, and `classify()` returns that as a structured verdict instead of an exception. The distinction is the one the review names: a transcript carrying a tool call or a turn after the registered prompt is the AUTHOR breaking §3's single-shot, no-tools instruction — `author-protocol-violation`, an authoring outcome retained in the denominator and scoring zero — while a mismatched prompt, a drifted golden context, a mangled log, a mis-extracted completion, a wrong turn-context or a nonzero recorded exit is APPARATUS and leaves it as `transcript-refused`. Wiring `check()` in wholesale, which is what the finding asks for, would have filed every tool call as pipeline-invalid and silently deleted the runs the instruction exists to catch. Fail-closed in three places: a refusal with no reason, a reason `REASON_CAUSE` does not name, and a read error on any of the five bound paths all raise `UnclassifiedRefusal` or answer `unreadable` rather than admitting. `tests/test_transcript_binding.py` holds one adversarial transcript per reason tag and asserts the side and the code of each, plus the closure tests — every reason reachable, every raise site tagged (read out of this module's AST), every assigned code a key of `batch.CODE_PARTITION` on the side the map claims |
| `harness/score_rates.py` | `f4d4463f081439f147a341bb38d8a6b709b3860f73f6f4e524234a180ec23336` | `harness/e4lib/stats.py` | `4dce9746aea5b16cfe0dd6ca0eae2fd7b85e1ac2a15349aa4dec0eae5fd68567` | **PARTIAL — the interval arithmetic only, plus this study's contrast.** Carried with their arithmetic unchanged: `ALPHA`, `BISECTIONS`, `_tail_ge()`, `_tail_le()`, `_bisect()` (the registered 200-halving bisection, fixed iteration count and exact comparison, so the same inputs give the same bits on any platform), `clopper_pearson()`, `lower_bound()`, `upper_bound()`, `probability_at_least()`, `rate_block()`, and **`REGISTERED_VECTORS` verbatim, all three rows** — 012's n = 30 and n = 25 are retained as PORT CONTROLS against numbers a predecessor already published, and its n = 50 row is this study's own per-arm denominator (§2 "Batch shape"). `harness/tests/test_score_stats.py` reproduces every published bound to the four decimals 012 printed; a drift in this arithmetic stops a previous study's number reproducing and the suite says so before anything is scored. **Not carried:** `HIGH_CUT`, `LOW_CUT`, `high_threshold()`, `low_threshold()` — Study 011 §5's review-depth cuts, reported by 012 as a product quantity and naming nothing in this study — and the whole of 012's scoring, population, census and record-compilation surface, which is about arms, policies and mirrors. Changed: `ValueError` becomes `StatsError` with a NAMED CODE as the message's first word (`CP-NO-TRIALS`, `CP-NOT-A-COUNT`), because this study's refusals are read by a scorer that publishes them and an unnamed refusal is a string. **Added below the port banner, from THIS study's design prototype `design/mutants/oc_table.py` (sha256 `4707e50cee46a1a922f4202911efbfae311c6a20ddae0c96d1d0846c549cd131`, cited in the module docstring as assembled-from-design lineage rather than as a cross-study port):** `z2_table()`, `tail_coefficients()`, `sup_tail_numerator()`, `sup_le_alpha()` and `critical_level()` carried, plus `critical_level_at()` (memoised, so the two registered contrasts at one N read the same c\*), `excludes_zero()` (Reading 1 — the Δ₀ = 0 inversion, which is the whole of what §5's decision reads), `tau_cut()` (§5's operative INTEGER cut, derived from the paired count at run time rather than transcribed). **SCAFFOLD items S7 and S8 land here, and neither is a relaxation of a guard.** **S8 — the general unequal-N inversion.** `z2_table()`, `tail_coefficients()`, `sup_tail_numerator()`, `sup_le_alpha()`, `critical_level()`, `critical_level_at()` and `excludes_zero()` all take TWO arm sizes now, `n_right` defaulting to `n_left`. At Δ₀ = 0 the FM constrained MLE is the pooled proportion in closed form whatever the arm sizes are, so the general statistic is the exact rational `N (x·n_C − y·n_A)² / (n_A·n_C·(x+y)·(N−x−y))` with `N = n_A + n_C`, and the prototype's `2N(x−y)²/((x+y)(2N−x−y))` is its n_A = n_C slice; because both arms share one nuisance rate at Δ₀ = 0, the tail is still ONE Bernstein polynomial in one variable and the half-mesh scan is still sound (the tail is symmetric under (x,y) → (n_A−x, n_C−y), asserted in the suite at unequal sizes rather than inherited). `tests/test_score_stats.py` requires the general form to reproduce `design/mutants/OC-TABLE.md`'s c* and realised size at N = 30/50/100 EXACTLY — as the same rationals, not to four decimals. The zero-exclusion predicate becomes `z² > 0` rather than `x != y`, which is the same set at equal arm sizes and the correct one at unequal ones, and `harness/score.py`'s `FM-UNEQUAL-N` refusal is gone: §5 registers this construction and §1a makes unequal denominators the expected case. **S7 — the Δ₀ sweep.** `interval_endpoints()` computes rather than refuses: `score_cubic()` builds, by polynomial multiplication rather than a transcribed expansion, the integer cubic whose root is the constrained MLE; `constrained_mle()` locates it by exactly `FM_MLE_BISECTIONS = 48` halvings of the feasible interval with the sign taken in exact INTEGER arithmetic — the same fixed-iteration, exact-comparison discipline Study 012 registered for `_bisect()`, and chosen over Farrington and Manning's trigonometric closed form precisely because that needs `cos`/`acos` and a libm call in the ordering of tables is what this program forbids; `fm_z2()` returns the exact Fraction (and `math.inf` for the zero-variance boundary at Δ₀ = ±1, so the ordering stays total); `delta_tail_sup()` takes the nuisance supremum in exact integers over the registered mesh, using per-row tail RUNS and a prefix sum so a thousand mesh points cost a hundred additions each rather than a row scan; and `fm_pvalue()` gives one sup per Δ₀, which is equivalent to the critical-level construction (the sup is non-increasing in the level and the observed statistic is an attained level) and is what a sweep wants. **The registered Δ₀ mesh is `FM_DELTA_MESH_DEN = 100`**, `M_Δ = {j/100 : j = −100…100}`: every attainable per-arm rate difference at the registered N = 50 is a multiple of 1/50 and therefore a mesh point, and 1000 is a multiple of 100 so `p_C` and `p_A = p_C + Δ₀` are both points of the registered NUISANCE mesh and the whole supremum stays integer arithmetic. The reported interval is the convex hull of the ACCEPTED MESH POINTS — an inner approximation to the continuum acceptance set, refined to 1/100, and the record says so in its own `construction` string along with whether the accepted set was contiguous. `fm_z2()` at Δ₀ = 0 returns `z2_table()`'s own cell arithmetic, so the reported interval and the registered decision cannot be two constructions that disagree at the one Δ₀ they share, and the suite asserts it. The endpoints are a REPORT: §5's rule reads `excludesZero` and nothing else, so `score.contrast()` catches an endpoint refusal and leaves the verdict standing. **ROUND-1 FINDING R1-16 renames what this file returns and quantifies one of its two approximations.** The reviewer's finding was that the reported interval is not established as an exact 95% confidence interval over the continuous parameter space: the nuisance supremum is taken over M = {k/1000} rather than over [0, 1], and the Δ₀ inversion over M_Δ = {j/100}. Certification was COSTED AND DECLINED — the Bernstein derivative bound makes the mesh error N/(2·mesh_den), so a certified continuum supremum at N = 100 needs a mesh of denominator ~50,000 to leave a thousandth of slack under α = 0.05, which is 25,000 exact degree-100 Bernstein evaluations per level inside a binary search inside a 201-point sweep — so the artifact is RELABELLED instead. `CONSTRUCTION_NAME` is the one name this study publishes, **exact-arithmetic mesh-inversion hull**, and it travels inside every contrast and every endpoint record together with `levelCertifiedOverContinuum: false`, `nuisanceMeshSlackBound` and an `approximationDirection` string that states which way each approximation errs: the mesh supremum is a LOWER bound on the continuum supremum, so the procedure may be anti-conservative by at most that bound, and the Δ₀ hull is an INNER approximation, so it can be narrower than the continuum interval and never wider. `mesh_slack_bound()` is new and computes that bound exactly from Bernstein's derivative identity; NOTHING is adjusted by it — it is a published ceiling on the label's error. `tau_cut()`'s `tau` default moves from definition time to CALL time, so a test that moves the registered threshold moves what the function computes **ROUND-2 FINDING R2-12 makes the marginal interval a SETTLED quantity rather than an inline one.** §5 says "no inferential quantity is computed, let alone published, at or above row 3", and `rate_block()` computed the exact Clopper-Pearson bounds inside every endpoint — before a single control gate had been evaluated — and the publisher printed them whatever row the ordered rule selected: a failed-E1 probe returned `control-gate-failed` and still published `[0.0126, 0.9874]`. Contrast and direction suppression held, which is narrower than the prohibition. `rate_block()` now returns its integers, its rate and `ci95State: not-computed-yet`; `fill_intervals(node, licensed, reason)` is new and walks a published structure once, computing the bounds only for an outcome that reached row 4 and otherwise stamping `not-computed-control-gate-failed` with the reason beside it. `CI_PENDING`, `CI_COMPUTED`, `CI_EMPTY` and `CI_SUPPRESSED` name the four states so no reader has to infer a suppressed interval from a null. Nothing recomputes a rate: a suppressed block and a published one carry the same counts. |
| `harness/census.py` | `911eb25773923789e5ddeae20f0bfa68032f932ae9c62fd7e9a21ad8aa8b73ea` | `harness/e4lib/census.py` | `49b96a2c7ea792b9656acb4a4bde488068b769e8c99628de8c3a4c9345c9aa03` | **PARTIAL — the machinery, not the endpoints.** §5 registers E5 as "012's census machinery, ported", so this is the sixth row SCAFFOLD item S6 owed. Carried verbatim: `_token()` (012 lines 237-241), `show_signature()` (226-235), `cover_greedily()` (251-269), and `_x4()`'s `signature()` grouping (515-541) as `signature_groups()` with its ordering key unchanged — descending by run count, then by the rendering, "so the order is a fact about the data and not about a hash", which is what 012's round-5 finding 9 forced into existence. Changed, and it is a behaviour change rather than a rename: `show_multiset()` sorted by `Decimal(value)` because 012's values were risk scores; this study's are outcome tokens, so it sorts by the rendered string and a numeric sort that would raise is gone. **Not carried, because they name Study 012's stimulus and nothing here:** `_policy_mirror()`, `edges()`, `embargoed()`, `score()`, `band()`, `profile()`, `probe()`, `probe_exact()`, `deciding_clause()`, `clause_text()`, `show_probe()`, `_near_edge_row()`, and X1-X6 (`_x1()`…`_x6()`) with 012's `render_markdown()` — 012 censused vendor records a model wrote inside a completion under one arm's thresholds, and this study's authors emit a policy and a test suite, so there is no `vendor` record to bucket and carrying them would give this study six endpoints it did not register. **New, and only §5's two registered rows:** `encoding_key()`, `pairwise_disagreement()`, `census()` and a small `render_markdown()`; the stimulus is a PARAMETER rather than a module constant (012 read the arm's `FAMILY.json`), so the machinery cannot silently run on the wrong grid. Carried unchanged from 012's own port decisions: **no publisher and no `__main__`** (the only publisher in this study is `harness/score.py`) and **no interval** (case-level counts inside one completion are not independent trials). **SCAFFOLD item S6 lands here:** `registered_stimulus()` was a REFUSING STUB raising `E5-STIMULUS-UNREGISTERED` for as long as §5 named no census grid. §5 registers one now — "Registered census stimulus: the gold-row input set (the 105 gold inputs; disagreement profiles are computed over exactly these cells, closing the §9 joint-reading concern about unstated stimuli)" — so the function READS the frozen gold suite instead, and reads it as a STIMULUS and not as an oracle: only the row ids and their order are taken, and no gold expectation reaches any census number. It refuses on the two ways a suite handed to it is not a stimulus (`E5-STIMULUS-EMPTY`, `E5-STIMULUS-DUPLICATE-CELLS`), and `STIMULUS_LABEL` travels inside every record so a reader of one table cannot lose which grid it is over. §9 is UNCHANGED and still governs the reading — E4's stimulus is the mutant set against each run's own authored suite, the census's is these cells, and no tradeoff statement combining them is licensed — which is why the note is carried in the record rather than left in the preregistration. The vectors `harness/score.py` hands it are the SAME evaluation E1 makes over the same cells, computed once, so the two endpoints cannot disagree about what a run answered. **ROUND 1 (R1-19) changes one thing, and it removes a transcribed number.** `STIMULUS_LABEL` was the constant string "the gold-row input set (105 gold inputs)", written when the gold suite had 105 rows; the adequacy pass and round 1's arm-A reference repair have moved that count since, so a published census table would have carried a row count the suite it was computed over does not have. The label is now `stimulus_label(count)` over `STIMULUS_LABEL_TEMPLATE`, applied to the count of the stimulus points ACTUALLY READ, and the two docstring quotations of §5 are re-quoted from §5's current bytes. No census number and no ordering key moves — `harness/tests/test_score_census.py` reproduces the same records — and `harness/tests/test_score_census.py::test_the_stimulus_label_is_derived_from_the_suite_it_was_read_over` reads the committed gold suite, requires the label to carry that suite's own row count, and requires the label at any other count to differ |
| `harness/make_manifest.py` | `660a350ad8a647a2df9fea443af273c8c20480bd276c5a74336e345a86cadb81` | `harness/make_manifest.py` | `cb1dbcc057f22e60446969c8a140e6c5db0fa4b9594bb563851b904e04437a1b` | **complete port, ADR 0004 applied.** From Study **014** (no lock, no pin: bound to the recorded commit alone). `REGISTERED_DOCUMENTS` is this study's registered set; `EXCLUDED_DOCUMENTS` gains **`DEVIATIONS.md` and `README.md`** — ADR 0004's named exclusions, excluded by construction and asserted by `harness/tests/test_manifest.py` **while both files exist**, so the assertion has power rather than guarding an absent path — and keeps 014's `harness/PINS.json` linear-anchor exclusion; `EXCLUDED_ARTIFACTS` names the manifest itself; the covered set adds `harness/*.sh` and `harness/PORTS.md`; and `pending_documents()` plus a `--freeze` flag are new, because several registered documents do not exist yet pre-freeze and a set discovered by globbing at freeze time is not a registered set — `--freeze` refuses while any is pending. 014's `EXCLUDED_FIXTURE_ROOTS` and its `fixtures/` and `adapter/` globs are dropped: this study has neither tree. **SCAFFOLD item M1, point 4 (closed here):** `manifest_entries()` globs `harness/e4lib/*.py` as well, because the scorer's ten modules decide every published rate and ten reviewed sources outside the exact-set manifest is the hole ADR 0004's manifest exists to close. The glob is ONE level, like the other three, so a nested package added later must be registered rather than swept in. **ROUND-1 FINDING R1-9 widens the covered set to every byte the scorer executes.** The manifest covered the two top-level mutant manifests and the reference MARKDOWN and none of the payloads: `REGISTERED_DOCUMENTS` gains `reference/refA/pack.json`, `reference/refB/policy.rego` and `controls/off-gold-equivalence.json`, and the new `REGISTERED_PAYLOAD_SETS` adds exact one-level globs over `mutants/jps/*.json`, `mutants/rego/*.rego` and the sealed `controls/reviewer-mutants/` set (R1-10) — so every mutant payload, both reference implementations and the certificate carry a PER-FILE hash and `--freeze` refuses while any of the three new registered documents is absent. A payload directory that does not exist yet contributes nothing and is not fabricated; once it exists the glob is exact, and an added file is as loud as a deleted one |

**This table is machine-read, and its columns answer to different
authorities.** This file is editable in *this* study, so it cannot be the
authority for what the inherited bytes were. `harness/integrity.py` therefore,
in order: verifies Study 012's `harness/PINS.json` against the digest it pins
for it; verifies Study 012's `harness/PORTS.md` against the digest **012's own
registry** records under `ownPorts`; verifies **this file** against the digest
`harness/PINS.json` records for it, so the change list cannot be rewritten
after the review; and then binds each row — the six Study 012 rows to 012's
own destination cells on the source side and to this table on the destination
side, the Study 014 row to the recorded commit's working file. It also requires
the destination set to be exactly the seven files above, so a deleted row
refuses rather than quietly dropping a check.

**Two rows are AHEAD of their registry, deliberately and in the registered
order.** `harness/SCAFFOLD.md`'s freeze-fill step 6 says "`PORTS.md` before
`PINS.json`, always: the registry pins the ports table and never the reverse."
The two new rows therefore land here first, and three things move after them
and are owed by name in `harness/SCAFFOLD.md` item M1: `PINS.json`'s
`ownPorts.sha256` (which pins this file and no longer matches),
`integrity.REQUIRED_PORTS` and `integrity.TIER1_TWELVE_PATHS` (which register
the exact destination set and its 012-side paths), and
`harness/STUDY-MANIFEST.sha256`. Until they do, `integrity.verify_chain()`
REFUSES — which is the correct state, not a broken one: `harness/score.py`
files that refusal as a pipeline problem and the attempt is pipeline-invalid,
so nothing is adjudicated against an unpinned ports table.

## The schedule, and why it is a floor rather than a balance

Study 012's 150 slots were 30 rounds of five arms, and its registered order was
*exactly* balanced: every arm in every within-round position exactly six times,
every ordered pair adjacent exactly six times within rounds. None of that
survives three arms:

* 50 slots per arm over 3 within-round positions is 16⅔ — no integer;
* 149 directed transitions over 6 ordered pairs is 24⅚ — no integer;
* 50 rounds is not a multiple of the 6 Williams sequences, so the batch cannot
  be whole blocks of the table.

What is registered instead is the **arithmetic floor of both spreads**, and it
is established rather than asserted. `derive_order()` enumerates all 720
orderings of W1…W6 against all 30 ordered two-sequence tails, discards every
order in which an arm immediately follows itself, and returns the
lexicographically-least of those minimizing (position spread, transition
spread). The answer is

```
block order  W1 W2 W3 W4 W6 W5   (eight times, rounds 1-48)
tail         W4 W6                (rounds 49-50)
spreads      position 1, transition 1 — the floor
```

and `harness/tests/test_schedule.py` asserts that the registered constants ARE
that answer. If a better order existed the search would find it and the test
would fail, rather than a worse order passing under an adjective. The published
properties, all re-derived by the test from the expansion's own counters:

| property | registered value |
|---|---|
| slots per arm | 50, all three equal |
| position counts | every (arm, position) cell 16 or 17; each arm 17, 17, 16 |
| self-successions | 0 — no arm ever immediately follows itself |
| within-round directed transitions | 100 |
| round-boundary transitions | 49 |
| total directed transitions | 149; five ordered pairs 25 times, one 24 — spread 1 |

## The timeout ceiling, and which side of §1a it is on

Study 012 registered no per-call ceiling and its wrapper ran unbounded. This
study registers **2700 s** (PREREGISTRATION.md §2 "Batch shape"), and three
files have to agree about it or the study has three ceilings: the registry
carries the number, the wrapper reads it from the registry and enforces it, and
the driver classifies on its own constant. `harness/tests/test_schedule.py`
asserts the registry's two values equal `batch.py`'s two constants.

Its SIDE is the load-bearing part. A timeout is an **apparatus** failure:
pipeline-invalid, excluded from every rate's denominator, reported with its own
rate and interval, and a per-arm timeout rate above the registered cap is a
control-gate failure adjudicating R1 in neither direction. §1a records why this
is registered in code rather than left to the driver — the design-phase pilot
driver mis-filed timeouts as an authoring code, which silently moves a run out
of the excluded set and into the denominator of every rate.
`harness/tests/test_partition.py` asserts the side against §1a's own list, and
asserts that no wrapper exit status maps to an authoring code.

One residual, stated rather than hidden: `timeout` returns 124 when TERM
sufficed and 137 (128+9) when the KILL was needed, and a 137 produced by
something else — an OOM kill, say — would be recorded here as a ceiling hit.
That misreading costs a code and never a denominator, because a nonzero exit is
an apparatus failure too.

## What was NOT ported, and why

Everything Study 012 built for a policy-perturbation design: the five arms'
`POLICY.md`/`FAMILY.json`/`ARM.json` artifacts and their assembler, the single
registered mirror and its clean-room second mirrors, the landmark grid, the
records compiler, and all of `score_rates.py` and `census.py` EXCEPT the two
partial rows above — 012's scoring, population, ledger-reconciliation and
record-compilation surface, and its X1–X6 census endpoints. This study's
stimulus is a contest policy in three representations, its oracle is a gold
suite plus two reference implementations, and its endpoint is what an authored
test suite kills — none of that machinery names anything here.

Also not ported: Study 012's `harness/tests/` — its fixtures are about arms,
policies and mirrors. This study's suite is new, and small on purpose.

## Assembled from this study's design prototypes

These modules are not cross-study ports and have no row in the table: they are
this study's own `design/` code, carried into the harness with its line ranges
named in the assembled module's docstring together with the prototype's path
and sha256. The prototypes were run against the real pinned engines during the
design phase, which is why they are carried rather than re-authored — but they
are this study's bytes, and a two-sided row would claim an inheritance from
another study that does not exist.

| assembled module | design prototype | prototype sha256 |
|---|---|---|
| `harness/e4lib/extract.py` | `design/pilot/pilot_run.py` (81–86, 181–216) | `09da06b334f6b3ae3224b03f6e49e2f0f3c5519401e94e72f23df7333cffd295` |
| `harness/e4lib/admit.py` | `design/pilot/pilot_run.py` (242–275, 276–315) | `09da06b334f6b3ae3224b03f6e49e2f0f3c5519401e94e72f23df7333cffd295` |
| `harness/e4lib/engines.py` | `design/pilot/pilot_run.py` (217–229, 232–241, 316–414); `design/mutants/e4_score.py` (337–374); `design/gold/check_gold.py` (the floor-gate invocation) | `09da06b3…`; `beb42b39…`; `a3aa62ea51491f370f4423f4945b79aa9bae06d03dd60489b9c8952ec6e9294b` |
| `harness/e4lib/e4.py` | `design/mutants/e4_score.py` (152–194, 195–231, 232–245, 295–308, 310–336, 375–384, 556–654) | `beb42b3903284dc2c33baff33000325814a1e53171d8268ca4d56820e4f995fb` |
| `harness/e4lib/stats.py` (contrast half only) | `design/mutants/oc_table.py` (141–275) | `4707e50cee46a1a922f4202911efbfae311c6a20ddae0c96d1d0846c549cd131` |
| `harness/leak_tokens.py` | `design/POLICY-DRAFT.md` — the STIMULUS SLICE the source itself marks off (`## Vendor Approval Policy` … `## Design notes (not part of the stimulus)`), read as prose and not as code | `bc6eeff9e18e144e055e32f85402ad4c47b1c05b64743cfbc1a6f4012fb0ad40` |

`harness/leak_tokens.py` is the odd one in that table and says so: its
"prototype" is the stimulus PROSE, not design code. SCAFFOLD item **G3** requires
`LEAK_TOKENS` to be re-derived from the frozen policy text rather than curated,
with a committed checker showing the list has power on mutated inputs, so the
module is the derivation: three registered rules over the slice the source marks
off for itself (bold and backticked terms; clause ids; the threshold numerals of
comparison sentences and their spellings), one admissibility filter that
publishes every drop with its reason, and three checks — `check_power()` (every
witness sentence the source's own markup identifies is caught, a scrambled list
of the same size catches strictly fewer, the empty list none),
`check_rederivation()` (move a threshold in the source and the derived list moves
with it) and `check_negative_corpus()` (no derived token fires on any name the
wrapper builds). The digest above is the source's at derivation time and
`report()["source"]["sha256"]` recomputes it; `policy/POLICY.md` supersedes the
draft at the freeze with no edit to the module, because `SOURCES` is ordered.
`harness/transcript_check.py`'s tuple is still the design-time list and
`design_time_gap()` computes, rather than remembers, what the freeze must copy
across.

`harness/e4lib/decision.py` is assembled from a PROGRAM SHAPE rather than from a
prototype — Studies 015–018's `decide()`, generalised from an if-ladder to an
ordered table, for the reason its docstring gives (Study 018's round-8 finding 1
was a decision rule whose code and whose registration disagreed, and a ladder
gives nothing to enumerate). Its authority is `PREREGISTRATION.md` §5's own
bytes, which `harness/tests/test_score_decision.py` reads directly.

## New here, not ported

`harness/PINS.json`, `harness/PORTS.md`, `harness/SCAFFOLD.md`,
`harness/STUDY-MANIFEST.sha256`, `harness/e4lib/__init__.py`,
`harness/e4lib/domain.py` and `harness/e4lib/reviewer.py` (both new in
round 1: the registered input domain with the symmetric per-arm case
enumeration finding R1-3 requires, and the sealed reviewer mutant set's
loader/executor finding R1-10 requires — neither is ported and neither is
assembled from a design prototype, because neither existed anywhere),
`harness/score.py`'s own publishing surface (the argument surface, the attempt
record, the population rule, the E1/E2/E3/E4 aggregations and the rendered
report), and `harness/tests/` (`test_schedule.py`, `test_manifest.py`,
`test_pins.py`, `test_partition.py`, `test_score_stats.py`,
`test_score_extract.py`, `test_score_admit.py`, `test_score_engines.py`,
`test_score_e4.py`, `test_score_decision.py`, `test_score_census.py`,
`test_score_attempt.py`, `test_score_pipeline.py`).

`test_score_pipeline.py` is the one module that invokes the real engines, and it
SKIPS unless `JPACK_BIN`/`OPA_BIN`/`OPA_CAPS` hash to the pins — §7 forbids
invoking `jpack` or `opa` in CI, so skipping there is the registered behaviour.
It exists because SCAFFOLD item T1 records the precise failure mode of
hand-verification: "which is evidence and not a suite: nothing in the repository
re-runs it."

Everything that section used to defer has landed: the driver's calling half
(SCAFFOLD items D1–D8) and the golden-context capture with the isolation
negative control (G1–G2) came in with `harness/batch.py`'s row above, and the
three refusing stubs are computations now — the census stimulus (S6) is §5's
registered gold-row input set, the Δ₀ sweep (S7) and the general unequal-N
inversion (S8) are in the `e4lib/stats.py` row, and the `engineSuppliedKill`
member (S9) is in both mutant manifests, arm A's from
`design/mutants/refA/REGISTRY.json`'s conflict-only list and arm B's as an
EMPTY registered class with its reason. `harness/score.py` runs the
reference-vs-gold floor gate (S10) rather than stamping it, and reads a slot
through the driver's own readers over the declared prefix (S11). What remains
owed is **T3** alone: the untracked `design/` sources and the stale
`__pycache__` trees that `integrity.verify_bytecode()` refuses, which is a
commit and not a port.
