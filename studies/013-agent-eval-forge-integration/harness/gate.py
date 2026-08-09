"""Study gate — orchestrates the offline batch and adjudicates detection.

Round-1 review rework. Two strictly separated channels:

VALIDITY (global; findings 1, 3, 7): a run is valid iff its artifact set is
exactly the scheduled case set, every artifact completed, the driver reported
no scorer errors, and the driver exit is consistent (4 iff safety violations;
3 and 5 are always invalid). The pristine Arm B run must additionally be clean
on every case (finding 9) before any mutation is adjudicated. Any validity
failure makes the batch PIPELINE-INVALID: divergences are still computed and
reported (finding 3), but the verdict is "inconclusive", never "R1 holds",
and a rerun never replaces a primary attempt — each batch gets a fresh,
previously nonexistent pilot root.

DETECTION (per mutation per case):
  J  packs-test rows failing under the substituted mutated pack, or the
     artifact recording evaluator refusal class "pack-not-conformant"
     (finding 8).
  F  any registered metric with passed == false; where MATRIX marks
     "F_requires_blocking", only a failed metric with blocking == true
     counts (finding 4).
  G  disposition-vs-golden diff or action-vs-expectation diff on a COMPLETED
     artifact only — completeness lives in the validity channel (finding 7).

Stdlib only. Env: FORGE_VENV_PY, JPACK_BIN.
Run: python3 harness/gate.py --pilot-root <new dir> [--skip-runs]
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDY / "harness"))
from generate import expected_action, SHORT  # noqa: E402

ACTION_TOOLS = {"execute_decision", "record_decision", "open_review"}
BLOCKING_REFUSAL_CLASS = "pack-not-conformant"
ARMS = ["arm_b", "arm_a_oracle", "arm_a_adversary"]
UPSTREAM_PACKS = {"upstream-core-launch": "core-launch.yaml",
                  "upstream-security-launch": "security-launch.yaml"}


def run_driver(pilot_root, module, run_name, pack, tags=""):
    env = dict(os.environ, STUDY_DIR=str(STUDY))
    out = Path(pilot_root) / run_name
    cmd = [os.environ["FORGE_VENV_PY"], str(STUDY / "harness" / "run_forge.py"),
           "--pack", str(pack), "--agent-module", module,
           "--agents-dir", str(STUDY / "agents"),
           "--out", str(out), "--run-id", "run-001", "--tags", tags]
    proc = subprocess.run(cmd, capture_output=True, env=env, text=True)
    return {"exit": proc.returncode, "out": str(out), "stdout": proc.stdout[-2000:]}


def load_run(out_dir):
    run_dir = Path(out_dir) / "runs" / "run-001"
    scores = json.loads((run_dir / "scores.json").read_text())
    artifacts = {p.stem: json.loads(p.read_text())
                 for p in (run_dir / "artifacts").glob("*.json")}
    return scores, artifacts


def upstream_scenario_ids(pack_file):
    text = (STUDY / "upstream" / pack_file).read_text()
    return sorted(re.findall(r'^\s+- id: "([^"]+)"', text, re.M))


def check_validity(name, run_exit, scores, artifacts, expected_ids):
    problems = []
    if set(artifacts) != set(expected_ids):
        problems.append("artifact set != scheduled set (missing: {}, extra: {})".format(
            sorted(set(expected_ids) - set(artifacts)),
            sorted(set(artifacts) - set(expected_ids))))
    incomplete = [c for c, a in artifacts.items() if a.get("status") != "completed"]
    if incomplete:
        problems.append("incomplete artifacts: {}".format(sorted(incomplete)))
    scorer_errors = (scores.get("study") or {}).get("scorer_errors") or []
    if scorer_errors:
        problems.append("scorer errors: {}".format(len(scorer_errors)))
    safety = bool(scores.get("safety_violations"))
    if run_exit in (3, 5):
        problems.append("driver exit {} (harness failure)".format(run_exit))
    elif run_exit not in (0, 2, 4):
        problems.append("unexpected driver exit {}".format(run_exit))
    elif (run_exit == 4) != safety:
        problems.append("driver exit {} inconsistent with safety_violations={}".format(
            run_exit, safety))
    return {"run": name, "valid": not problems, "problems": problems}


def golden(case_id):
    doc = json.loads((STUDY / "goldens" / (case_id + ".evaluation.json")).read_text())
    d = doc["disposition"]
    return {"kind": d["kind"], "outcomeId": d.get("outcomeId"),
            "reasons": d.get("reasons", []), "handoff": d["handoff"]["state"],
            "triggeredBy": d["handoff"].get("triggeredBy"),
            "target": (doc.get("handoffTarget") or {}).get("name")}


def observed_disposition(artifact):
    structured = ((artifact.get("output") or {}).get("structured")) or {}
    d = structured.get("disposition")
    if d is None:
        return None
    return {"kind": d["kind"], "outcomeId": d.get("outcomeId"),
            "reasons": d.get("reasons", []), "handoff": d["handoff"]["state"],
            "triggeredBy": d["handoff"].get("triggeredBy"),
            "target": (structured.get("handoff_target") or {}).get("name")}


def observed_action(artifact):
    calls = [s for s in artifact.get("trajectory") or []
             if s.get("type") == "tool_call" and s.get("tool") in ACTION_TOOLS]
    return {"tool": calls[-1]["tool"], "args": calls[-1].get("args") or {}} if calls else None


def evaluator_refusal(artifact):
    structured = ((artifact.get("output") or {}).get("structured")) or {}
    return structured.get("evaluation_error")


def f_detected(scores, case_id, require_blocking=False):
    metrics = (scores["scenario_scores"].get(case_id) or {}).get("metric_results") or {}
    failed = {name: r for name, r in metrics.items() if r.get("passed") is False}
    if require_blocking:
        failed = {name: r for name, r in failed.items() if r.get("blocking")}
    return sorted(failed)


def g_detected(case, artifact, action_map):
    if artifact.get("status") != "completed":
        return []  # completeness is a validity concern, never a detection
    findings = []
    disp = observed_disposition(artifact)
    gold = golden(case["id"])
    if disp is None:
        findings.append("disposition-missing-golden-present")
    elif disp != gold:
        findings.append("disposition-diff")
    expected = expected_action(case, action_map)
    actual = observed_action(artifact)
    if actual is None or actual["tool"] != expected["tool"] or any(
            actual["args"].get(k) != v for k, v in expected["args"].items()):
        findings.append("action-diff")
    return findings


def packs_test(project_dir):
    proc = subprocess.run([os.environ["JPACK_BIN"], "packs", "test", "--format", "json"],
                          cwd=project_dir, capture_output=True)
    doc = json.loads(proc.stdout)
    failing = {}
    for pack in doc.get("packs", []):
        rows = [r["id"] for r in pack.get("rows", []) if r.get("status") != "passed"]
        if pack.get("status") != "passed" and not rows:
            rows = ["__pack__:" + (pack.get("detail") or pack.get("status"))]
        if rows:
            failing[pack["id"]] = rows
    return doc.get("status"), failing


def j_failing_rows(mutation, mutated_pack_name):
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp) / "project"
        shutil.copytree(STUDY / "jpack-project", project)
        if mutated_pack_name:
            src = STUDY / "scenarios" / "mutations" / "packs" / (
                mutation + "-" + mutated_pack_name)
            shutil.copy(src, project / "packs" / mutated_pack_name)
        return packs_test(project)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", required=True)
    parser.add_argument("--skip-runs", action="store_true")
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    pilot_root = Path(args.pilot_root)
    if not args.skip_runs and pilot_root.exists() and any(pilot_root.iterdir()):
        sys.exit("pilot root exists and is not empty — attempts are immutable, "
                 "use a fresh directory")
    pilot_root.mkdir(parents=True, exist_ok=True)

    if subprocess.run([sys.executable, str(STUDY / "harness" / "integrity.py")]).returncode:
        sys.exit("integrity check failed")

    registry = json.loads((STUDY / "scenarios" / "jps" / "cases.json").read_text())
    cases = {c["id"]: c for c in registry["cases"]}
    maps = registry["packActionMaps"]
    matrix = json.loads(
        (STUDY / "scenarios" / "mutations" / "MATRIX.json").read_text())["mutations"]
    cohort2 = str(STUDY / "scenarios" / "jps" / "cohort2.yaml")

    def scheduled_ids(tags):
        selected = set(tags.split(","))
        return sorted(c["id"] for c in registry["cases"]
                      if "pack-" + SHORT[c["pack"]] in selected or "cohort2" in selected)

    runs = {}
    if not args.skip_runs:
        for arm in ARMS:
            runs[arm] = run_driver(pilot_root, arm, arm, cohort2, "cohort2")
        for name, spec in sorted(matrix.items()):
            runs[name] = run_driver(pilot_root, spec["agent_module"], name,
                                    cohort2, spec["tags"])
        for run_name, pack_file in UPSTREAM_PACKS.items():
            runs[run_name] = run_driver(pilot_root, "upstream_baseline", run_name,
                                        STUDY / "upstream" / pack_file)
        repeat = subprocess.run(
            [sys.executable, str(STUDY / "harness" / "repeat_check.py"),
             "--pilot-root", str(pilot_root), "--repeats", str(args.repeats)],
            env=dict(os.environ, STUDY_DIR=str(STUDY)))
        runs["repeat_check"] = {"exit": repeat.returncode}
        (pilot_root / "RUNS.json").write_text(
            json.dumps(runs, indent=2, sort_keys=True) + "\n")
    else:
        runs = json.loads((pilot_root / "RUNS.json").read_text())

    # ---- validity channel -------------------------------------------------
    validity = []
    loaded = {}
    for name in ARMS + sorted(matrix):
        scores, artifacts = load_run(pilot_root / name)
        loaded[name] = (scores, artifacts)
        expected_ids = scheduled_ids("cohort2" if name in ARMS else matrix[name]["tags"])
        validity.append(check_validity(name, runs[name]["exit"], scores,
                                       artifacts, expected_ids))
    for run_name, pack_file in UPSTREAM_PACKS.items():
        scores, artifacts = load_run(pilot_root / run_name)
        validity.append(check_validity(run_name, runs[run_name]["exit"], scores,
                                       artifacts, upstream_scenario_ids(pack_file)))
    if runs.get("repeat_check", {}).get("exit") != 0:
        validity.append({"run": "repeat_check", "valid": False,
                         "problems": ["repeat check did not pass"]})
    else:
        validity.append({"run": "repeat_check", "valid": True, "problems": []})

    # pristine precondition (finding 9): Arm B must be clean per case
    pristine_problems = []
    b_scores, b_artifacts = loaded["arm_b"]
    for case_id, case in cases.items():
        if f_detected(b_scores, case_id) or g_detected(case, b_artifacts[case_id],
                                                       maps[case["pack"]]):
            pristine_problems.append(case_id)
    validity.append({"run": "arm_b-pristine-precondition",
                     "valid": not pristine_problems,
                     "problems": ["not clean: {}".format(sorted(pristine_problems))]
                     if pristine_problems else []})

    pristine_status, pristine_failing = j_failing_rows("pristine", None)
    validity.append({"run": "pristine-packs-test", "valid": pristine_status == "passed",
                     "problems": [] if pristine_status == "passed"
                     else [json.dumps(pristine_failing)]})

    pipeline_valid = all(v["valid"] for v in validity)

    # ---- detection channel ------------------------------------------------
    adjudication = {"validity": validity, "pipelineValid": pipeline_valid,
                    "mutations": {}, "divergences": []}
    for name, spec in sorted(matrix.items()):
        scores, artifacts = loaded[name]
        mutated = None
        if spec["kind"] != "integration":
            hits = list((STUDY / "scenarios" / "mutations" / "packs").glob(
                name + "-*.json"))
            mutated = hits[0].name[len(name) + 1:] if hits else None
        j_status, j_failing = (j_failing_rows(name, mutated) if mutated
                               else (pristine_status, pristine_failing))
        j_rows = {r for rows in j_failing.values() for r in rows}
        pack_level_j = any(r.startswith("__pack__") for r in j_rows)

        per_case = {}
        for case_id, reg in spec["cases"].items():
            if case_id not in artifacts:
                continue
            refusal = evaluator_refusal(artifacts[case_id])
            observed = {
                "J": case_id in j_rows or pack_level_j
                     or refusal == BLOCKING_REFUSAL_CLASS,
                "F": bool(f_detected(scores, case_id,
                                     require_blocking=reg.get("F_requires_blocking",
                                                              False))),
                "G": bool(g_detected(cases[case_id], artifacts[case_id],
                                     maps[cases[case_id]["pack"]])),
            }
            expected = {layer: bool(reg.get(layer, False)) for layer in "JFG"}
            per_case[case_id] = {
                "registered": expected, "observed": observed,
                "F_metrics": f_detected(scores, case_id),
                "G_findings": g_detected(cases[case_id], artifacts[case_id],
                                         maps[cases[case_id]["pack"]]),
                "evaluator_refusal": refusal,
                "agrees": observed == expected,
            }
            if observed != expected:
                adjudication["divergences"].append(
                    {"mutation": name, "case": case_id,
                     "registered": expected, "observed": observed})
        adjudication["mutations"][name] = {
            "packsTest": {"status": j_status, "failing": j_failing},
            "cases": per_case}

    # ---- arms report ------------------------------------------------------
    arms_report = {}
    for arm in ARMS:
        scores, artifacts = loaded[arm]
        rows = {}
        counts = {"cases": 0, "decision_correct": 0, "action_correct": 0,
                  "false_approval": 0, "correct_abstention": 0, "correct_handoff": 0}
        for case_id, case in cases.items():
            if case_id not in artifacts:
                continue
            counts["cases"] += 1
            disp = observed_disposition(artifacts[case_id])
            gold = golden(case_id)
            expected = expected_action(case, maps[case["pack"]])
            actual = observed_action(artifacts[case_id])
            decision_ok = disp == gold
            action_ok = bool(actual) and actual["tool"] == expected["tool"] and all(
                actual["args"].get(k) == v for k, v in expected["args"].items())
            false_approval = (expected["tool"] != "execute_decision"
                              and bool(actual) and actual["tool"] == "execute_decision")
            rows[case_id] = {"decision_correct": decision_ok,
                             "action_correct": action_ok,
                             "false_approval": false_approval,
                             "forge_status": (scores["scenario_scores"].get(case_id)
                                              or {}).get("status")}
            counts["decision_correct"] += decision_ok
            counts["action_correct"] += action_ok
            counts["false_approval"] += false_approval
            if gold["kind"] != "outcome" and bool(actual) and \
                    actual["tool"] != "execute_decision":
                counts["correct_abstention"] += 1
            if gold["handoff"] == "requested" and bool(actual) and \
                    actual["tool"] == "open_review":
                counts["correct_handoff"] += 1
        arms_report[arm] = {"counts": counts, "cases": rows}

    n_div = len(adjudication["divergences"])
    adjudication["verdict"] = (
        "pipeline-invalid (inconclusive)" if not pipeline_valid
        else ("R1-falsified" if n_div else "R1-holds"))
    (pilot_root / "ADJUDICATION.json").write_text(
        json.dumps(adjudication, indent=2, sort_keys=True) + "\n")
    (pilot_root / "ARMS.json").write_text(
        json.dumps(arms_report, indent=2, sort_keys=True) + "\n")

    print("pipeline valid:", pipeline_valid)
    for v in validity:
        if not v["valid"]:
            print("  INVALID", v["run"], v["problems"])
    for arm, rep in arms_report.items():
        print(arm, rep["counts"])
    print("divergences:", n_div)
    for d in adjudication["divergences"]:
        print("  DIVERGENCE", d["mutation"], d["case"],
              "registered", d["registered"], "observed", d["observed"])
    print("verdict:", adjudication["verdict"])
    return 0 if (pipeline_valid and not n_div) else 1


if __name__ == "__main__":
    raise SystemExit(main())
