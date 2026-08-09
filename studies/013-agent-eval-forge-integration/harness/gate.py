"""Study gate — orchestrates the offline batch and adjudicates detection.

Round-3 rework: the gate is TOTAL. Every failure — unreadable run output,
malformed scores, a packs-test crash, an integrity refusal, a missing pin —
becomes a recorded validity row and a terminal, written adjudication; no
input can prevent the attempt record from existing. Verdict literals
(quoted exactly in PREREGISTRATION.md §5):

    VERDICT_INVALID   "R1 inconclusive — pipeline-invalid"
    VERDICT_HOLDS     "R1 holds"
    VERDICT_FALSIFIED "R1 falsified"

Two epistemic strata are reported end-to-end (round 3, R3-6): the sixteen
original cells (locked replication) and the reviewer-authored holdout cells
(prospective; merged only under --include-holdout, refused while the
preregistration status is DRAFT). Each stratum gets scheduled/adjudicated
counts, its divergences, and its own result under one global validity result.

Cohort 1 asserts the EXACT registered judge-unscored (scenario, metric) pairs
(scenarios/upstream-expected-unscored.json) with the exact error string; a
judge metric that scores, goes silent, or vanishes is an invalidity (R3-3).
The repeat check is re-validated from REPEAT.json content: exactly
repeat-01..repeat-03, artifact AND score ids equal to the full schedule,
completion, scorer errors, driver-exit consistency (R3-2).

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
from generate import expected_action, SHORT, JUDGE_METRICS  # noqa: E402,F401

VERDICT_INVALID = "R1 inconclusive — pipeline-invalid"
VERDICT_HOLDS = "R1 holds"
VERDICT_FALSIFIED = "R1 falsified"
REPEATS = 3
ACTION_TOOLS = {"execute_decision", "record_decision", "open_review"}
BLOCKING_REFUSAL_CLASS = "pack-not-conformant"
ARMS = ["arm_b", "arm_a_oracle", "arm_a_adversary"]
UPSTREAM_PACKS = {"upstream-core-launch": "core-launch.yaml",
                  "upstream-security-launch": "security-launch.yaml"}


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe(fn, *args):
    try:
        return fn(*args)
    except Exception:
        return None


def provenance():
    """Total: a missing identity yields null, never an exception (R3-1)."""
    clone = os.environ.get("FORGE_CLONE")
    return {
        "jpackSha256": safe(sha256_file, os.environ.get("JPACK_BIN", "")),
        "forgeCommit": safe(lambda: subprocess.run(
            ["git", "-C", clone, "rev-parse", "HEAD"], capture_output=True,
            text=True).stdout.strip()) if clone else None,
        "forgeFreezeSha256": safe(sha256_file, STUDY / "harness" / "forge-freeze.txt"),
        "harnessPython": platform.python_version(),
        "pinsSha256": safe(sha256_file, STUDY / "harness" / "PINS.json"),
        "studyManifestSha256": safe(
            sha256_file, STUDY / "harness" / "STUDY-MANIFEST.sha256"),
    }


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
    """Load and SHAPE-CHECK one run's outputs; raises with a reason on any defect."""
    run_dir = Path(out_dir) / "runs" / "run-001"
    if not (run_dir / "run.json").exists():
        raise ValueError("run.json missing")
    scores = json.loads((run_dir / "scores.json").read_text())
    if not isinstance(scores.get("scenario_scores"), dict):
        raise ValueError("scores.json has no scenario_scores dict")
    for sid, ss in scores["scenario_scores"].items():
        if not isinstance(ss, dict) or not isinstance(
                ss.get("metric_results"), dict):
            raise ValueError("malformed scenario score: " + sid)
    artifacts = {}
    for p in (run_dir / "artifacts").glob("*.json"):
        artifact = json.loads(p.read_text())
        if not isinstance(artifact, dict) or "status" not in artifact:
            raise ValueError("malformed artifact: " + p.stem)
        artifacts[p.stem] = artifact
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
    if set(scores.get("scenario_scores") or {}) != set(expected_ids):
        problems.append("score set != scheduled set")
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


