"""RQ3 runner — three stages, governed by AMENDMENT-RQ3.md.

  --stage calls    63 model calls (21 cases x 3 repetitions) via the pinned
                   codex CLI, full retention per slot: PROMPT.md, CALL.json,
                   last-message.txt, stdout.raw, stderr.raw, decision.json.
                   Each call runs in an EMPTY working directory (the model
                   can read nothing — opacity is mechanical, not trust).
  --stage replay   3 Forge runs of cohort2.yaml with agents/arm_a_codex
                   deterministically replaying the retained decisions.
  --stage analyze  registered endpoints vs the pinned-evaluator goldens;
                   writes RESULTS-RQ3.json.

Failure rules (registered): one retry on a nonzero codex exit (transport);
schema-invalid or non-JSON output is model behavior — recorded as
model-failure with no retry, counted as disagreement (intent to treat).

Stdlib only. Env: JPACK_BIN (analyze: golden digests), FORGE_VENV_PY
(replay), STUDY_DIR implied. Run under CPython 3.12.11.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
ATTEMPT = STUDY / "results" / "rq3-attempt-001"
CODEX = "/home/onword/.local/bin/codex"
CODEX_SHA256 = "a2a05dafaa1acb002a45eaec0a462de5b13694fcfcd7bc43305f14781ce7be14"
MODEL = "gpt-5.6-sol"
EFFORT = "ultra"
REPS = 3
TIMEOUT = 600
PACK_SHORT = {
    "data-request-intake-triage.json": "triage",
    "decimal-threshold-fee.json": "fee",
    "direct-exception-escalation.json": "direct",
    "partial-trigger-conflict.json": "partial",
    "exception-force-outcome.json": "xforce",
    "exception-suppress-rule.json": "xsuppress",
}
REASONS = {"not-applicable", "missing-required-evidence", "unknown",
           "conflict", "no-match", "exception-escalation"}

PROMPT_TEMPLATE = """You are the deciding officer for one business case under the policy below.
Decide the case exactly as the policy directs — including declining to decide
when the policy says the case is blocked, out of scope, or undecidable.

