"""Study gate — orchestrates the offline batch and adjudicates detection.

Round-2 rework. Protocol-facing verdict literals are defined ONCE here and
quoted exactly in PREREGISTRATION.md §5:

    VERDICT_INVALID   "R1 inconclusive — pipeline-invalid"
    VERDICT_HOLDS     "R1 holds"
    VERDICT_FALSIFIED "R1 falsified"

Channels:

VALIDITY (global): integrity is the first recorded validity row (never a
pre-record crash); per run — artifact set AND score set exactly equal the
scheduled case set, every artifact completed, zero scorer errors, driver exit
consistent (4 iff safety violations; 3/5 always invalid); cohort 1
additionally asserts the registered judge-unscored metric set and zero
deterministic scorer errors; the repeat check must report exactly 3 complete,
byte-identical runs; pristine Arm B must be clean per case and the pristine
packs test must pass. Any failure => VERDICT_INVALID, terminal for the
attempt: computable divergences are still reported descriptively, and no
rerun replaces the attempt (the root must not pre-exist; ATTEMPT.json marks
it before anything else runs).

DETECTION (per mutation per case, completed artifacts only):
  J  packs-test rows failing under the substituted mutated pack, or the
     artifact recording evaluator refusal class "pack-not-conformant".
  F  failed registered metrics; on cells marked F_requires_blocking only a
     failed metric with blocking == true counts. The unfiltered and counted
     metric lists are both retained with {name, passed, blocking}.
  G  disposition-vs-golden diff or action-vs-expectation diff.
An incomplete or missing artifact makes the cell NOT-ADJUDICATED (never a
false or true detection) and the batch invalid.

HOLDOUTS: MATRIX-HOLDOUT.json cells (reviewer-authored) are merged only under
--include-holdout, which is REFUSED while PREREGISTRATION.md is a DRAFT —
their first execution is the post-freeze registered run.

Stdlib only. Env: FORGE_VENV_PY, JPACK_BIN, FORGE_CLONE.
Run: python3 harness/gate.py --pilot-root <nonexistent dir> [--include-holdout]
"""

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDY / "harness"))
from generate import expected_action, SHORT  # noqa: E402

VERDICT_INVALID = "R1 inconclusive — pipeline-invalid"
VERDICT_HOLDS = "R1 holds"
VERDICT_FALSIFIED = "R1 falsified"
REPEATS = 3
ACTION_TOOLS = {"execute_decision", "record_decision", "open_review"}
BLOCKING_REFUSAL_CLASS = "pack-not-conformant"
ARMS = ["arm_b", "arm_a_oracle", "arm_a_adversary"]
UPSTREAM_PACKS = {"upstream-core-launch": "core-launch.yaml",
                  "upstream-security-launch": "security-launch.yaml"}
JUDGE_METRICS = {
    "task_completion", "output_correctness", "synthesis_quality",
    "clarification_quality", "refusal_quality", "recovery_quality",
    "blast_radius_accuracy", "verification_quality", "hypothesis_quality",
    "evidence_grounding", "hallucination_rate",
    "policy_adherence", "retry_discipline",  # hybrid: gate unreachable offline
}


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


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


def check_validity(name, run_exit, scores, artifacts, expected_ids, upstream=False):
    problems = []
    if set(artifacts) != set(expected_ids):
        problems.append("artifact set != scheduled set (missing: {}, extra: {})".format(
            sorted(set(expected_ids) - set(artifacts)),
            sorted(set(artifacts) - set(expected_ids))))
    if set(scores.get("scenario_scores") or {}) != set(expected_ids):
        problems.append("score set != scheduled set")
    incomplete = [c for c, a in artifacts.items() if a.get("status") != "completed"]
    if incomplete:
        problems.append("incomplete artifacts: {}".format(sorted(incomplete)))
    scorer_errors = (scores.get("study") or {}).get("scorer_errors") or []
    if scorer_errors:
        problems.append("scorer errors: {}".format(len(scorer_errors)))
    if upstream:
        for sid, sscore in (scores.get("scenario_scores") or {}).items():
            for metric, result in (sscore.get("metric_results") or {}).items():
                err = result.get("error")
                if err and (metric not in JUDGE_METRICS
                            or "judge not configured" not in err):
                    problems.append("unexpected scorer error: {}/{}".format(sid, metric))
                if not err and metric in JUDGE_METRICS and result.get("score") is None:
                    problems.append("judge metric silently unscored without the "
                                    "registered error: {}/{}".format(sid, metric))
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


