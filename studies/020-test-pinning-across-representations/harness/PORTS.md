# Ports — what Study 020 takes, from where, and what changed

Study 020 asks Study 019's question of the same three representations with the
instrument repaired. The machinery it counts with is inherited as **bytes**, not
as descriptions (`PREREGISTRATION.md` §7): this file records every port, its
digest on both sides, and exactly what was changed. `harness/integrity.py`
machine-reads the table below and binds each row **to the authority that row
actually has** before any call is made and before anything is scored.

**The chain, and why it is shorter than 019's while binding more.** Study 019
inherited seven files from Study 012 and could bind them only to the seven
destination cells 012's own `PORTS.md` published. Study 019 is **frozen**, and a
frozen study publishes a digest for every byte of its harness and every
registered artifact in one file, pinned by its own registry. That file is this
port's source-side authority, and `integrity.verify()` reads it first.

```
this file                                    (pinned in harness/PINS.json at port time)
    -> Study 019's harness/PINS.json              9ba6394db66f0e3723359c17f68e4a612870a015f3f973e1efad10fd522a759c
       Study 019's harness/STUDY-MANIFEST.sha256  79076e3181fd738b457a6c63d827be0769bb36d85b66ce35c37e6cf211d3e1a0
          (the digest 019's OWN registry pins for it under `studyManifest`,
           read from it and not chosen here)
```

The port was taken at commit

```
commit e87e1311da11c28e929edf1e7e39f048e4ec0e6a
```

**Every harness row is WHOLE-FILE and by digest.** The source path and the
destination path are the same path — a row that renames a file is a row this
study is not taking by digest, and `verify_chain()` refuses it by name. The
source cell of every row must equal 019's own lock line for that path, and 019's
working file must hash to it. There is no partial row in this table and no
`SCAFFOLD.md` deferral list: `PREREGISTRATION.md` §7's "ported with no design
change" list is the whole harness, and the thirteen registered deltas are
changes ON TOP of a complete port rather than pieces of an incomplete one.

## The harness — 46 rows, two-sided

