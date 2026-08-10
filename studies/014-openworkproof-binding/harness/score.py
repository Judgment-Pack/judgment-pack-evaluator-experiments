"""The scorer — the only thing that publishes.

Adjudicates every registered cell in `harness/MATRIX.json` by deterministic
recomputation from frozen fixture bytes, and writes one attempt record:

    ATTEMPT.json         written before any cell runs, so an attempt that dies
                         mid-flight is still a recorded attempt
    RESULTS.json         per-cell layer outcomes, the registered expectation,
                         divergence flags, the pins stamp, and a validity section
                         kept strictly separate from the detection section
    DETECTION-MATRIX.md  the per-layer table, published in full whichever way it
                         lands (PREREGISTRATION section 10)

Decision rule (PREREGISTRATION section 5, ordered and exhaustive):

    1. any pipeline-invalid       -> "R1 inconclusive - pipeline-invalid"
    2. else any control-gate row
       diverging                  -> "R1 inconclusive - control gate failed"
    3. else zero endpoint
       divergences                -> "R1 holds"
    4. else                       -> "R1 falsified"

Rows whose role is `demonstration` or `descriptive` are adjudicated, published
in full, and counted toward nothing.

Freeze integrity is enforced, not declared. Before any cell runs the scorer
compares every non-null pin in `PINS.json` against the live artefact — the
preregistration, matrix and SPEC digests when they are filled, the `jpack`
binary digest always, the interpreter version exactly, and the installed
dependency set through `pip freeze` — verifies `harness/STUDY-MANIFEST.sha256`
as an exact set, and asserts the frozen cell-id set and per-cell schema of the
loaded matrix. Any mismatch is terminal: the attempt is pipeline-invalid and no
detection is adjudicated. Nothing in the published outputs is a timestamp or an
absolute path, so two runs of the same frozen tree are byte-identical.

While `PINS.json` carries a null preregistration digest the attempt is labelled
PILOT and can never be labelled REGISTERED (PREREGISTRATION section 6), and
`--include-holdout` is refused mechanically: the reviewer-authored holdout
stratum may not be executed before the freeze.

Run: JPACK_BIN=... python harness/score.py --attempt-root <new directory>
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

import make_manifest  # noqa: E402
import verify  # noqa: E402

VERDICT_INVALID = "R1 inconclusive — pipeline-invalid"
VERDICT_VOID = "R1 inconclusive — control gate failed"
VERDICT_HOLDS = "R1 holds"
VERDICT_FALSIFIED = "R1 falsified"
NOT_ADJUDICATED = "NOT-ADJUDICATED"

OWP_OUTCOMES = ("pass", "fail", "unavailable")
BINDING_OUTCOMES = ("pass",) + tuple("fail:" + code for code in verify.BINDING_CODES)
REPLAY_OUTCOMES = ("pass", "unavailable") + tuple(
    "fail:" + code for code in verify.REPLAY_CODES
)
LAYER_OUTCOMES = {
    "owp": OWP_OUTCOMES,
    "binding": BINDING_OUTCOMES,
    "replay": REPLAY_OUTCOMES,
}
LAYERS = ("owp", "binding", "replay")

ROLES = ("endpoint", "control-gate", "demonstration", "descriptive")
ATTACKER_CAPABILITIES = ("none", "tamper", "selective-keys", "full-keys")
CELL_FIELDS = (
    "id",
    "category",
    "variant",
    "role",
    "attackerCapability",
    "registeredAbsences",
    "construction",
    "expected",
    "note",
)
ARTIFACT_FILES = {
    "bundle": "bundle.json",
    "commitment": "commitment.json",
    "pack": "pack.json",
    "facts": "facts.json",
    "evidence": "evidence.json",
    "evaluation": "evaluation.json",
}

# The frozen cell-id set, asserted against the loaded matrix so a reduced or
# extended registry cannot satisfy zero divergence by shrinking the denominator.
REGISTERED_CELL_IDS = (
    "pos-baseline",
    "neg-signature",
    "neg-evidence-digest",
    "neg-parent-ref",
    "neg-action-param",
    "a01-pack-bytes-drift",
    "a02-pack-version-substitution",
    "a03-pack-substitution-compatible",
    "a04-commitment-packdigest-tampered",
    "a04-commitment-packdigest-resigned",
    "a05-pack-artifact-missing",
    "b06-fact-edit-same-disposition",
    "b07-facts-doc-substituted",
    "b08-same-disposition-different-facts",
    "b09-factsdigest-field-wrong",
    "c10-reject-executed",
    "c11-unresolved-executed",
    "c12-handoff-requested-executed",
    "c13-outcome-forged",
    "c14-reasons-forged",
    "c15-manual-review-unbound-execution",
    "d15-tool-tampered",
    "d15-tool-resigned",
    "d16-argument-tampered",
    "d16-argument-resigned",
    "d17-amount-tampered",
    "d17-amount-resigned",
    "d18-approve-extra-execution",
    "e19-decision-rebound",
    "e20-execution-point-divergence",
    "e21-outside-window",
    "e22-workorder-rollback",
    "e23-executable-digest-forged",
    "f23-wrong-parent-decision",
    "f24-parent-receipt-removed",
    "f25-extra-parent-inserted",
    "f26-cross-execution-receipt",
    "f27-cross-execution-evidence",
    "m28-unsigned-metadata-carriage",
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
    """SHA-256 of `pip freeze` in the interpreter that is running the scorer."""
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

    expected_freeze = (pins.get("openworkproof") or {}).get("pipFreezeSha256")
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
    for cell in cells:
        cell_id = cell.get("id", "<unnamed>")
        missing_fields = [field for field in CELL_FIELDS if field not in cell]
        if missing_fields:
            problems.append("%s: missing required fields %s" % (cell_id, missing_fields))
            continue
        if cell["role"] not in ROLES:
            problems.append("%s: role %r is out of vocabulary" % (cell_id, cell["role"]))
        if cell["attackerCapability"] not in ATTACKER_CAPABILITIES:
            problems.append(
                "%s: attackerCapability %r is out of vocabulary"
                % (cell_id, cell["attackerCapability"])
            )
        absences = cell["registeredAbsences"]
        if not isinstance(absences, list) or any(
            name not in ARTIFACT_FILES for name in absences
        ):
            problems.append("%s: registeredAbsences %r is invalid" % (cell_id, absences))
        expected = cell["expected"]
        if not isinstance(expected, dict) or tuple(sorted(expected)) != tuple(
            sorted(LAYERS)
        ):
            problems.append("%s: expected is not a three-layer object" % cell_id)
            continue
        for layer in LAYERS:
            if expected[layer] not in LAYER_OUTCOMES[layer]:
                problems.append(
                    "%s: expected %s outcome %r is out of vocabulary"
                    % (cell_id, layer, expected[layer])
                )
    return problems


# --------------------------------------------------------------------------
# per-cell validity
# --------------------------------------------------------------------------

def registered_absences(cell):
    """Artifact file names the registry authorizes to be absent for this cell.

    Read from the cell's own `registeredAbsences` field and from nothing else:
    validity is registered independently of any expected verdict, so the same
    entry can never both authorize a missing artifact and award its detection.
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
    tuple_ = {layer: observed[layer]["outcome"] for layer in LAYERS}
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


