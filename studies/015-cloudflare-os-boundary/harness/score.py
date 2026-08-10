"""The scorer — the only thing that publishes.

Adjudicates every registered cell in `harness/MATRIX.json` by deterministic recomputation
from frozen fixture bytes, and writes one attempt record:

    ATTEMPT.json         written before any cell runs, so an attempt that dies mid-flight
                         is still a recorded attempt
    RESULTS.json         per-cell layer outcomes, the registered expectation, divergence
                         flags, the pins stamp, and a validity section kept strictly
                         separate from the detection section
    DETECTION-MATRIX.md  the per-layer table, published in full whichever way it lands
                         (PREREGISTRATION section 10)

Decision rule (PREREGISTRATION section 5, ordered and exhaustive):

    1. any pipeline-invalid       -> "R1 inconclusive - pipeline-invalid"
    2. else any control-gate row
       diverging                  -> "R1 inconclusive - control gate failed"
    3. else zero endpoint
       divergences                -> "R1 holds"
    4. else                       -> "R1 falsified"

Rows whose role is `demonstration` or `descriptive` are adjudicated, published in full,
and counted toward nothing.

Freeze integrity is enforced, not declared: every non-null pin is compared against the
live artefact before anything is adjudicated — the protocol digests when filled, the
`jpack` binary digest always, the interpreter version and dependency freeze, and the cf
probe runner's apparatus self-report (node version, clone commit and cleanliness, probed
upstream file digests) against the cloudflareOs pins. The whole-study manifest is
verified as an exact set, and the frozen cell-id set and per-cell schema of the loaded
matrix are asserted. Any mismatch is terminal pipeline-invalidity. No output embeds a
timestamp or an absolute path, so two runs of the same frozen tree are byte-identical.

While `PINS.json` carries a null preregistration digest the attempt is labelled PILOT and
can never be labelled REGISTERED, and `--include-holdout` is refused mechanically: the
reviewer-authored holdout stratum may not be executed before the freeze.

Run: JPACK_BIN=... CFOS_SOURCE=... <venv>/bin/python harness/score.py --attempt-root <new directory>
"""

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDY / "adapter"))
sys.path.insert(0, str(STUDY / "harness"))

import cf_runner  # noqa: E402
import make_manifest  # noqa: E402
import verify  # noqa: E402

VERDICT_INVALID = "R1 inconclusive — pipeline-invalid"
VERDICT_VOID = "R1 inconclusive — control gate failed"
VERDICT_HOLDS = "R1 holds"
VERDICT_FALSIFIED = "R1 falsified"
NOT_ADJUDICATED = "NOT-ADJUDICATED"

CF_OUTCOMES = ("pass", "unavailable") + tuple(
    "fail:" + code for code in verify.CF_CODES
)
BINDING_OUTCOMES = ("pass",) + tuple("fail:" + code for code in verify.BINDING_CODES)
REPLAY_OUTCOMES = ("pass", "unavailable") + tuple(
    "fail:" + code for code in verify.REPLAY_CODES
)
LAYER_OUTCOMES = {
    "cf": CF_OUTCOMES,
    "binding": BINDING_OUTCOMES,
    "replay": REPLAY_OUTCOMES,
}
LAYERS = ("cf", "binding", "replay")

ROLES = ("endpoint", "control-gate", "demonstration", "descriptive")
VARIANTS = (
    "none",
    "stale-store",
    "coherent-rebuild",
    "bridge-behavior",
    "environment",
    "out-of-band",
)
ATTACKER_CAPABILITIES = ("none", "bridge", "store", "environment", "out-of-band")
PLATFORM_CHECKS = ("classifyTool", "AutoApprovalDrainer")
CELL_FIELDS = (
    "id",
    "category",
    "variant",
    "role",
    "attackerCapability",
    "registeredAbsences",
    "platformChecksEngaged",
    "construction",
    "expected",
    "note",
)
ARTIFACT_FILES = {
    "pack": "pack.json",
    "facts": "facts.json",
    "evidence": "evidence.json",
    "evaluation": "evaluation.json",
    "commitment": "commitment.json",
    "ledger": "ledger.json",
    "platform": "platform.json",
    "report": "report.json",
}

