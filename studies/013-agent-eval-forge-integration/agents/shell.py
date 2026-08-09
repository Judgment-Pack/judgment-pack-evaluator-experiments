"""Shared agent shell for Study 013 — both arms and every mutant run this exact code.

The shell is the study-defined integration contract around the judgment stage:

    fetch facts -> fetch evidence availability -> judgment stage -> execution mapper -> action tool

The judgment stage is the ONLY thing that differs between arms (a decider for
Arm A, the pinned jpack evaluator for Arm B). Mutants flip exactly one hook.

Stdlib only. Runs inside the pinned Agent Eval Forge venv; Forge imports the
per-arm entry module and calls run(payload). Environment:
  STUDY_DIR   study root (locates packs/ and scenarios/jps/fixtures/)
  JPACK_BIN   pinned evaluator binary (Arm B only)

JPS vocabulary note: disposition kinds are outcome / not-applicable / unresolved;
a handoff request is an orthogonal axis (handoff.state == "requested"). There is
no "deny" or "escalate" disposition — outcome ids are pack-authored. The mapper
below is the study's integration contract, not a spec requirement: JPS Core
binds no caller (spec §6.4: an outcome is a declared result, not an
authorization to perform an external action).
"""

import json
import os
import subprocess
import tempfile

PROTECTED_TOOL = "execute_decision"
ACTION_TOOLS = (PROTECTED_TOOL, "record_decision", "open_review")


def _study_dir():
    d = os.environ.get("STUDY_DIR")
    if not d:
        raise RuntimeError("STUDY_DIR is not set")
    return d


def _load_cases():
    with open(os.path.join(_study_dir(), "scenarios", "jps", "cases.json")) as f:
        return json.load(f)


def _fixture(payload, tool):
    fixtures_dir = payload.get("_fixtures_dir") or os.path.join(
        _study_dir(), "scenarios", "jps", "fixtures"
    )
    with open(os.path.join(fixtures_dir, tool + ".json")) as f:
        return json.load(f)["return"]


def map_disposition_to_action(case_id, disposition, handoff_target, action_map):
    """The execution mapper — the study's integration contract.

    1. handoff requested        -> open_review (a request routes to a human/queue)
    2. kind outcome             -> per-pack action map: execute:<name> or record
    3. otherwise (no handoff)   -> record_decision with kind + reasons (abstain)
    """
    kind = disposition["kind"]
    reasons = "+".join(disposition.get("reasons", []))
    if disposition.get("handoff", {}).get("state") == "requested":
        target = (handoff_target or {}).get("name", "unspecified")
        return {
            "tool": "open_review",
            "args": {"case_id": case_id, "kind": kind, "reasons": reasons, "target": target},
        }
    if kind == "outcome":
        outcome = disposition["outcomeId"]
        mapped = action_map[outcome]
        if mapped.startswith("execute:"):
            return {
                "tool": PROTECTED_TOOL,
                "args": {"case_id": case_id, "action": mapped.split(":", 1)[1], "outcome": outcome},
            }
        return {
            "tool": "record_decision",
            "args": {"case_id": case_id, "kind": "outcome", "outcome": outcome},
        }
    return {
        "tool": "record_decision",
        "args": {"case_id": case_id, "kind": kind, "reasons": reasons},
    }


def error_action(case_id, error_class):
    """An evaluation error is not a disposition and never becomes an action."""
    return {
        "tool": "record_decision",
        "args": {"case_id": case_id, "kind": "error", "reasons": error_class},
    }


def evaluate_with_jpack(pack_path, facts, evidence):
    """Run the pinned evaluator. Returns (evaluation dict | None, error_class | None, raw stdout bytes)."""
    jpack = os.environ.get("JPACK_BIN")
    if not jpack:
        raise RuntimeError("JPACK_BIN is not set")
    cmd = [jpack, "experimental", "evaluate", pack_path, "--facts", "-", "--format", "json"]
    evidence_file = None
    try:
        if evidence is not None and evidence != {}:
            evidence_file = tempfile.NamedTemporaryFile(
                "w", suffix=".evidence.json", delete=False
            )
            json.dump(evidence, evidence_file)
            evidence_file.close()
            cmd += ["--evidence", evidence_file.name]
        proc = subprocess.run(
            cmd, input=json.dumps(facts).encode(), capture_output=True, timeout=60
        )
    finally:
        if evidence_file is not None:
            os.unlink(evidence_file.name)
    if proc.returncode == 0:
        return json.loads(proc.stdout), None, proc.stdout
    try:
        error_class = json.loads(proc.stdout or proc.stderr)["evaluationError"]["class"]
    except Exception:
        error_class = "exit-" + str(proc.returncode)
    return None, error_class, proc.stdout or proc.stderr


