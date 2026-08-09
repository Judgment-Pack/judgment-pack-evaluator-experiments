"""RQ3 Arm A: replay decider for retained model decisions.

Stage 2 of the two-stage design (AMENDMENT-RQ3.md): the model calls happen
OUTSIDE Forge (harness/rq3_run.py --stage calls) with full retention; this
module deterministically REPLAYS the retained decision for each case inside
Forge, so the Forge runs stay reproducible and the adapter never waits on a
model. Env: STUDY_RQ3_REP_DIR names the authoring repetition directory.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import shell  # noqa: E402

REASONS = {"not-applicable", "missing-required-evidence", "unknown",
           "conflict", "no-match", "exception-escalation"}


def _handles():
    with open(os.path.join(os.environ["STUDY_DIR"], "scenarios", "rq3",
                           "HANDLES.json")) as f:
        return json.load(f)["handles"]


def codex_replay(case, facts, evidence, action_map):
    rep_dir = os.environ["STUDY_RQ3_REP_DIR"]
    handle = _handles()[case["id"]]
    with open(os.path.join(rep_dir, handle, "decision.json")) as f:
        decision = json.load(f)
    if decision.get("error"):
        return {"error": decision["error"]}
    disposition = {
        "kind": decision["kind"],
        "reasons": sorted(set(decision.get("reasons") or [])),
        "handoff": {"state": decision.get("handoff", "none")},
    }
    if decision["kind"] == "outcome":
        disposition["outcomeId"] = decision.get("outcomeId")
    target = decision.get("target") or None
    return {"disposition": disposition, "handoffTarget": target}


def run(payload):
    return shell.run_with(payload, {"arm": "a-codex", "mutation": None,
                                    "decider": codex_replay, "hooks": {}})