def check_upstream_unscored(name, scores):
    """Exact registered judge-unscored pair equality (R3-3)."""
    registered = json.loads(
        (STUDY / "scenarios" / "upstream-expected-unscored.json").read_text())
    expected_error = registered["error"]
    problems = []
    observed = {}
    for sid, ss in (scores.get("scenario_scores") or {}).items():
        for metric, result in (ss.get("metric_results") or {}).items():
            err = result.get("error")
            if err is not None:
                observed.setdefault(sid, []).append(metric)
                if err != expected_error:
                    problems.append("error text != registered: {}/{}".format(sid, metric))
            elif metric in JUDGE_METRICS and result.get("score") is None:
                problems.append("judge metric silently unscored: {}/{}".format(sid, metric))
    expected_pairs = {sid: sorted(metrics)
                      for sid, metrics in registered["pairs"].items()
                      if sid in (scores.get("scenario_scores") or {})}
    observed_pairs = {sid: sorted(metrics) for sid, metrics in observed.items()}
    if observed_pairs != expected_pairs:
        problems.append("errored pairs != registered judge-unscored pairs")
    return {"run": name + "-judge-unscored", "valid": not problems,
            "problems": problems}


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
    """Total (R3-1): any crash or unparsable output becomes an 'unavailable' status."""
    try:
        proc = subprocess.run(
            [os.environ["JPACK_BIN"], "packs", "test", "--format", "json"],
            cwd=project_dir, capture_output=True, timeout=120)
        doc = json.loads(proc.stdout)
    except Exception as exc:
        return "unavailable: {}".format(exc), {}
    if proc.returncode not in (0, 1):
        return "unavailable: exit {}".format(proc.returncode), {}
    failing = {}
    for pack in doc.get("packs", []):
        rows = [r["id"] for r in pack.get("rows", []) if r.get("status") != "passed"]
        if pack.get("status") != "passed" and not rows:
            rows = ["__pack__:" + str(pack.get("detail") or pack.get("status"))]
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
            if not src.exists():
                return "unavailable: mutated pack missing", {}
            shutil.copy(src, project / "packs" / mutated_pack_name)
        return packs_test(project)


def load_matrices(include_holdout, registry):
    matrix = json.loads(
        (STUDY / "scenarios" / "mutations" / "MATRIX.json").read_text())["mutations"]
    strata = {name: "replication" for name in matrix}
    if include_holdout:
        holdout = json.loads(
            (STUDY / "scenarios" / "mutations" / "MATRIX-HOLDOUT.json").read_text()
        )["mutations"]
        collisions = set(matrix) & set(holdout)
        if collisions:
            raise ValueError("matrix collision: {}".format(sorted(collisions)))
        matrix = {**matrix, **holdout}
        strata.update({name: "holdout" for name in holdout})
    tags_of = {c["id"]: "pack-" + SHORT[c["pack"]] for c in registry["cases"]}
    for name, spec in matrix.items():
        selected = set(spec["tags"].split(","))
        scheduled = {cid for cid, tag in tags_of.items()
                     if tag in selected or "cohort2" in selected}
        if set(spec["cases"]) != scheduled:
            raise ValueError("mutation {} case set != tag-selected schedule".format(name))
    return matrix, strata