Report your decision in this fixed vocabulary:
- "kind": "outcome" (the policy produced a definite outcome),
  "not-applicable" (the case is outside the policy's scope), or
  "unresolved" (the policy blocks the decision).
- "outcomeId": the outcome's identifier, ONLY when kind is "outcome".
- "reasons": when kind is not "outcome", the applicable subset of
  ["not-applicable","missing-required-evidence","unknown","conflict",
  "no-match","exception-escalation"]; empty when kind is "outcome".
- "handoff": "requested" if the policy routes this blocked or exceptional
  case to a configured destination (or an exception escalates it directly),
  else "none".
- "target": when handoff is "requested" and the policy configures a
  destination, {{"kind": "...", "name": "..."}} exactly as the policy names
  it; null when no destination is configured or handoff is "none".

## The policy

{policy}

## The case

Case handle: {handle}

Facts:
```json
{facts}
```

Evidence availability ("present" / "absent"; anything not listed is unknown):
{evidence}

For reference, the application maps outcomes to actions as:
```json
{action_map}
```

Respond with ONLY one JSON object, no prose, no code fence:
{{"kind": "...", "outcomeId": "... or omit", "reasons": [...], "handoff": "none|requested", "target": {{...}} or null}}
"""


def load_registry():
    return json.loads((STUDY / "scenarios" / "jps" / "cases.json").read_text())


def load_handles():
    return json.loads(
        (STUDY / "scenarios" / "rq3" / "HANDLES.json").read_text())["handles"]


def build_prompt(case, action_map):
    prose = (STUDY / "scenarios" / "rq3" / "policy-prose" /
             (PACK_SHORT[case["pack"]] + ".md")).read_text()
    handles = load_handles()
    evidence = case["evidence"]
    evidence_text = ("```json\n" + json.dumps(evidence, indent=2, sort_keys=True)
                     + "\n```" if evidence else
                     "No evidence availability information was provided.")
    return PROMPT_TEMPLATE.format(
        policy=prose, handle=handles[case["id"]],
        facts=json.dumps(case["facts"], indent=2, sort_keys=True),
        evidence=evidence_text,
        action_map=json.dumps(action_map, indent=2, sort_keys=True))


def validate_decision(doc, action_map):
    if not isinstance(doc, dict):
        return "not an object"
    kind = doc.get("kind")
    if kind not in ("outcome", "not-applicable", "unresolved"):
        return "bad kind"
    if kind == "outcome":
        if doc.get("outcomeId") not in action_map:
            return "unknown outcomeId"
    else:
        reasons = doc.get("reasons")
        if not isinstance(reasons, list) or not reasons or \
                not set(reasons) <= REASONS:
            return "bad reasons"
    if doc.get("handoff") not in ("none", "requested"):
        return "bad handoff"
    target = doc.get("target")
    if target is not None and (not isinstance(target, dict)
                               or set(target) != {"kind", "name"}):
        return "bad target"
    return None


def one_call(prompt, slot):
    slot.mkdir(parents=True, exist_ok=True)
    (slot / "PROMPT.md").write_text(prompt)
    last = slot / "last-message.txt"
    cmd = [CODEX, "exec", "-s", "read-only", "--skip-git-repo-check",
           "-m", MODEL, "-c", 'model_reasoning_effort="{}"'.format(EFFORT),
           "-o", str(last), "-"]
    attempts = []
    for attempt in (1, 2):
        with tempfile.TemporaryDirectory() as empty_cwd:
            proc = subprocess.run(cmd, input=prompt.encode(), cwd=empty_cwd,
                                  capture_output=True, timeout=TIMEOUT)
        attempts.append(proc.returncode)
        (slot / "stdout.raw").write_bytes(proc.stdout)
        (slot / "stderr.raw").write_bytes(proc.stderr)
        if proc.returncode == 0:
            break
    (slot / "CALL.json").write_text(json.dumps({
        "argv": cmd, "codexSha256": CODEX_SHA256, "model": MODEL,
        "effort": EFFORT, "exitCodes": attempts,
        "promptSha256": hashlib.sha256(prompt.encode()).hexdigest(),
    }, indent=2, sort_keys=True) + "\n")
    if attempts[-1] != 0:
        return {"error": "model-failure", "detail": "transport exit {}".format(attempts[-1])}
    try:
        text = last.read_text().strip()
        if text.startswith("```"):
            text = text.strip("`\n")
            text = text[text.index("{"):]
        doc = json.loads(text[text.index("{"):text.rindex("}") + 1])
    except Exception as exc:
        return {"error": "model-failure", "detail": "unparsable: {}".format(exc)}
    return doc


def stage_calls():
    if hashlib.sha256(Path(CODEX).read_bytes()).hexdigest() != CODEX_SHA256:
        sys.exit("codex binary does not match the registered digest")
    registry = load_registry()
    for rep in range(1, REPS + 1):
        rep_dir = ATTEMPT / "authoring" / "rep-{:02d}".format(rep)
        for case in registry["cases"]:
            action_map = registry["packActionMaps"][case["pack"]]
            handle = load_handles()[case["id"]]
            slot = rep_dir / handle
            if (slot / "decision.json").exists():
                continue  # slots are immutable; resume skips completed slots
            doc = one_call(build_prompt(case, action_map), slot)
            if "error" not in doc:
                problem = validate_decision(doc, action_map)
                if problem:
                    doc = {"error": "model-failure",
                           "detail": "schema: " + problem, "raw": doc}
            (slot / "decision.json").write_text(
                json.dumps(doc, indent=2, sort_keys=True) + "\n")
            print(rep, handle, "->",
                  doc.get("kind", doc.get("error")), flush=True)


def stage_replay():
    for rep in range(1, REPS + 1):
        out = ATTEMPT / "forge" / "rep-{:02d}".format(rep)
        env = dict(os.environ, STUDY_DIR=str(STUDY),
                   STUDY_RQ3_REP_DIR=str(ATTEMPT / "authoring" /
                                         "rep-{:02d}".format(rep)))
        cmd = [os.environ["FORGE_VENV_PY"], str(STUDY / "harness" / "run_forge.py"),
               "--pack", str(STUDY / "scenarios" / "jps" / "cohort2.yaml"),
               "--agent-module", "arm_a_codex",
               "--agents-dir", str(STUDY / "agents"),
               "--out", str(out), "--run-id", "run-001", "--tags", "cohort2"]
        proc = subprocess.run(cmd, capture_output=True, env=env, text=True)
        print("replay rep", rep, "driver exit", proc.returncode, flush=True)


def golden(case_id):
    doc = json.loads((STUDY / "goldens" / (case_id + ".evaluation.json")).read_text())
    d = doc["disposition"]
    return ({"kind": d["kind"], "outcomeId": d.get("outcomeId"),
             "reasons": sorted(d.get("reasons", [])),
             "handoff": d["handoff"]["state"]},
            (doc.get("handoffTarget") or {}).get("name"))


def stage_analyze():
    registry = load_registry()
    maps = registry["packActionMaps"]
    sys.path.insert(0, str(STUDY / "harness"))
    from generate import expected_action  # noqa: E402
    reps_out = []
    for rep in range(1, REPS + 1):
        run_dir = ATTEMPT / "forge" / "rep-{:02d}".format(rep) / "runs" / "run-001"
        counts = {"cases": 0, "agreement": 0, "target_agreement": 0,
                  "false_approval": 0, "correct_abstention": 0,
                  "correct_handoff": 0, "model_failures": 0}
        rows = {}
        for case in registry["cases"]:
            artifact = json.loads(
                (run_dir / "artifacts" / (case["id"] + ".json")).read_text())
            structured = ((artifact.get("output") or {}).get("structured")) or {}
            counts["cases"] += 1
            gold, gold_target = golden(case["id"])
            disp = structured.get("disposition")
            failure = structured.get("action", {}).get("args", {}).get(
                "kind") == "error"
            if failure or disp is None:
                counts["model_failures"] += 1
                rows[case["id"]] = {"agreement": False, "model_failure": True}
                continue
            observed = {"kind": disp["kind"], "outcomeId": disp.get("outcomeId"),
                        "reasons": sorted(disp.get("reasons", [])),
                        "handoff": disp["handoff"]["state"]}
            agree = observed == gold
            target_agree = ((structured.get("handoff_target") or {}).get("name")
                            == gold_target)
            expected = expected_action(case, maps[case["pack"]])
            calls = [s for s in artifact.get("trajectory") or []
                     if s.get("type") == "tool_call"
                     and s.get("tool") in ("execute_decision", "record_decision",
                                           "open_review")]
            actual_tool = calls[-1]["tool"] if calls else None
            counts["agreement"] += agree
            counts["target_agreement"] += target_agree
            counts["false_approval"] += (expected["tool"] != "execute_decision"
                                         and actual_tool == "execute_decision")
            if gold["kind"] != "outcome" and actual_tool != "execute_decision":
                counts["correct_abstention"] += 1
            if gold["handoff"] == "requested" and actual_tool == "open_review":
                counts["correct_handoff"] += 1
            rows[case["id"]] = {"agreement": agree, "observed": observed,
                                "golden": gold, "target_agreement": target_agree}
        reps_out.append({"rep": rep, "counts": counts, "cases": rows})
    pooled = sum(r["counts"]["agreement"] for r in reps_out)
    total = sum(r["counts"]["cases"] for r in reps_out)
    results = {"attempt": "results/rq3-attempt-001", "model": MODEL,
               "effort": EFFORT, "codexSha256": CODEX_SHA256,
               "repetitions": reps_out,
               "pooled": {"agreement": pooled, "trials": total},
               "armBReference": "primary-attempt-001: 21/21 agreement by "
                                "construction (deterministic evaluator)"}
    (STUDY / "RESULTS-RQ3.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n")
    for r in reps_out:
        print("rep", r["rep"], r["counts"])
    print("pooled agreement: {}/{}".format(pooled, total))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True,
                        choices=["calls", "replay", "analyze"])
    args = parser.parse_args()
    {"calls": stage_calls, "replay": stage_replay,
     "analyze": stage_analyze}[args.stage]()


if __name__ == "__main__":
    main()