def vocabulary_problems(cell_id, observed):
    """An out-of-vocabulary observation is non-adjudicable, never a divergence."""
    problems = []
    for layer in LAYERS:
        seen = observed[layer]["outcome"]
        if seen not in LAYER_OUTCOMES[layer]:
            problems.append(
                "layer %s returned an outcome outside the registered vocabulary: %s"
                % (layer, seen)
            )
    return problems


# --------------------------------------------------------------------------
# publication
# --------------------------------------------------------------------------

def detection_matrix(rows):
    lines = [
        "# Detection matrix — Study 014",
        "",
        "Per-cell, per-layer outcome adjudicated against `harness/MATRIX.json`",
        "(locked-replication stratum). Every registered cell appears; nothing is",
        "excluded. Only `endpoint` rows count toward R1; `control-gate` rows are",
        "validity gates, `demonstration` and `descriptive` rows count toward nothing.",
        "",
        "| Cell | Role | Attacker | OWP | BINDING | REPLAY | Combined | Registered | Divergence |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        if row["status"] == NOT_ADJUDICATED:
            lines.append(
                "| `%s` | %s | %s | — | — | — | %s | %s | pipeline-invalid |"
                % (
                    row["cell"],
                    row["role"],
                    row["attackerCapability"],
                    NOT_ADJUDICATED,
                    "expected " + json.dumps(row["expected"]),
                )
            )
            continue
        seen = row["observedOutcomes"]
        lines.append(
            "| `%s` | %s | %s | `%s` | `%s` | `%s` | `%s` | %s | %s |"
            % (
                row["cell"],
                row["role"],
                row["attackerCapability"],
                seen["owp"],
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
        detection_matrix(rows), encoding="utf-8"
    )


def terminal_invalid(attempt_root, label, problems, provenance):
    """Persist a terminal pipeline-invalid record. Every failure path lands here."""
    results = {
        "study": "014-openworkproof-binding",
        "stratum": "locked-replication",
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
            "preregistration digest, so the preregistration is still DRAFT and "
            "the reviewer-authored holdout stratum may not be executed"
        )

    # The attempt marker lands before anything else runs, so an attempt that
    # dies mid-flight is still a recorded attempt rather than a silent absence.
    attempt_root.mkdir(parents=True)
    (attempt_root / "ATTEMPT.json").write_text(
        json.dumps(
            {
                "study": "014-openworkproof-binding",
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
        registry = json.loads(
            (STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8")
        )
    except Exception as error:
        return terminal_invalid(
            attempt_root, label, ["matrix is unreadable: %s" % error], provenance
        )

    gate_problems = []
    gate_problems.extend(pin_problems(pins, jpack_bin))
    gate_problems.extend(make_manifest.manifest_problems())
    gate_problems.extend(matrix_problems(registry))
    if gate_problems:
        return terminal_invalid(attempt_root, label, gate_problems, provenance)

    validity = []
    rows = []
    work_root = Path(tempfile.mkdtemp(prefix="study014-score-"))
    try:
        for cell in registry["cells"]:
            row = adjudicate_cell(cell, jpack_bin, work_root, validity)
            rows.append(row)
    except Exception as error:
        return terminal_invalid(
            attempt_root,
            label,
            [item["problem"] for item in validity]
            + ["harness crashed while adjudicating: %s: %s" % (type(error).__name__, error)],
            provenance,
        )
    finally:
        shutil.rmtree(work_root, ignore_errors=True)

    invalid = [row for row in rows if row["status"] == NOT_ADJUDICATED]
    diverged = [row for row in rows if row["divergences"]]
    gates = [row for row in rows if row["role"] == "control-gate"]
    endpoints = [row for row in rows if row["role"] == "endpoint"]
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
        "study": "014-openworkproof-binding",
        "stratum": "locked-replication",
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
            "cells": len(rows),
            "adjudicated": len(rows) - len(invalid),
            "endpointCells": len(endpoints),
            "endpointDivergentCells": [row["cell"] for row in diverged_endpoints],
            "divergentCells": [row["cell"] for row in diverged],
            "rows": rows,
        },
    }
    write_outputs(attempt_root, results, rows)
    return results


def adjudicate_cell(cell, jpack_bin, work_root, validity):
    """One cell. Never raises: a crash here is a NOT-ADJUDICATED row."""
    shared = {
        "cell": cell["id"],
        "category": cell["category"],
        "role": cell["role"],
        "attackerCapability": cell["attackerCapability"],
        "expected": expected_tuple(cell["expected"]),
        "registeredUndetected": bool(cell.get("registeredUndetected")),
    }
    try:
        directory = cell_directory(cell["id"])
        problems = pipeline_problems(directory, cell)
        if not problems:
            observed = verify.verify_cell(directory, jpack_bin, work_root)
            problems = vocabulary_problems(cell["id"], observed)
    except Exception as error:
        problems = ["harness raised while verifying: %s: %s" % (type(error).__name__, error)]
        observed = None
    if problems:
        validity.extend({"scope": cell["id"], "problem": problem} for problem in problems)
        return dict(
            shared,
            status=NOT_ADJUDICATED,
            observed=None,
            observedOutcomes=None,
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
                % (row["cell"], row["role"], item["layer"], item["expected"], item["observed"])
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