def check_repeat(pilot_root, expected_ids):
    """Deep validation of REPEAT.json content (R3-2)."""
    problems = []
    try:
        doc = json.loads((Path(pilot_root) / "REPEAT.json").read_text())
    except Exception as exc:
        return {"run": "repeat_check", "valid": False,
                "problems": ["REPEAT.json unreadable: {}".format(exc)]}
    if doc.get("repeats") != REPEATS:
        problems.append("repeats != {}".format(REPEATS))
    if not doc.get("identical"):
        problems.append("repeat runs not identical")
    details = doc.get("runs") or []
    names = [d.get("name") for d in details]
    if names != ["repeat-{:02d}".format(i + 1) for i in range(REPEATS)]:
        problems.append("repeat run names/cardinality wrong: {}".format(names))
    for detail in details:
        for key in ("artifact_ids", "score_ids"):
            if sorted(detail.get(key) or []) != sorted(expected_ids):
                problems.append("{} wrong in {}".format(key, detail.get("name")))
        if not detail.get("all_completed"):
            problems.append("not all completed in {}".format(detail.get("name")))
        if detail.get("scorer_errors"):
            problems.append("scorer errors in {}".format(detail.get("name")))
        exit_code = detail.get("driver_exit")
        safety = bool(detail.get("safety_violations"))
        if exit_code not in (0, 2, 4) or (exit_code == 4) != safety:
            problems.append("driver exit/safety inconsistent in {}".format(
                detail.get("name")))
    return {"run": "repeat_check", "valid": not problems, "problems": problems}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", required=True)
    parser.add_argument("--include-holdout", action="store_true")
    args = parser.parse_args()
    pilot_root = Path(args.pilot_root)
    if pilot_root.exists():
        sys.exit("pilot root exists — attempts are immutable, use a fresh directory")
    if args.include_holdout:
        prereg = (STUDY / "PREREGISTRATION.md").read_text()
        if re.search(r"Status:\s*DRAFT", prereg):
            sys.exit("--include-holdout refused: PREREGISTRATION.md status is DRAFT; "
                     "the holdouts' first execution is the post-freeze registered run")
    pilot_root.mkdir(parents=True)
    (pilot_root / "ATTEMPT.json").write_text(json.dumps(
        {"root": str(pilot_root), "includeHoldout": args.include_holdout,
         "repeats": REPEATS}, indent=2) + "\n")

    validity = []
    adjudication = {"validity": validity, "mutations": {}, "divergences": [],
                    "notAdjudicated": [], "provenance": provenance(),
                    "strata": {}}

    def terminal(exit_code):
        adjudication["pipelineValid"] = all(v["valid"] for v in validity)
        n_div = len(adjudication["divergences"])
        adjudication["verdict"] = (
            VERDICT_INVALID if not adjudication["pipelineValid"]
            else (VERDICT_FALSIFIED if n_div else VERDICT_HOLDS))
        (pilot_root / "ADJUDICATION.json").write_text(
            json.dumps(adjudication, indent=2, sort_keys=True) + "\n")
        print("pipeline valid:", adjudication["pipelineValid"])
        for v in validity:
            if not v["valid"]:
                print("  INVALID", v["run"], v["problems"])
        print("divergences:", n_div, "| not adjudicated:",
              len(adjudication["notAdjudicated"]))
        for d in adjudication["divergences"]:
            print("  DIVERGENCE", d["mutation"], d["case"], "stratum", d["stratum"],
                  "registered", d["registered"], "observed", d["observed"])
        for stratum, summary in adjudication["strata"].items():
            print("stratum", stratum, summary)
        print("verdict:", adjudication["verdict"])
        return exit_code

    integrity = subprocess.run(
        [sys.executable, str(STUDY / "harness" / "integrity.py")],
        capture_output=True, text=True)
    validity.append({"run": "integrity", "valid": integrity.returncode == 0,
                     "problems": [l for l in integrity.stderr.splitlines() if l]})
    if integrity.returncode != 0:
        return terminal(1)

    try:
        registry = json.loads((STUDY / "scenarios" / "jps" / "cases.json").read_text())
        cases = {c["id"]: c for c in registry["cases"]}
        maps = registry["packActionMaps"]
        matrix, strata_of = load_matrices(args.include_holdout, registry)
    except Exception as exc:
        validity.append({"run": "study-inputs", "valid": False,
                         "problems": ["registry/matrix unreadable: {}".format(exc)]})
        return terminal(1)
    cohort2 = str(STUDY / "scenarios" / "jps" / "cohort2.yaml")

    def scheduled_ids(tags):
        selected = set(tags.split(","))
        return sorted(c["id"] for c in registry["cases"]
                      if "pack-" + SHORT[c["pack"]] in selected or "cohort2" in selected)

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
                                           artifacts, upstream_scenario_ids(pack_file)))
            validity.append(check_upstream_unscored(run_name, scores))
        except Exception as exc:
            validity.append({"run": run_name, "valid": False,
                             "problems": ["run output unreadable: {}".format(exc)]})
    if runs["repeat_check"]["exit"] != 0:
        validity.append({"run": "repeat_check-exit", "valid": False,
                         "problems": ["repeat check exited non-zero"]})
    validity.append(check_repeat(pilot_root, sorted(cases)))

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
                     else [str(pristine_status), json.dumps(pristine_failing)]})

    # ---- detection channel ------------------------------------------------
    strata_summary = {"replication": {"scheduled": 0, "adjudicated": 0,
                                      "divergences": 0},
                      "holdout": {"scheduled": 0, "adjudicated": 0,
                                  "divergences": 0}}
    for name, spec in sorted(matrix.items()):
        stratum = strata_of[name]
        strata_summary[stratum]["scheduled"] += len(spec["cases"])
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
        j_unavailable = str(j_status).startswith("unavailable")
        if j_unavailable:
            validity.append({"run": "packs-test-" + name, "valid": False,
                             "problems": [str(j_status)]})
        j_rows = {r for rows in j_failing.values() for r in rows}
        pack_level_j = any(r.startswith("__pack__") for r in j_rows)

        per_case = {}
        for case_id, reg in spec["cases"].items():
            artifact = artifacts.get(case_id)
            if artifact is None or artifact.get("status") != "completed" \
                    or (j_unavailable and mutated):
                per_case[case_id] = {"adjudicated": False,
                                     "reason": "artifact missing/incomplete or "
                                               "packs-test unavailable"}
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
            strata_summary[stratum]["adjudicated"] += 1
            per_case[case_id] = {
                "adjudicated": True, "stratum": stratum,
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
                strata_summary[stratum]["divergences"] += 1
                adjudication["divergences"].append(
                    {"mutation": name, "case": case_id, "stratum": stratum,
                     "registered": expected, "observed": observed})
        adjudication["mutations"][name] = {
            "stratum": stratum,
            "packsTest": {"status": j_status, "failing": j_failing},
            "cases": per_case}

    for stratum, summary in strata_summary.items():
        if summary["scheduled"] == 0:
            summary["result"] = "not-scheduled"
        elif summary["adjudicated"] < summary["scheduled"]:
            summary["result"] = "incomplete"
        else:
            summary["result"] = "holds" if summary["divergences"] == 0 else "falsified"
    adjudication["strata"] = strata_summary

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
    (pilot_root / "ARMS.json").write_text(
        json.dumps(arms_report, indent=2, sort_keys=True) + "\n")
    for arm, rep in arms_report.items():
        print(arm, rep.get("counts", rep))

    exit_code = terminal(0)
    if not adjudication["pipelineValid"] or adjudication["divergences"]:
        return 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