| source (Study 019) | 019's lock digest | destination (Study 020) | digest as landed | changed |
|---|---|---|---|---|
| `harness/authoring_call.sh` | `8b326083e805062fcd21f341d05fa20c97fc3629180a06134147c514fcfa08da` | `harness/authoring_call.sh` | `c31a88a27cee97981fe9c2383d9e6df3600a4b71f4ba131f731034621e5d6442` | **re-pointed.** Scratch/home/bin names `s020-…`; the CALL.json note names this study. No call-path logic touched |
| `harness/batch.py` | `0e5306847b1292fe81db99e6ee3b67d5fbed68497615f4e82df69e94d472d6fe` | `harness/batch.py` | `ef9608a828e0f12c3f1c470347785a8f0bc4980425e67283c74b580f1f3b8361` | delta 7 (§7): the schedule constants carry the port skeleton pending the registered round count; label rule wiring for --sweep |
| `harness/e4lib/__init__.py` | `0887ba7f3916801d1e4bada096e0b135c745dfe2ac2dde290aa4d9402f3d6e0a` | `harness/e4lib/__init__.py` | `abb52bb99624e894c0599f62432bd8a9204111d0e19eb2e3c1f5fa3092944a8a` | delta 5 wiring: the family module exported |
| `harness/e4lib/admit.py` | `ac2c481e594690e009f10b325786bb98abbc4f933ee154364b4a6bd156cf21a8` | `harness/e4lib/admit.py` | `33063ceb69230d4cf944e4cbd4dc3a04c924318dafbdc0fd210d20b1fcc9b2a2` | delta 3 (§3.2): presence-idiom-unsound wired behind its registered-off switch |
| `harness/e4lib/capabilities.py` | `5793fa83810f64ab0ba3f4098a0555ae6aea8b44e86334abc0d2a3fd25643296` | `harness/e4lib/capabilities.py` | `5793fa83810f64ab0ba3f4098a0555ae6aea8b44e86334abc0d2a3fd25643296` | ported by digest, byte-identical to 019 |
| `harness/e4lib/census.py` | `f7e603df0440785b55b10a61b5aef2cc0fbd42677e7e713a71013840f77d0601` | `harness/e4lib/census.py` | `ea363300c446cd98ad9dd25b03b4383b22a031b9873ecd3826eca1e391b466ed` | port note added to the module head; no code change |
| `harness/e4lib/decision.py` | `3edb743f5bfe738e28035889e3d7be22f1f0af80de61f74ae8998d8877d81921` | `harness/e4lib/decision.py` | `4e8238654bfbb18f72c8e8351df97841b280266ef10d2d1ca03e7c31f321422d` | delta 5 (§5): the ordered decision table over the IU family verdict |
| `harness/e4lib/domain.py` | `20016d0987344be7544b503b0856d13b70c62dd434d6e708652749cbc4a555f1` | `harness/e4lib/domain.py` | `20016d0987344be7544b503b0856d13b70c62dd434d6e708652749cbc4a555f1` | ported by digest, byte-identical to 019 |
| `harness/e4lib/e4.py` | `13646b0d2a11e4580c3a971505dcdf107572c60ac5cf9cf8bd9171b477ddea3f` | `harness/e4lib/e4.py` | `788d276401c89ed66f6b98bdc673026f05145daf9c5163a847907597dc1daee3` | deltas 1-2 (§7): per-language denominators and lattices kept, threshold arm removed |
| `harness/e4lib/engines.py` | `1382c0cb523aca8fb8e99a02838721d4831847aa307c628a3a20484b0f469c09` | `harness/e4lib/engines.py` | `1382c0cb523aca8fb8e99a02838721d4831847aa307c628a3a20484b0f469c09` | ported by digest, byte-identical to 019 |
| `harness/e4lib/extract.py` | `4e853d688609dde4f3b0c98f33418218afed0c44048a9609b8234241b96aca9c` | `harness/e4lib/extract.py` | `4e853d688609dde4f3b0c98f33418218afed0c44048a9609b8234241b96aca9c` | ported by digest, byte-identical to 019 |
| `harness/e4lib/reviewer.py` | `0fc38aa4ebde113ec361f2986aab49d1925b4d962f1e1e554551d2ebba753b31` | `harness/e4lib/reviewer.py` | `0fc38aa4ebde113ec361f2986aab49d1925b4d962f1e1e554551d2ebba753b31` | ported by digest, byte-identical to 019 |
| `harness/e4lib/stats.py` | `e2ac82dd2248896ef8c3f72fbdd9a51ba92de3a67a4df24a6567a64c64c94c07` | `harness/e4lib/stats.py` | `09961a3f688d23a130566d0f3466e9b28c12f8c387f37d794df2a6b464658301` | delta 5 (§5): BCa intervals and the two permutation schemes with pinned B and seed |
| `harness/grid_gate.py` | `eea10546a2289129dd785ff9eddd546f83a1ac02ba508e51d4133567561bf75c` | `harness/grid_gate.py` | `eea10546a2289129dd785ff9eddd546f83a1ac02ba508e51d4133567561bf75c` | ported by digest, byte-identical to 019 |
| `harness/integrity.py` | `ba2175ad213abcd019e10dc7768aa16f5bcb7f52f77c5af1520c942fc81657e3` | `harness/integrity.py` | `3168b37445a8dd4ff1318a9fbb9dbdd6a80ed8c11a48b0da7df4002908c56d63` | port chain to 019's lock (§7) plus NEW_IN_020 and the ports/new exhaustiveness check |
| `harness/leak_tokens.py` | `5573f712eb89bd341862198f4e19fa58f1d7af4f69d269c1753ae66b39026c0c` | `harness/leak_tokens.py` | `21763f8ae76bbcce06507b17c387a60fe17b5ea5cdd133123e9b7ed70dae54d3` | **re-pointed.** `INSTRUMENT_TOKENS` names BOTH study titles (020's own, and 019's — 020's stimulus IS 019's bytes) and `WRAPPER_NAME_TEMPLATES` moves to `s020-…` with the wrapper |
| `harness/make_manifest.py` | `f30beaa3b186d29d7ddacb3e78d1ea3c30dcd6110fb9c8b193383811caeeb90d` | `harness/make_manifest.py` | `0c1acb0dc86e616cd8b14a74214e9faa97bd288eb9c81c23c4122850c3882ddf` | **§7 delta 11.** `CORRECTION-TARGETS.md` leaves the covered set by named constant and its pre-freeze obligation moves to `UNCOVERED_PRE_FREEZE_DOCUMENTS`, which `--freeze` refuses on |
| `harness/render_round_status.py` | `23a0720415c76417568b2a20c51fe8db64d78ff6e0697e6a36a7ba229e3800d0` | `harness/render_round_status.py` | `251b1feb2d379b7515229f6650b6f1cf9c2bb35367ce410b1972d2b91293db80` | **§7 delta 10.** The empty-of-rounds block is permitted and rendered; `SURFACES` narrows to `README.md` + `PREREGISTRATION.md`. Every other refusal ported unchanged |
| `harness/score.py` | `ddced312b2c4ae9ee67d491799066d24abbced6acea75da19056bdbcf03f5d6a` | `harness/score.py` | `22cbe29f879c69535d1d6542ac322405916f93dd3c2240aed2696463802f5d40` | deltas 1, 2, 4 (§7): survivor-vector write-time refusal, no-threshold cuts machinery, ownPolicyIdentity as a second named relation emitting E6 |
| `harness/tests/conftest.py` | `5ff1a90ab864b4fe61c3ad618a050bee9803746a8c8b930677564e84d25cc13e` | `harness/tests/conftest.py` | `5ff1a90ab864b4fe61c3ad618a050bee9803746a8c8b930677564e84d25cc13e` | ported by digest, byte-identical to 019 |
| `harness/tests/test_batch.py` | `731749aa0daf365ce9ca98ae116e73a93da0c55be5b79e63c26626bd96c34d07` | `harness/tests/test_batch.py` | `29fa150b92b415cdb62352307720f6b39a7aa439755d0fae0c7602d5e92f88e6` | rebuilt for 020's registered surfaces (the delta owning its subject; see §7) |
| `harness/tests/test_census_replication.py` | `65c417fa4bbf754bc54da8e9d0943075874f4d736d4d7df3e877c6c1fd70385e` | `harness/tests/test_census_replication.py` | `65c417fa4bbf754bc54da8e9d0943075874f4d736d4d7df3e877c6c1fd70385e` | ported by digest, byte-identical to 019 |
| `harness/tests/test_design_regeneration.py` | `d85d169f3e41d81f77617078ebdc971e1edfa41d45b11db98578e3efee2d490a` | `harness/tests/test_design_regeneration.py` | `d85d169f3e41d81f77617078ebdc971e1edfa41d45b11db98578e3efee2d490a` | ported by digest, byte-identical to 019 |
| `harness/tests/test_grid_gate.py` | `256be828f023e3b991b1a0302110797257515cf15772cec9edae4224115f6bbf` | `harness/tests/test_grid_gate.py` | `256be828f023e3b991b1a0302110797257515cf15772cec9edae4224115f6bbf` | ported by digest, byte-identical to 019 |
| `harness/tests/test_leak_tokens.py` | `2ad01b4228fc8367d3e0ec6fccca6e8228eb622fda7807d5d0ae914b66459e1c` | `harness/tests/test_leak_tokens.py` | `2ad01b4228fc8367d3e0ec6fccca6e8228eb622fda7807d5d0ae914b66459e1c` | ported by digest, byte-identical to 019 |
| `harness/tests/test_manifest.py` | `753bdd4287c7720c148e99bcd10f399ee5111d336171be865f4df01adf7bfdf1` | `harness/tests/test_manifest.py` | `54b80a7e5ca5450527b4b433d33adf43b0d924533af4982468b47e1e1c97cce5` | **§7 delta 11's asserting tests**, including the exclusion asserted WHILE the file is absent |
| `harness/tests/test_partition.py` | `1d3541d5a37a55ec0ddc98c400a9d4fa8465aed22fa1408eb7f6fd48ecb42fce` | `harness/tests/test_partition.py` | `db198e513a8187049900fd4bd2927e14326a558b916d1d7f3bf36e7bf1da887b` | rebuilt for 020's registered surfaces (the delta owning its subject; see §7) |
| `harness/tests/test_pins.py` | `af927a517fabfb1a25c8141189128817e9b784648206b0e0d16ed65832ad4c14` | `harness/tests/test_pins.py` | `50a8328ea76fe9708d70f90dc34728d9724ea361b45580f26aaf534daba62380` | rebuilt for 020's registered surfaces (the delta owning its subject; see §7) |
| `harness/tests/test_ports_chain.py` | `279f5c250e0aeff10c910dd3cd27331805e797be423ab02ba2a14327cac22cad` | `harness/tests/test_ports_chain.py` | `7225d4eb5bba1c85aad3ed88923b254c99a497a6b2d225a3c5573d3171467093` | rebuilt for 020's registered surfaces (the delta owning its subject; see §7) |
| `harness/tests/test_prereg_currency.py` | `aed98a18e1015f305cab9f8c344c7378a50ad56d6c75a2443dfba60089f6bbf0` | `harness/tests/test_prereg_currency.py` | `ee6739e60804a17af601c03e5db48d19dbc40fe4f66e34f36a48ac2902e52b25` | **§7 delta 10's asserting tests** added. The rest of this file still reads Study 019's prose and is HANDED OFF, not ported clean |
| `harness/tests/test_schedule.py` | `fcdfd6e535aafa649ff3c49cfd3d6886bf9f8501de27f50861b21728d4f3cd2c` | `harness/tests/test_schedule.py` | `257df54d7dd9d545e86a85a645c8542b3bbae703498cd47c87572869fbebccb2` | rebuilt for 020's registered surfaces (the delta owning its subject; see §7) |
| `harness/tests/test_score_admit.py` | `497b4ec0b9a627e19356859b6005a38b4199a87acac67b4c47e1c828b816342d` | `harness/tests/test_score_admit.py` | `497b4ec0b9a627e19356859b6005a38b4199a87acac67b4c47e1c828b816342d` | ported by digest, byte-identical to 019 |
| `harness/tests/test_score_attempt.py` | `3d0691fa58670d63575e879a3c19909799916440049a9b007a159278967199bf` | `harness/tests/test_score_attempt.py` | `12bee7e170f174dd75aad91b8f7b6c9eef985b44d607ba8a2a3095bf7f515c6f` | rebuilt for 020's registered surfaces (the delta owning its subject; see §7) |
| `harness/tests/test_score_capabilities.py` | `578d3d34a4ac39e0fcf878671541f583024fc99a3e6a50fcdefb9501fcb830d2` | `harness/tests/test_score_capabilities.py` | `578d3d34a4ac39e0fcf878671541f583024fc99a3e6a50fcdefb9501fcb830d2` | ported by digest, byte-identical to 019 |
| `harness/tests/test_score_census.py` | `44d1814988dd382b414362805ece3046e97891c4ea2189b8b75f5fdf6e2c9bb9` | `harness/tests/test_score_census.py` | `df1132035dd006a6ffc17e8c5aaac5e9bdf9e65f52ee68acb64497bd60044774` | rebuilt for 020's registered surfaces (the delta owning its subject; see §7) |
| `harness/tests/test_score_decision.py` | `7a636d283853ce651f6ac2dbd63bad7cdee629e134023614a4ec163c307d8792` | `harness/tests/test_score_decision.py` | `5ed11bd372da779e901d47392dc6dc1d0434c772d195e297fa7b3c7b5adddeb9` | rebuilt for 020's registered surfaces (the delta owning its subject; see §7) |
| `harness/tests/test_score_domain.py` | `89f5acd0e74d037d72529b70234ffed88691fccafaaeef0d8b4cc6e14252c3cb` | `harness/tests/test_score_domain.py` | `89f5acd0e74d037d72529b70234ffed88691fccafaaeef0d8b4cc6e14252c3cb` | ported by digest, byte-identical to 019 |
| `harness/tests/test_score_e4.py` | `2940605e88894ba449a9ca9984f8a86cde4b795ce19ce404247a9771d3187e88` | `harness/tests/test_score_e4.py` | `32ad008918b6e405178ca1a9245ad7af54ce1787e60cb94c06c2826300c22c17` | rebuilt for 020's registered surfaces (the delta owning its subject; see §7) |
| `harness/tests/test_score_engines.py` | `30c0c28975762f8088c2bb20dd4e642cf09c7803b4f051e8d3e1d5a095b85d8d` | `harness/tests/test_score_engines.py` | `30c0c28975762f8088c2bb20dd4e642cf09c7803b4f051e8d3e1d5a095b85d8d` | ported by digest, byte-identical to 019 |
| `harness/tests/test_score_extract.py` | `93f52695a38a4cff9880cab278efe04f8f080cc169a160e3b8b08070a26bbeb1` | `harness/tests/test_score_extract.py` | `93f52695a38a4cff9880cab278efe04f8f080cc169a160e3b8b08070a26bbeb1` | ported by digest, byte-identical to 019 |
| `harness/tests/test_score_pipeline.py` | `ac622c003e3c04534337298ce392b81160c192e5c9addd75bc76565f29c49761` | `harness/tests/test_score_pipeline.py` | `ac622c003e3c04534337298ce392b81160c192e5c9addd75bc76565f29c49761` | ported by digest, byte-identical to 019 |
| `harness/tests/test_score_publication.py` | `188acebd75bbd31d7e2b38fa1fc243dcfa5074c559d1efb08b68a23ad842eebc` | `harness/tests/test_score_publication.py` | `2ec98dd6bd0d33b7ecc064dbd44fce4d0d6e1c88aa08a5f6d86c80df7cfe3c88` | rebuilt for 020's registered surfaces (the delta owning its subject; see §7) |
| `harness/tests/test_score_reviewer.py` | `771763d8e0cbea21ffa44aa45fe0b79111f1fc360f75f9601e7a86c6fa22c47c` | `harness/tests/test_score_reviewer.py` | `771763d8e0cbea21ffa44aa45fe0b79111f1fc360f75f9601e7a86c6fa22c47c` | ported by digest, byte-identical to 019 |
| `harness/tests/test_score_stats.py` | `5c4e5a3c62d7db662b80e5afe75608e5b8cb9eebcaca630f18b40aecc4dee973` | `harness/tests/test_score_stats.py` | `928f2102a15e67dc1062a82e5a61db517030f15e9cc5a412821ae812c8543042` | rebuilt for 020's registered surfaces (the delta owning its subject; see §7) |
| `harness/tests/test_transcript_binding.py` | `9a6bbeee4444682647a02f76c88c2862b19fcc9d03b06c49427e6a18889a75ee` | `harness/tests/test_transcript_binding.py` | `9a6bbeee4444682647a02f76c88c2862b19fcc9d03b06c49427e6a18889a75ee` | ported by digest, byte-identical to 019 |
| `harness/transcript_check.py` | `17ab4655c703feb19b9df53096e71f55125d3178404ae9e8a4a96596f01f5ce7` | `harness/transcript_check.py` | `53b16836007aab006c1f4a1caa035a7566e60fb5692eac36f757afb378713895` | port note added to the module head; no code change |

