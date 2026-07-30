# Study 005 — semantic source discovery

This API-dependent efficacy study compares the current prose-only `jpack.json` source hint with an
experimental `{id, description}` semantic reference. It asks whether one model selects the right
synthetic MCP source and degrades safely when the source is unavailable, ambiguous, denied,
malicious, or paired with a mutating decoy.

The study was frozen before implementation in
[`PREREGISTRATION.md`](PREREGISTRATION.md). The schemas in [`schema/`](schema/) are study
artifacts, not JPS or runtime formats. The deterministic harness is stdlib-only; model trials are
manual and never run in CI.

Commands, from this directory:

```bash
python3 harness/study.py validate
python3 -m unittest harness/test_study.py
python3 harness/study.py prepare
python3 harness/study.py run
python3 harness/study.py score
```

`run` invokes the preregistered Codex model and therefore needs the operator's existing Codex
authentication and network access. It retains every prompt, event log, stderr log, final response,
and MCP receipt under `trials/`.