def metric_triples(scores, case_id):
    metrics = (scores["scenario_scores"].get(case_id) or {}).get("metric_results") or {}
    return [{"name": name, "passed": r.get("passed"), "blocking": bool(r.get("blocking"))}
            for name, r in sorted(metrics.items())]


def f_evidence(scores, case_id, require_blocking):
    triples = metric_triples(scores, case_id)
    failed = [t for t in triples if t["passed"] is False]
    counted = [t for t in failed if t["blocking"]] if require_blocking else failed
    return failed, counted


def g_detected(case, artifact, action_map):
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


def load_matrices(include_holdout, registry):
    matrix = json.loads(
        (STUDY / "scenarios" / "mutations" / "MATRIX.json").read_text())["mutations"]
    if include_holdout:
        holdout = json.loads(
            (STUDY / "scenarios" / "mutations" / "MATRIX-HOLDOUT.json").read_text()
        )["mutations"]
        collisions = set(matrix) & set(holdout)
        if collisions:
            sys.exit("matrix collision: {}".format(sorted(collisions)))
        matrix = {**matrix, **holdout}
    tags_of = {c["id"]: "pack-" + SHORT[c["pack"]] for c in registry["cases"]}
    for name, spec in matrix.items():
        selected = set(spec["tags"].split(","))
        scheduled = {cid for cid, tag in tags_of.items()
                     if tag in selected or "cohort2" in selected}
        if set(spec["cases"]) != scheduled:
            sys.exit("mutation {} case set != tag-selected schedule "
                     "(missing {}, extra {})".format(
                         name, sorted(scheduled - set(spec["cases"])),
                         sorted(set(spec["cases"]) - scheduled)))
    return matrix


