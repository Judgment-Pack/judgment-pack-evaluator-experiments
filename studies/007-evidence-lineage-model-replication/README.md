# Study 007 — evidence-lineage model replication

This cleanly replicates Study 006's model-authoring phase with a separately qualified,
hosted-compatible response transport schema. The semantic candidate validator and lineage gate
remain the admission authority.

The protocol was frozen before implementation in
[`PREREGISTRATION.md`](PREREGISTRATION.md). The source requirement, binding lock, evidence envelope,
and receipts are experimental product artifacts, not JPS Core or stable-runtime formats.

From this directory:

```bash
python3 harness/study.py validate
python3 -m unittest -v harness/test_study.py
python3 harness/study.py prepare
python3 harness/study.py qualify
python3 harness/study.py freeze
python3 harness/study.py run
python3 harness/study.py score
```

`qualify` makes one registered hosted schema-compatibility call with no MCP server and no efficacy
scenario. `run` sends the 24 authorized fictional prompts and synthetic MCP payloads only after the
qualification artifacts and complete harness have been committed.
