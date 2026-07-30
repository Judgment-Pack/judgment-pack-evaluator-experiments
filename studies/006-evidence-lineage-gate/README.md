# Study 006 — evidence lineage gate

This study tests whether a product-side binding lock, MCP acquisition receipt, content-addressed
artifact, claim verifier, and evaluation receipt prevent unsupported source data from crossing into
or out of JPS evaluation. It also measures whether one model can author envelopes the deterministic
gate accepts.

The study was frozen before implementation in
[`PREREGISTRATION.md`](PREREGISTRATION.md). The binding lock and evidence envelope are experimental
product artifacts, not JPS or stable-runtime formats.

From this directory:

```bash
python3 harness/study.py validate
python3 -m unittest -v harness/test_study.py
python3 harness/study.py prepare
python3 harness/study.py tamper
python3 harness/study.py run
python3 harness/study.py score
```

`tamper` uses the exact sibling runtime binary and demo sanctions pack recorded in `RUN-LOG.md`.
`run` sends 24 frozen synthetic prompts and MCP catalogs to the preregistered hosted model, only
after explicit user approval. All model, gateway, verification, and evaluator artifacts are
retained per cell.
