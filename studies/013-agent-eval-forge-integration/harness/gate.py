"""Study gate — orchestrates the offline pilot batch and adjudicates detection.

Layers adjudicated per mutation per case (observed, then compared to the
REGISTERED expectations in scenarios/mutations/MATRIX.json):

  J  judgment tooling: `jpack packs test` on a temp project with the mutated
     pack substituted (pack mutations), or an evaluation error in the artifact
     (m15a). Integration mutations run against pristine packs, so J is
     observed from the pristine matrix staying green.
  F  Forge deterministic scorers via the driver: any registered metric with
     passed == false on the case (metric-level, warns count).
  G  this gate: disposition-vs-golden diff, action-vs-expected diff, or a
     missing disposition where the golden has one.

Every divergence between registered and observed is loud (exit non-zero) and
recorded — in either direction. Unchanged cases are within-run controls.

Stdlib only; shells out to the Forge venv driver and the pinned jpack.
Env: FORGE_VENV_PY, JPACK_BIN, STUDY_DIR optional (defaults to repo layout).

Run: python3 harness/gate.py --pilot-root <dir> [--skip-runs]
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDY / "harness"))
from generate import expected_action  # noqa: E402

ACTION_TOOLS = {"execute_decision", "record_decision", "open_review"}
ARMS = ["arm_b", "arm_a_oracle", "arm_a_adversary"]


def run_driver(pilot_root, module, run_name, tags="cohort2"):
    env = dict(os.environ, STUDY_DIR=str(STUDY))
    out = Path(pilot_root) / run_name
    cmd = [os.environ["FORGE_VENV_PY"], str(STUDY / "harness" / "run_forge.py"),
           "--pack", str(STUDY / "scenarios" / "jps" / "cohort2.yaml"),
           "--agent-module", module, "--agents-dir", str(STUDY / "agents"),
           "--out", str(out), "--run-id", "run-001", "--tags", tags]
    proc = subprocess.run(cmd, capture_output=True, env=env, text=True)
    return {"exit": proc.returncode, "out": str(out), "stdout": proc.stdout[-2000:]}


def load_run(out_dir):
    run_dir = Path(out_dir) / "runs" / "run-001"
    scores = json.loads((run_dir / "scores.json").read_text())
    artifacts = {}
    for path in (run_dir / "artifacts").glob("*.json"):
        artifacts[path.stem] = json.loads(path.read_text())
    return scores, artifacts


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


def f_detected(scores, case_id):
    metrics = (scores["scenario_scores"].get(case_id) or {}).get("metric_results") or {}
    return sorted(name for name, r in metrics.items() if r.get("passed") is False)


def g_detected(case, artifact, action_map):
    disp = observed_disposition(artifact)
    gold = golden(case["id"])
    expected = expected_action(case, action_map)
    actual = observed_action(artifact)
    findings = []
    if artifact.get("status") != "completed":
        findings.append("artifact-not-completed")
    if disp is None:
        findings.append("disposition-missing-golden-present")
    elif disp != gold:
        findings.append("disposition-diff")
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
            src = STUDY / "scenarios" / "mutations" / "packs" / (mutation + "-" + mutated_pack_name)
            shutil.copy(src, project / "packs" / mutated_pack_name)
        return packs_test(project)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", required=True)
    parser.add_argument("--skip-runs", action="store_true")
    args = parser.parse_args()
    pilot_root = Path(args.pilot_root)
    pilot_root.mkdir(parents=True, exist_ok=True)

    if subprocess.run([sys.executable, str(STUDY / "harness" / "integrity.py")]).returncode:
        sys.exit("integrity check failed")

    registry = json.loads((STUDY / "scenarios" / "jps" / "cases.json").read_text())
    cases = {c["id"]: c for c in registry["cases"]}
    maps = registry["packActionMaps"]
    matrix = json.loads(
        (STUDY / "scenarios" / "mutations" / "MATRIX.json").read_text())["mutations"]

    runs = {}
    if not args.skip_runs:
        for arm in ARMS:
            runs[arm] = run_driver(pilot_root, arm, arm)
        for name, spec in sorted(matrix.items()):
            runs[name] = run_driver(pilot_root, spec["agent_module"], name,
                                    tags=spec["tags"].replace("pack-", "pack-"))
        (pilot_root / "RUNS.json").write_text(json.dumps(runs, indent=2, sort_keys=True) + "\n")

    pristine_status, pristine_failing = j_failing_rows("pristine", None)

    adjudication = {"pristinePacksTest": {"status": pristine_status,
                                          "failing": pristine_failing},
                    "mutations": {}, "divergences": []}
    for name, spec in sorted(matrix.items()):
        scores, artifacts = load_run(pilot_root / name)
        mutated = None
        if spec["kind"] != "integration":
            sample = STUDY / "scenarios" / "mutations" / "packs"
            hits = list(sample.glob(name + "-*.json"))
            mutated = hits[0].name[len(name) + 1:] if hits else None
        j_status, j_failing = j_failing_rows(name, mutated) if mutated else (
            pristine_status, pristine_failing)
        j_rows = {r for rows in j_failing.values() for r in rows}

        per_case = {}
        for case_id, reg in spec["cases"].items():
            if case_id not in artifacts:
                continue
            observed = {
                "J": case_id in j_rows or any(r.startswith("__pack__") for r in j_rows),
                "F": bool(f_detected(scores, case_id)),
                "G": bool(g_detected(cases[case_id], artifacts[case_id], maps[cases[case_id]["pack"]])),
            }
            expected = {layer: bool(reg.get(layer, False)) for layer in "JFG"}
            per_case[case_id] = {
                "registered": expected, "observed": observed,
                "F_metrics": f_detected(scores, case_id),
                "G_findings": g_detected(cases[case_id], artifacts[case_id],
                                         maps[cases[case_id]["pack"]]),
                "agrees": observed == expected,
            }
            if observed != expected:
                adjudication["divergences"].append(
                    {"mutation": name, "case": case_id,
                     "registered": expected, "observed": observed})
        adjudication["mutations"][name] = {"packsTest": {"status": j_status,
                                                         "failing": j_failing},
                                           "cases": per_case}

    arms_report = {}
    for arm in ARMS:
        scores, artifacts = load_run(pilot_root / arm)
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
            abstain_expected = gold["kind"] != "outcome"
            handoff_expected = gold["handoff"] == "requested"
            rows[case_id] = {"decision_correct": decision_ok, "action_correct": action_ok,
                             "false_approval": false_approval,
                             "forge_status": (scores["scenario_scores"].get(case_id) or {}).get("status")}
            counts["decision_correct"] += decision_ok
            counts["action_correct"] += action_ok
            counts["false_approval"] += false_approval
            if abstain_expected and bool(actual) and actual["tool"] != "execute_decision":
                counts["correct_abstention"] += 1
            if handoff_expected and bool(actual) and actual["tool"] == "open_review":
                counts["correct_handoff"] += 1
        arms_report[arm] = {"counts": counts, "cases": rows}

    (pilot_root / "ADJUDICATION.json").write_text(
        json.dumps(adjudication, indent=2, sort_keys=True) + "\n")
    (pilot_root / "ARMS.json").write_text(
        json.dumps(arms_report, indent=2, sort_keys=True) + "\n")

    n_div = len(adjudication["divergences"])
    print("pristine packs test:", pristine_status)
    for arm, rep in arms_report.items():
        print(arm, rep["counts"])
    print("mutation adjudication divergences:", n_div)
    for d in adjudication["divergences"]:
        print("  DIVERGENCE", d["mutation"], d["case"],
              "registered", d["registered"], "observed", d["observed"])
    return 1 if (n_div or pristine_status != "passed") else 0


if __name__ == "__main__":
    raise SystemExit(main())