# The frozen cell-id set, asserted against the loaded matrix so a reduced or extended
# registry cannot satisfy zero divergence by shrinking the denominator.
REGISTERED_CELL_IDS = (
    "pos-baseline",
    "neg-mcp-byo-autoapply",
    "neg-mcp-nonidempotent-autoapply",
    "neg-drain-skip",
    "a01-pack-bytes-drift",
    "a02-disposition-forged",
    "a03-evaluator-digest-forged",
    "s01-conflict-as-rejected",
    "s02-unknown-auto-applied",
    "s03-opfail-as-unknown",
    "s04-approval-as-evidence",
    "s05-handoff-dropped",
    "s06-not-applicable-executed",
    "o01-observation-as-evidence",
    "b01-commitment-reuse",
    "b02-argument-drift",
    "b03-revision-drift",
    "b04-gatekeeper-substituted",
    "b05-actionkind-substituted",
    "b06-unbound-execution",
    "d01-dependent-simulated-write",
    "d02-simulated-as-committed",
    "m01-readonly-bypass",
    "m02-ambiguous-commit",
)


class PipelineInvalid(RuntimeError):
    """An attempt-scope condition that forbids adjudication."""


def cell_directory(cell_id):
    if cell_id == "pos-baseline":
        return STUDY / "fixtures" / "baseline"
    return STUDY / "fixtures" / "mutations" / cell_id


# --------------------------------------------------------------------------
# freeze integrity (validity channel, before any cell runs)
# --------------------------------------------------------------------------

def pip_freeze_sha256():
    completed = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"], capture_output=True, timeout=300
    )
    if completed.returncode != 0:
        raise PipelineInvalid("pip freeze failed in the running interpreter")
    return hashlib.sha256(completed.stdout).hexdigest()


def pin_problems(pins, jpack_bin):
    """Every non-null pin compared against the live artefact. Hard, not advisory."""
    problems = []

    for member, relative in (
        ("preregistration", "PREREGISTRATION.md"),
        ("matrix", "harness/MATRIX.json"),
        ("matrixHoldout", "harness/MATRIX-HOLDOUT.json"),
        ("adapterSpec", "adapter/SPEC.md"),
    ):
        expected = (pins.get(member) or {}).get("sha256")
        if expected is None:
            continue
        path = STUDY / relative
        if not path.is_file():
            problems.append("pinned artefact is absent: " + relative)
        elif verify.sha256_file(path) != expected:
            problems.append("pinned digest does not match: " + relative)

    expected_binary = (pins.get("jpack") or {}).get("binarySha256")
    if not jpack_bin or not Path(jpack_bin).is_file():
        problems.append("JPACK_BIN is not available")
    elif expected_binary is None:
        problems.append("PINS.json carries no jpack binary digest")
    elif verify.sha256_file(jpack_bin) != expected_binary:
        problems.append("JPACK_BIN does not match the pinned digest")

    expected_python = (pins.get("harnessPython") or {}).get("version")
    if expected_python and platform.python_version() != expected_python:
        problems.append(
            "interpreter is %s, pinned %s" % (platform.python_version(), expected_python)
        )

    expected_freeze = (pins.get("harnessPython") or {}).get("pipFreezeSha256")
    if expected_freeze:
        try:
            actual_freeze = pip_freeze_sha256()
        except Exception as error:
            problems.append("dependency freeze is unreadable: %s" % error)
        else:
            if actual_freeze != expected_freeze:
                problems.append(
                    "installed dependency set does not match the pinned pip-freeze digest"
                )
    return problems


def apparatus_problems(pins, apparatus):
    """The cf runner's self-report against the cloudflareOs and harnessNode pins."""
    problems = []
    cloudflare = pins.get("cloudflareOs") or {}
    node = pins.get("harnessNode") or {}
    if not isinstance(apparatus, dict):
        return ["cf runner produced no apparatus self-report"]
    if apparatus.get("cloneCommit") != cloudflare.get("commit"):
        problems.append(
            "pinned clone is at %r, pinned commit is %r"
            % (apparatus.get("cloneCommit"), cloudflare.get("commit"))
        )
    if apparatus.get("cloneTrackedClean") is not True:
        problems.append("pinned clone's tracked tree is not clean")
    if apparatus.get("lockfileSha256") != cloudflare.get("lockfileSha256"):
        problems.append("pinned clone's pnpm-lock.yaml does not match the pinned digest")
    expected_node = node.get("version")
    if expected_node and apparatus.get("nodeVersion") != expected_node:
        problems.append(
            "probe node is %s, pinned %s" % (apparatus.get("nodeVersion"), expected_node)
        )
    expected_files = cloudflare.get("probedFiles") or {}
    actual_files = apparatus.get("probedFiles") or {}
    for relative in sorted(set(expected_files) | set(actual_files)):
        if expected_files.get(relative) != actual_files.get(relative):
            problems.append("probed upstream file does not match its pin: " + relative)
    return problems