**What "changed" means in the last column.** `ported by digest, byte-identical
to 019` is exactly that: `sha256(source) == sha256(destination)`, and the
generator that wrote this table refuses to emit that phrase for a file whose two
digests differ — and refuses to emit a table at all for a file that differs with
no change recorded. Every other cell names the registration that forced it.

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

## What does NOT carry, and why

| not carried | why |
|---|---|
| `controls/reviewer-mutants/` | §4.3: 019's reviewer set is **spent** — first executed at 019's primary attempt. 020 registers a **fresh sealed set**, authored during review rounds. 019's is kept only as a published comparison. |
| `design/pilot/pilot_run.py` | §7 **delta 12**, and §2a.2: 020 runs one driver, and a second pilot driver in the tree is a second thing that can make a call. |
| `design/pilots/` | §2a.1: 019's pilot cannot be reused — the differences are five, not three — so 020 runs its own (C1–C5). Carrying 019's pilot outputs would put another study's calibration data where this study's belongs. |
| `harness/tests/E2E-SMOKE.md` | 019's end-to-end smoke transcript is 019's **evidence**. 020 writes its own; §7 **delta 13** restates the part of it that failed. |
| `controls/opa-capabilities.json` | 020's capabilities file is generated from the pinned binary and the registered denylist **at pin time** (§2), not copied. |
| `arms/*/authoring/`, `arms/BATCH.json`, `results/` | 019's batch and its scored attempt. §1a registers 020's prospective content as its own post-freeze runs, and `make_manifest.py`'s freeze gates refuse a tree that carries any of it. |
| Study 019's `DEVIATIONS.md` entries D-1…D-4 | 019's deviations are **already in the ported bytes** — D-1's stdin redirect and D-2's gate re-seating are what this port takes. The entries themselves are 019's record. |

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