def provenance():
    pins_path = STUDY / "harness" / "PINS.json"
    clone = os.environ.get("FORGE_CLONE", "")
    head = subprocess.run(["git", "-C", clone, "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip() if clone else None
    return {
        "jpackSha256": sha256_file(os.environ["JPACK_BIN"]),
        "forgeCommit": head,
        "forgeFreezeSha256": sha256_file(STUDY / "harness" / "forge-freeze.txt"),
        "harnessPython": platform.python_version(),
        "pinsSha256": sha256_file(pins_path),
        "studyManifestSha256": sha256_file(STUDY / "harness" / "STUDY-MANIFEST.sha256"),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", required=True)
    parser.add_argument("--include-holdout", action="store_true")
    args = parser.parse_args()
    pilot_root = Path(args.pilot_root)
    if pilot_root.exists():
        sys.exit("pilot root exists — attempts are immutable, use a fresh directory")
    if args.include_holdout and "DRAFT" in (STUDY / "PREREGISTRATION.md").read_text():
        sys.exit("--include-holdout refused: PREREGISTRATION.md is still a DRAFT; "
                 "the holdouts' first execution is the post-freeze registered run")
    pilot_root.mkdir(parents=True)
    (pilot_root / "ATTEMPT.json").write_text(json.dumps(
        {"root": str(pilot_root), "includeHoldout": args.include_holdout,
         "repeats": REPEATS}, indent=2) + "\n")

    validity = []
    integrity = subprocess.run(
        [sys.executable, str(STUDY / "harness" / "integrity.py")],
        capture_output=True, text=True)
    validity.append({"run": "integrity", "valid": integrity.returncode == 0,
                     "problems": [l for l in integrity.stderr.splitlines() if l]})

    registry = json.loads((STUDY / "scenarios" / "jps" / "cases.json").read_text())
    cases = {c["id"]: c for c in registry["cases"]}
    maps = registry["packActionMaps"]
    matrix = load_matrices(args.include_holdout, registry)
    cohort2 = str(STUDY / "scenarios" / "jps" / "cohort2.yaml")

    def scheduled_ids(tags):
        selected = set(tags.split(","))
        return sorted(c["id"] for c in registry["cases"]
                      if "pack-" + SHORT[c["pack"]] in selected or "cohort2" in selected)

    adjudication = {"validity": validity, "mutations": {}, "divergences": [],
                    "notAdjudicated": [], "provenance": provenance()}

    if integrity.returncode != 0:
        adjudication["pipelineValid"] = False
        adjudication["verdict"] = VERDICT_INVALID
        (pilot_root / "ADJUDICATION.json").write_text(
            json.dumps(adjudication, indent=2, sort_keys=True) + "\n")
        print("verdict:", VERDICT_INVALID, "(integrity failed before any run)")
        return 1

    runs = {}
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
         "--pilot-root", str(pilot_root), "--repeats", str(REPEATS)],
        env=dict(os.environ, STUDY_DIR=str(STUDY)))
    runs["repeat_check"] = {"exit": repeat.returncode}
    (pilot_root / "RUNS.json").write_text(json.dumps(runs, indent=2, sort_keys=True) + "\n")

    # ---- validity channel -------------------------------------------------
    loaded = {}
    for name in ARMS + sorted(matrix):
        expected_ids = scheduled_ids("cohort2" if name in ARMS else matrix[name]["tags"])
        try:
            scores, artifacts = load_run(pilot_root / name)
            loaded[name] = (scores, artifacts)
            validity.append(check_validity(name, runs[name]["exit"], scores,
                                           artifacts, expected_ids))
        except Exception as exc:
            validity.append({"run": name, "valid": False,
                             "problems": ["run output unreadable: {}".format(exc)]})
    for run_name, pack_file in UPSTREAM_PACKS.items():
        try:
            scores, artifacts = load_run(pilot_root / run_name)
            validity.append(check_validity(run_name, runs[run_name]["exit"], scores,
                                           artifacts, upstream_scenario_ids(pack_file),
                                           upstream=True))
        except Exception as exc:
            validity.append({"run": run_name, "valid": False,
                             "problems": ["run output unreadable: {}".format(exc)]})

    repeat_row = {"run": "repeat_check", "valid": False, "problems": []}
    try:
        repeat_doc = json.loads((pilot_root / "REPEAT.json").read_text())
        if runs["repeat_check"]["exit"] != 0:
            repeat_row["problems"].append("repeat check exited non-zero")
        if repeat_doc.get("repeats") != REPEATS:
            repeat_row["problems"].append("repeats != {}".format(REPEATS))
        if not repeat_doc.get("identical"):
            repeat_row["problems"].append("repeat runs not identical")
        for detail in repeat_doc.get("runs") or []:
            if sorted(detail.get("case_ids") or []) != sorted(cases):
                repeat_row["problems"].append("repeat case ids wrong: " + detail["name"])
            if detail.get("driver_exit") not in (0, 2, 4):
                repeat_row["problems"].append("repeat driver exit: " + detail["name"])
            if detail.get("scorer_errors"):
                repeat_row["problems"].append("repeat scorer errors: " + detail["name"])
        repeat_row["valid"] = not repeat_row["problems"]
    except Exception as exc:
        repeat_row["problems"].append("REPEAT.json unreadable: {}".format(exc))
    validity.append(repeat_row)

    pristine_problems = []
    if "arm_b" in loaded:
        b_scores, b_artifacts = loaded["arm_b"]
        for case_id, case in cases.items():
            if case_id not in b_artifacts or \
                    b_artifacts[case_id].get("status") != "completed":
                pristine_problems.append(case_id)
                continue
            failed, _ = f_evidence(b_scores, case_id, False)
            if failed or g_detected(case, b_artifacts[case_id], maps[case["pack"]]):
                pristine_problems.append(case_id)
    else:
        pristine_problems.append("arm_b run unreadable")
    validity.append({"run": "arm_b-pristine-precondition",
                     "valid": not pristine_problems,
                     "problems": ["not clean: {}".format(sorted(pristine_problems))]
                     if pristine_problems else []})

    pristine_status, pristine_failing = j_failing_rows("pristine", None)
    validity.append({"run": "pristine-packs-test", "valid": pristine_status == "passed",
                     "problems": [] if pristine_status == "passed"
                     else [json.dumps(pristine_failing)]})

    pipeline_valid = all(v["valid"] for v in validity)
    adjudication["pipelineValid"] = pipeline_valid

    # ---- detection channel ------------------------------------------------
    for name, spec in sorted(matrix.items()):
        if name not in loaded:
            adjudication["mutations"][name] = {"notAdjudicated": "run unreadable"}
            adjudication["notAdjudicated"].append({"mutation": name, "case": "*"})
            continue
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
            artifact = artifacts.get(case_id)
            if artifact is None or artifact.get("status") != "completed":
                per_case[case_id] = {"adjudicated": False,
                                     "reason": "artifact missing or incomplete"}
                adjudication["notAdjudicated"].append(
                    {"mutation": name, "case": case_id})
                continue
            require_blocking = bool(reg.get("F_requires_blocking", False))
            failed, counted = f_evidence(scores, case_id, require_blocking)
            refusal = evaluator_refusal(artifact)
            observed = {
                "J": case_id in j_rows or pack_level_j
                     or refusal == BLOCKING_REFUSAL_CLASS,
                "F": bool(counted),
                "G": bool(g_detected(cases[case_id], artifact,
                                     maps[cases[case_id]["pack"]])),
            }
            expected = {layer: bool(reg.get(layer, False)) for layer in "JFG"}
            per_case[case_id] = {
                "adjudicated": True,
                "registered": expected, "observed": observed,
                "F_requires_blocking": require_blocking,
                "F_failed_metrics_all": failed,
                "F_counted_metrics": counted,
                "G_findings": g_detected(cases[case_id], artifact,
                                         maps[cases[case_id]["pack"]]),
                "evaluator_refusal": refusal,
                "agrees": observed == expected,
            }
            if observed != expected:
                adjudication["divergences"].append(
                    {"mutation": name, "case": case_id, "holdout": name.startswith("h"),
                     "registered": expected, "observed": observed})
        adjudication["mutations"][name] = {
            "packsTest": {"status": j_status, "failing": j_failing},
            "cases": per_case}

    # ---- arms report ------------------------------------------------------
    arms_report = {}
    for arm in ARMS:
        if arm not in loaded:
            arms_report[arm] = {"error": "run unreadable"}
            continue
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
        VERDICT_INVALID if not pipeline_valid
        else (VERDICT_FALSIFIED if n_div else VERDICT_HOLDS))
    (pilot_root / "ADJUDICATION.json").write_text(
        json.dumps(adjudication, indent=2, sort_keys=True) + "\n")
    (pilot_root / "ARMS.json").write_text(
        json.dumps(arms_report, indent=2, sort_keys=True) + "\n")

    print("pipeline valid:", pipeline_valid)
    for v in validity:
        if not v["valid"]:
            print("  INVALID", v["run"], v["problems"])
    for arm, rep in arms_report.items():
        print(arm, rep.get("counts", rep))
    print("divergences:", n_div, "| not adjudicated:",
          len(adjudication["notAdjudicated"]))
    for d in adjudication["divergences"]:
        print("  DIVERGENCE", d["mutation"], d["case"],
              "registered", d["registered"], "observed", d["observed"])
    print("verdict:", adjudication["verdict"])
    return 0 if (pipeline_valid and not n_div) else 1


if __name__ == "__main__":
    raise SystemExit(main())