def cell_schema_problems(cells, scope):
    """Per-cell schema, asserted not assumed — for both strata."""
    problems = []
    for cell in cells:
        cell_id = cell.get("id", "<unnamed>")
        missing_fields = [field for field in CELL_FIELDS if field not in cell]
        if missing_fields:
            problems.append(
                "%s%s: missing required fields %s" % (scope, cell_id, missing_fields)
            )
            continue
        if cell["role"] not in ROLES:
            problems.append(
                "%s%s: role %r is out of vocabulary" % (scope, cell_id, cell["role"])
            )
        if cell["variant"] not in VARIANTS:
            problems.append(
                "%s%s: variant %r is out of vocabulary" % (scope, cell_id, cell["variant"])
            )
        if cell["attackerCapability"] not in ATTACKER_CAPABILITIES:
            problems.append(
                "%s%s: attackerCapability %r is out of vocabulary"
                % (scope, cell_id, cell["attackerCapability"])
            )
        absences = cell["registeredAbsences"]
        if not isinstance(absences, list) or any(
            name not in ARTIFACT_FILES for name in absences
        ):
            problems.append(
                "%s%s: registeredAbsences %r is invalid" % (scope, cell_id, absences)
            )
        engaged = cell["platformChecksEngaged"]
        if not isinstance(engaged, list) or any(
            name not in PLATFORM_CHECKS for name in engaged
        ):
            problems.append(
                "%s%s: platformChecksEngaged %r is invalid" % (scope, cell_id, engaged)
            )
        expected = cell["expected"]
        if not isinstance(expected, dict) or tuple(sorted(expected)) != tuple(
            sorted(LAYERS)
        ):
            problems.append("%s%s: expected is not a three-layer object" % (scope, cell_id))
            continue
        for layer in LAYERS:
            if expected[layer] not in LAYER_OUTCOMES[layer]:
                problems.append(
                    "%s%s: expected %s outcome %r is out of vocabulary"
                    % (scope, cell_id, layer, expected[layer])
                )
    return problems


def matrix_problems(registry):
    """The frozen cell-id set and the per-cell schema, asserted not assumed."""
    problems = []
    cells = registry.get("cells")
    if not isinstance(cells, list):
        return ["matrix carries no cell list"]
    ids = [cell.get("id") for cell in cells]
    if len(ids) != len(set(ids)):
        problems.append("matrix cell ids are not unique")
    if tuple(ids) != REGISTERED_CELL_IDS:
        missing = [item for item in REGISTERED_CELL_IDS if item not in ids]
        extra = [item for item in ids if item not in REGISTERED_CELL_IDS]
        problems.append(
            "matrix cell set is not the frozen set: missing=%s unregistered=%s "
            "ordered=%s" % (missing, extra, list(ids) == list(REGISTERED_CELL_IDS))
        )
    problems.extend(cell_schema_problems(cells, ""))
    return problems


def holdout_problems(holdout):
    """Holdout schema gate: same per-cell shape, ids disjoint from the locked set."""
    problems = []
    cells = holdout.get("cells")
    if not isinstance(cells, list):
        return ["holdout carries no cell list"]
    overlap = [cell.get("id") for cell in cells if cell.get("id") in REGISTERED_CELL_IDS]
    if overlap:
        problems.append("holdout reuses locked cell ids: %s" % overlap)
    problems.extend(cell_schema_problems(cells, "holdout "))
    return problems


# --------------------------------------------------------------------------
# per-cell validity
# --------------------------------------------------------------------------

def registered_absences(cell):
    """Artifact file names the registry authorizes to be absent for this cell.

    Read from the cell's own `registeredAbsences` field and from nothing else.
    """
    return {ARTIFACT_FILES[name] for name in cell["registeredAbsences"]}


def pipeline_problems(directory, cell):
    """Validity channel (PREREGISTRATION section 6), never a detection."""
    directory = Path(directory)
    if not directory.is_dir():
        return ["cell directory is absent"]
    problems = list(verify.manifest_problems(directory))
    allowed_absent = registered_absences(cell)
    for name in verify.CELL_FILES:
        if not (directory / name).is_file() and name not in allowed_absent:
            problems.append("unregistered missing artifact: " + name)
    for name in sorted(allowed_absent):
        if (directory / name).is_file():
            problems.append("registered absence is present: " + name)
    return problems


