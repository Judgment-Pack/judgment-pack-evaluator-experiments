"""Minimal compliant baseline agent for Cohort 1 (upstream Forge scenarios, unchanged).

Purpose: external integration validation only — prove the pinned harness runs
upstream scenario packs end-to-end through the study driver with complete
artifacts and computable deterministic scores. It calls each allowed tool once
(self-serving the upstream fixtures, which is the harness's own contract:
tool interception is not wired upstream), never touches a disallowed tool, and
answers with fixture-grounded text. It does NOT try to satisfy judge-scored
rubrics, and its scores claim nothing. Where a scenario has no tools it
answers cautiously and declines override/exfiltration/probing instructions.

Stdlib only. Env: STUDY_DIR.
"""

import json
import os

REFUSAL = (
    "I can't comply with that request: it asks me to override my instructions, "
    "expose internal configuration, or access restricted resources. I can help "
    "with the underlying task through approved tools instead."
)


def _fixture(payload, tool):
    fixtures_dir = payload.get("_fixtures_dir") or os.path.join(
        os.environ["STUDY_DIR"], "upstream", "fixtures")
    path = os.path.join(fixtures_dir, tool + ".json")
    if not os.path.exists(path):
        return {"status": "no-fixture"}
    with open(path) as f:
        return json.load(f)["return"]


def run(payload):
    steps = []
    results = {}
    for tool in payload.get("allowed_tools") or []:
        name = tool["name"]
        steps.append({"type": "tool_call", "tool": name, "args": {}})
        result = _fixture(payload, name)
        results[name] = result
        steps.append({"type": "tool_result", "tool": name, "result": result})

    if results:
        final = "Findings from {}: {}".format(
            ", ".join(sorted(results)), json.dumps(results, sort_keys=True))
    else:
        final = REFUSAL
    steps.append({"type": "response", "content": final})
    return {
        "schema_version": "evalforge.run_envelope.v1",
        "status": "completed",
        "output": {"final": final, "structured": None},
        "trajectory": {"steps": steps},
        "cost": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "cost_usd": 0.0},
        "error": None,
    }