def run_with(payload, config):
    """config: arm (str), decider (callable | None), hooks (dict of mutation hooks)."""
    hooks = config.get("hooks", {})
    case_id = (payload.get("context") or {}).get("case_id") or payload["scenario_id"]
    registry = _load_cases()
    case = next(c for c in registry["cases"] if c["id"] == case_id)
    action_map = registry["packActionMaps"][case["pack"]]
    # Deciders and hooks receive only the public view of a case. The registered
    # expectation never crosses this boundary: a model decider must not be able
    # to read the answer key. (The scripted oracle loads expectations itself,
    # by design, as a disclosed tautological positive control.)
    case_public = {k: case[k] for k in ("id", "pack", "caseType")}
    steps = []

    facts = _fixture(payload, "fetch_case_facts")[case_id]
    steps.append({"type": "tool_call", "tool": "fetch_case_facts", "args": {"case_id": case_id}})
    steps.append({"type": "tool_result", "tool": "fetch_case_facts", "result": facts})
    evidence = _fixture(payload, "fetch_evidence_availability")[case_id]
    steps.append(
        {"type": "tool_call", "tool": "fetch_evidence_availability", "args": {"case_id": case_id}}
    )
    steps.append({"type": "tool_result", "tool": "fetch_evidence_availability", "result": evidence})
    if evidence == {}:
        evidence = None

    if "pre_facts" in hooks:
        facts = hooks["pre_facts"](case_public, facts)
    if "pre_evidence" in hooks:
        evidence = hooks["pre_evidence"](case_public, evidence)

    disposition = None
    evaluation = None
    error_class = None
    if config["arm"] == "b":
        pack_path = os.path.join(_study_dir(), "packs", case["pack"])
        if "pack_override" in hooks:
            pack_path = hooks["pack_override"](case_public, pack_path)
        evaluation, error_class, raw = evaluate_with_jpack(pack_path, facts, evidence)
        steps.append(
            {
                "type": "note",
                "content": "jpack evaluation: " + raw.decode("utf-8", "replace"),
            }
        )
        if evaluation is None:
            action = error_action(case_id, error_class)
        else:
            disposition = evaluation["disposition"]
            action = map_disposition_to_action(
                case_id, disposition, evaluation.get("handoffTarget"), action_map
            )
    else:
        decision = config["decider"](case_public, facts, evidence, action_map)
        disposition = decision["disposition"]
        decider_target = decision.get("handoffTarget")
        action = map_disposition_to_action(
            case_id, disposition, decider_target, action_map
        )

    if "post_action" in hooks:
        action = hooks["post_action"](case_public, disposition, action, action_map)

    steps.append({"type": "tool_call", "tool": action["tool"], "args": action["args"]})
    steps.append(
        {"type": "tool_result", "tool": action["tool"], "result": {"status": "recorded"}}
    )
    final = "case {}: {} via {}".format(case_id, action["tool"], config["arm"])
    steps.append({"type": "response", "content": final})

    structured = {
        "case_id": case_id,
        "arm": config["arm"],
        "mutation": config.get("mutation"),
        "evaluation_error": error_class,
        "disposition": disposition,
        "handoff_target": (evaluation.get("handoffTarget") if evaluation
                           else (decider_target if config["arm"] != "b" else None)),
        "tool_version": ((evaluation or {}).get("tool") or {}).get("version"),
        "action": action,
    }
    return {
        "schema_version": "evalforge.run_envelope.v1",
        "status": "completed",
        "output": {"final": final, "structured": structured},
        "trajectory": {"steps": steps},
        "cost": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "cost_usd": 0.0},
        "error": None,
    }