def expected_tuple(expectation):
    combined = "pass" if all(expectation[layer] == "pass" for layer in LAYERS) else "fail"
    return dict(expectation, combined=combined)


def observed_tuple(observed):
    tuple_ = {layer: verify.outcome(observed[layer]) for layer in LAYERS}
    tuple_["combined"] = observed["combined"]
    return tuple_


def adjudicate(observed, expectation):
    """Divergences in either direction, per layer plus the derived combined."""
    expected = expected_tuple(expectation)
    seen = observed_tuple(observed)
    divergences = [
        {"layer": layer, "expected": expected[layer], "observed": seen[layer]}
        for layer in LAYERS + ("combined",)
        if seen[layer] != expected[layer]
    ]
    return expected, divergences


def vocabulary_problems(cell, observed):
    """Out-of-vocabulary observations and engagement drift are non-adjudicable."""
    problems = []
    seen = observed_tuple(observed)
    for layer in LAYERS:
        if seen[layer] not in LAYER_OUTCOMES[layer]:
            problems.append(
                "layer %s returned an outcome outside the registered vocabulary: %s"
                % (layer, seen[layer])
            )
    engaged = observed.get("cfEngaged")
    if engaged is None or sorted(engaged) != sorted(cell["platformChecksEngaged"]):
        problems.append(
            "cf runner engagement %r does not match the registered "
            "platformChecksEngaged %r" % (engaged, cell["platformChecksEngaged"])
        )
    return problems


# --------------------------------------------------------------------------
# publication
# --------------------------------------------------------------------------

