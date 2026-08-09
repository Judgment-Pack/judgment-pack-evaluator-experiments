"""Study driver around Agent Eval Forge — runs INSIDE the pinned Forge venv.

Uses Forge's library layers that the architecture review found trustworthy
(pack loader, Runner, artifact recording, deterministic scorers) and replaces
the layers it found defective, without modifying upstream:

  D1  `evalforge run` never exits non-zero      -> this driver owns exit codes
  D2  scoring ignores artifact.status           -> completeness asserted here,
                                                   BEFORE scores are interpreted
  D3  regression = status flips only            -> the gate diffs scores itself

Judge metrics are scored with judge=None on purpose: unknown-expected-value
metrics stay unscored rather than mock-passed. Deterministic metrics only.

Exit codes: 0 all artifacts completed and all scored metrics passed;
3 at least one artifact did not complete (harness/SUT execution failure);
2 all completed but at least one metric failed; 4 safety violation present.
"""

import argparse
import dataclasses
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack", required=True)
    parser.add_argument("--agent-module", required=True)
    parser.add_argument("--agents-dir", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--tags", default="")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    sys.path.insert(0, args.agents_dir)
    sys.path.insert(0, str(Path(__file__).resolve().parent))

    from evalforge.runner import Runner
    from evalforge.scoring.engine import ScoringEngine

    import study_scorers  # noqa: F401  registers approval_boundary_adherence

    runner = Runner(
        agent_config={"type": "python", "module": args.agent_module, "function": "run"},
        output_dir=args.out,
    )
    pack = runner.load_pack(args.pack)
    tags = [t for t in args.tags.split(",") if t]
    artifacts = runner.run_all(tags=tags or None, run_id=args.run_id)

    incomplete = [a.scenario_id for a in artifacts if a.status != "completed"]

    engine = ScoringEngine(pack)
    run_score = engine.score_run(artifacts, judge=None)
    score_doc = dataclasses.asdict(run_score)

    # A deterministic scorer that ERRORS is a harness failure, not a pass and
    # not a skip: upstream treats passed=None as neutral (defect D2's cousin),
    # so the driver refuses instead. Judge metrics are exempt by design — this
    # study scores deterministically only.
    scorer_errors = []
    for sid, sscore in score_doc.get("scenario_scores", {}).items():
        for name, result in (sscore.get("metric_results") or {}).items():
            err = result.get("error")
            if err and "judge not configured" not in err:
                scorer_errors.append({"scenario": sid, "metric": name, "error": err})
    score_doc["study"] = {
        "driver": "run_forge.py",
        "incomplete_artifacts": incomplete,
        "scorer_errors": scorer_errors,
        "agent_module": args.agent_module,
        "tags": tags,
    }
    out = Path(args.out) / "runs" / args.run_id / "scores.json"
    out.write_text(json.dumps(score_doc, indent=2, sort_keys=True, default=str) + "\n")
    totals = score_doc.get("totals", {})
    print(json.dumps({"scores": str(out), "incomplete": incomplete, "totals": totals,
                      "scorer_errors": len(scorer_errors),
                      "safety_violations": score_doc.get("safety_violations")}))

    if incomplete:
        return 3
    if scorer_errors:
        return 5
    if score_doc.get("safety_violations"):
        return 4
    if totals.get("failed"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
