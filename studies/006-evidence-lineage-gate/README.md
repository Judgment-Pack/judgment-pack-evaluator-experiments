# Study 006 — evidence lineage gate

This study tests whether a product-side binding lock, MCP acquisition receipt, content-addressed
artifact, claim verifier, and evaluation receipt prevent unsupported source data from crossing into
or out of JPS evaluation. Its deterministic phase completed successfully. Its model-authoring
phase terminated before inference after exhausting its registered infrastructure rerun, so model
usability is not estimable in this study.

The study was frozen before implementation in
[`PREREGISTRATION.md`](PREREGISTRATION.md). The binding lock and evidence envelope are experimental
product artifacts, not JPS or stable-runtime formats.

From this directory:

```bash
python3 harness/study.py validate
python3 -m unittest -v harness/test_study.py
python3 harness/study.py prepare
python3 harness/study.py tamper
python3 harness/study.py audit-d4
python3 harness/study.py run
python3 harness/study.py score
```

`tamper` uses the exact sibling runtime binary and demo sanctions pack recorded in `RUN-LOG.md`.
`run` was authorized to send 24 frozen synthetic prompts and MCP catalogs to the preregistered
hosted model. Both attempts at the first cell were rejected by the service's output-schema
validator before treatment; no model received a prompt or MCP payload. The retained outcome is
reported in [`RESULTS.md`](RESULTS.md), analyzed in [`ANALYSIS.md`](ANALYSIS.md), and challenged in
[`ADVERSARIAL-REVIEW.md`](ADVERSARIAL-REVIEW.md).