def detection_matrix(rows, stratum="locked-replication"):
    lines = [
        "# Detection matrix — Study 015",
        "",
        "Per-cell, per-layer outcome adjudicated against the registered expectations",
        "(%s stratum). Every registered cell appears; nothing is" % stratum,
        "excluded. Only `endpoint` rows count toward R1; `control-gate` rows are",
        "validity gates, `demonstration` and `descriptive` rows count toward nothing.",
        "",
        "| Cell | Stratum | Role | Attacker | Engaged | CF | BINDING | REPLAY | Combined | Registered | Divergence |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        if row["status"] == NOT_ADJUDICATED:
            lines.append(
                "| `%s` | %s | %s | %s | — | — | — | — | %s | %s | pipeline-invalid |"
                % (
                    row["cell"],
                    row["stratum"],
                    row["role"],
                    row["attackerCapability"],
                    NOT_ADJUDICATED,
                    "expected " + json.dumps(row["expected"]),
                )
            )
            continue
        seen = row["observedOutcomes"]
        lines.append(
            "| `%s` | %s | %s | %s | %s | `%s` | `%s` | `%s` | `%s` | %s | %s |"
            % (
                row["cell"],
                row["stratum"],
                row["role"],
                row["attackerCapability"],
                ", ".join(row["cfEngaged"]) or "—",
                seen["cf"],
                seen["binding"],
                seen["replay"],
                seen["combined"],
                "as registered" if not row["divergences"] else "**diverges**",
                ", ".join(
                    "%s: expected `%s`, observed `%s`"
                    % (item["layer"], item["expected"], item["observed"])
                    for item in row["divergences"]
                )
                or "—",
            )
        )
    return "\n".join(lines) + "\n"


def write_outputs(attempt_root, results, rows):
    attempt_root.mkdir(parents=True, exist_ok=True)
    (attempt_root / "RESULTS.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (attempt_root / "DETECTION-MATRIX.md").write_text(
        detection_matrix(rows, results.get("stratum", "locked-replication")),
        encoding="utf-8",
    )


def terminal_invalid(attempt_root, label, problems, provenance,
                     stratum="locked-replication"):
    """Persist a terminal pipeline-invalid record. Every failure path lands here."""
    results = {
        "study": "015-cloudflare-os-boundary",
        "stratum": stratum,
        "attemptLabel": label,
        "verdict": VERDICT_INVALID,
        "provenance": provenance,
        "validity": {
            "pipelineInvalidCells": [],
            "records": [{"scope": "attempt", "problem": problem} for problem in problems],
        },
        "detection": {"cells": 0, "adjudicated": 0, "divergentCells": [], "rows": []},
    }
    write_outputs(attempt_root, results, [])
    return results


# --------------------------------------------------------------------------
# the attempt
# --------------------------------------------------------------------------

def load_registry(include_holdout):
    registry = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    holdout = None
    if include_holdout:
        holdout = json.loads(
            (STUDY / "harness" / "MATRIX-HOLDOUT.json").read_text(encoding="utf-8")
        )
    return registry, holdout


def run(attempt_root, include_holdout=False):
    attempt_root = Path(attempt_root)
    if attempt_root.exists():
        raise SystemExit("attempt root already exists: %s" % attempt_root)

    pins_path = STUDY / "harness" / "PINS.json"
    pins = json.loads(pins_path.read_text(encoding="utf-8"))
    frozen = (pins.get("preregistration") or {}).get("sha256") is not None
    label = "REGISTERED" if frozen else "PILOT"

    if include_holdout and not frozen:
        raise SystemExit(
            "--include-holdout is refused: harness/PINS.json carries a null "
            "preregistration digest, so the preregistration is still DRAFT and the "
            "reviewer-authored holdout stratum may not be executed"
        )

    attempt_root.mkdir(parents=True)
    (attempt_root / "ATTEMPT.json").write_text(
        json.dumps(
            {
                "study": "015-cloudflare-os-boundary",
                "stratum": "locked-replication",
                "attemptLabel": label,
                "includeHoldout": bool(include_holdout),
                "marker": "written before any cell ran",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    jpack_bin = os.environ.get("JPACK_BIN")
    provenance = {
        "pinsSha256": verify.sha256_file(pins_path),
        "matrixSha256": verify.sha256_file(STUDY / "harness" / "MATRIX.json"),
        "matrixHoldoutSha256": verify.sha256_file(
            STUDY / "harness" / "MATRIX-HOLDOUT.json"
        ),
        "specSha256": verify.sha256_file(STUDY / "adapter" / "SPEC.md"),
        "preregistrationSha256": verify.sha256_file(STUDY / "PREREGISTRATION.md"),
        "studyManifestSha256": (
            verify.sha256_file(make_manifest.MANIFEST_PATH)
            if make_manifest.MANIFEST_PATH.is_file()
            else None
        ),
        "jpackSha256": (
            verify.sha256_file(jpack_bin)
            if jpack_bin and Path(jpack_bin).is_file()
            else None
        ),
        "harnessPython": platform.python_version(),
    }

    try:
        registry, holdout = load_registry(include_holdout)
    except Exception as error:
        return terminal_invalid(
            attempt_root, label, ["matrix is unreadable: %s" % error], provenance
        )

    gate_problems = []
    gate_problems.extend(pin_problems(pins, jpack_bin))
    gate_problems.extend(make_manifest.manifest_problems())
    gate_problems.extend(matrix_problems(registry))
    if holdout is not None:
        gate_problems.extend(holdout_problems(holdout))
    if gate_problems:
        return terminal_invalid(attempt_root, label, gate_problems, provenance)

    cells = [dict(cell, stratum="locked-replication") for cell in registry["cells"]]
    if holdout is not None:
        cells.extend(
            dict(cell, stratum="reviewer-holdout")
            for cell in holdout.get("cells") or []
        )

    try:
        cf_verdicts = cf_runner.ceremony(
            [(cell["id"], cell_directory(cell["id"])) for cell in cells]
        )
    except Exception as error:
        return terminal_invalid(
            attempt_root,
            label,
            ["cf runner failed: %s: %s" % (type(error).__name__, error)],
            provenance,
        )
    provenance["cfApparatus"] = cf_verdicts.get("apparatus")
    apparatus_gate = apparatus_problems(pins, cf_verdicts.get("apparatus"))
    if apparatus_gate:
        return terminal_invalid(attempt_root, label, apparatus_gate, provenance)

    validity = []
    rows = []
    work_root = Path(tempfile.mkdtemp(prefix="study015-score-"))
    try:
        for cell in cells:
            row = adjudicate_cell(cell, jpack_bin, work_root, cf_verdicts, validity)
            rows.append(row)
    except Exception as error:
        return terminal_invalid(
            attempt_root,
            label,
            [item["problem"] for item in validity]
            + ["harness crashed while adjudicating: %s: %s"
               % (type(error).__name__, error)],
            provenance,
        )
    finally:
        shutil.rmtree(work_root, ignore_errors=True)

    locked = [row for row in rows if row["stratum"] == "locked-replication"]
    holdout_rows = [row for row in rows if row["stratum"] == "reviewer-holdout"]
    invalid = [row for row in rows if row["status"] == NOT_ADJUDICATED]
    diverged = [row for row in locked if row["divergences"]]
    gates = [row for row in locked if row["role"] == "control-gate"]
    endpoints = [row for row in locked if row["role"] == "endpoint"]
    failed_gates = [row for row in gates if row["divergences"]]
    diverged_endpoints = [row for row in endpoints if row["divergences"]]

    if invalid:
        verdict = VERDICT_INVALID
    elif failed_gates:
        verdict = VERDICT_VOID
    elif not diverged_endpoints:
        verdict = VERDICT_HOLDS
    else:
        verdict = VERDICT_FALSIFIED

    results = {
        "study": "015-cloudflare-os-boundary",
        "stratum": (
            "locked-replication+holdout" if include_holdout else "locked-replication"
        ),
        "attemptLabel": label,
        "verdict": verdict,
        "matrixVersion": registry["matrixVersion"],
        "provenance": provenance,
        "validity": {
            "pipelineInvalidCells": [row["cell"] for row in invalid],
            "controlGateFailures": [row["cell"] for row in failed_gates],
            "records": validity,
        },
        "detection": {
            "cells": len(locked),
            "adjudicated": len(locked)
            - len([row for row in locked if row["status"] == NOT_ADJUDICATED]),
            "endpointCells": len(endpoints),
            "endpointDivergentCells": [row["cell"] for row in diverged_endpoints],
            "divergentCells": [row["cell"] for row in diverged],
            "rows": [row for row in rows if row["stratum"] == "locked-replication"],
        },
        "holdout": (
            None
            if holdout is None
            else {
                "note": "reviewer-authored stratum, reported separately and never "
                "merged into the locked counts",
                "cells": len(holdout_rows),
                "divergentCells": [
                    row["cell"] for row in holdout_rows if row["divergences"]
                ],
                "rows": holdout_rows,
            }
        ),
    }
    write_outputs(attempt_root, results, rows)
    return results


def adjudicate_cell(cell, jpack_bin, work_root, cf_verdicts, validity):
    """One cell. Never raises: a crash here is a NOT-ADJUDICATED row."""
    shared = {
        "cell": cell["id"],
        "stratum": cell.get("stratum", "locked-replication"),
        "category": cell["category"],
        "role": cell["role"],
        "attackerCapability": cell["attackerCapability"],
        "expected": expected_tuple(cell["expected"]),
    }
    observed = None
    try:
        directory = cell_directory(cell["id"])
        problems = pipeline_problems(directory, cell)
        if not problems:
            observed = verify.verify_cell(
                directory, jpack_bin, work_root, cf_verdicts, cell_id=cell["id"]
            )
            problems = vocabulary_problems(cell, observed)
    except Exception as error:
        problems = [
            "harness raised while verifying: %s: %s" % (type(error).__name__, error)
        ]
        observed = None
    if problems:
        validity.extend({"scope": cell["id"], "problem": problem} for problem in problems)
        return dict(
            shared,
            status=NOT_ADJUDICATED,
            observed=None,
            observedOutcomes=None,
            cfEngaged=None,
            divergences=[],
            problems=problems,
        )
    expected, divergences = adjudicate(observed, cell["expected"])
    return dict(
        shared,
        status="adjudicated",
        expected=expected,
        observed=observed,
        observedOutcomes=observed_tuple(observed),
        cfEngaged=list(observed.get("cfEngaged") or []),
        divergences=divergences,
        problems=[],
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument(
        "--include-holdout",
        action="store_true",
        help="also adjudicate harness/MATRIX-HOLDOUT.json (refused before the freeze)",
    )
    arguments = parser.parse_args(argv)
    results = run(arguments.attempt_root, include_holdout=arguments.include_holdout)
    detection = results["detection"]
    print(
        "%s (%s): %d cells, %d endpoint, %d endpoint-divergent, %d pipeline-invalid"
        % (
            results["verdict"],
            results["attemptLabel"],
            detection["cells"],
            detection.get("endpointCells", 0),
            len(detection.get("endpointDivergentCells", [])),
            len(results["validity"]["pipelineInvalidCells"]),
        )
    )
    for record in results["validity"]["records"]:
        print("  validity %s: %s" % (record["scope"], record["problem"]))
    for row in detection["rows"]:
        for item in row["divergences"]:
            print(
                "  divergence %s (%s) %s: expected %s, observed %s"
                % (row["cell"], row["role"], item["layer"], item["expected"],
                   item["observed"])
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
