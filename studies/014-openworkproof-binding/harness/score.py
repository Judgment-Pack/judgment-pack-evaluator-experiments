"""The scorer — the only thing that publishes.

Adjudicates every registered cell in `harness/MATRIX.json` by deterministic
recomputation from frozen fixture bytes, and writes one attempt record:

    RESULTS.json         per-cell layer verdicts, the registered expectation,
                         divergence flags, the pins stamp, and a validity section
                         kept strictly separate from the detection section
    DETECTION-MATRIX.md  the per-layer table, published in full whichever way it
                         lands (PREREGISTRATION section 10)

Decision rule (PREREGISTRATION section 5, ordered and exhaustive):

    1. any cell pipeline-invalid  -> "R1 inconclusive - pipeline-invalid"
    2. else zero divergences      -> "R1 holds"
    3. else                       -> "R1 falsified"

While `PINS.json` carries a null preregistration digest the attempt is labelled
PILOT and can never be labelled REGISTERED (PREREGISTRATION section 6).

Run: JPACK_BIN=... python harness/score.py --attempt-root <new directory>
"""

import argparse
import json
import os
import platform
import shutil
import sys
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDY / "adapter"))

import verify  # noqa: E402

VERDICT_INVALID = "R1 inconclusive — pipeline-invalid"
VERDICT_HOLDS = "R1 holds"
VERDICT_FALSIFIED = "R1 falsified"
NOT_ADJUDICATED = "NOT-ADJUDICATED"

OWP_VERDICTS = ("pass", "fail", "unavailable")
BINDING_VERDICTS = ("pass",) + tuple("fail:" + code for code in verify.BINDING_CODES)
REPLAY_VERDICTS = ("pass", "unavailable") + tuple(
    "fail:" + code for code in verify.REPLAY_CODES
)
LAYER_VERDICTS = {
    "owp": OWP_VERDICTS,
    "binding": BINDING_VERDICTS,
    "replay": REPLAY_VERDICTS,
}


def normalize(verdict):
    """`fail:replay-refused:<class>` classifies as `fail:replay-refused`."""
    if isinstance(verdict, str) and verdict.startswith("fail:replay-refused:"):
        return "fail:replay-refused"
    return verdict


def classify(layer, verdict):
    """True when the layer's verdict is inside the registered vocabulary."""
    return normalize(verdict) in LAYER_VERDICTS[layer]


def cell_directory(cell_id):
    if cell_id == "pos-baseline":
        return STUDY / "fixtures" / "baseline"
    return STUDY / "fixtures" / "mutations" / cell_id


def registered_absences(expectation):
    """Artifacts whose absence the matrix registers for this cell."""
    absent = set()
    for layer, verdict in expectation.items():
        if layer != "binding" or not isinstance(verdict, str):
            continue
        for name, artifact in (
            ("pack-artifact-missing", "pack.json"),
            ("facts-artifact-missing", "facts.json"),
            ("evidence-artifact-missing", "evidence.json"),
        ):
            if verdict == "fail:" + name:
                absent.add(artifact)
    return absent


def pipeline_problems(directory, expectation):
    """Validity channel (PREREGISTRATION section 6), never a detection."""
    directory = Path(directory)
    if not directory.is_dir():
        return ["cell directory is absent"]
    problems = list(verify.manifest_problems(directory))
    allowed_absent = registered_absences(expectation or {})
    for name in verify.CELL_FILES:
        if not (directory / name).is_file() and name not in allowed_absent:
            problems.append("unregistered missing artifact: " + name)
    return problems


def expected_tuple(expectation):
    combined = (
        "pass"
        if all(expectation[layer] == "pass" for layer in ("owp", "binding", "replay"))
        else "fail"
    )
    return dict(expectation, combined=combined)


def adjudicate(observed, expectation):
    """Divergences in either direction, per layer plus the derived combined."""
    expected = expected_tuple(expectation)
    divergences = []
    for layer in ("owp", "binding", "replay"):
        seen = observed[layer]["verdict"]
        if seen != expected[layer]:
            divergences.append(
                {"layer": layer, "expected": expected[layer], "observed": seen}
            )
    if observed["combined"] != expected["combined"]:
        divergences.append(
            {
                "layer": "combined",
                "expected": expected["combined"],
                "observed": observed["combined"],
            }
        )
    return expected, divergences


def detection_matrix(rows):
    lines = [
        "# Detection matrix — Study 014",
        "",
        "Per-cell, per-layer outcome adjudicated against `harness/MATRIX.json`.",
        "Every registered cell appears; nothing is excluded.",
        "",
        "| Cell | Category | OWP | BINDING | REPLAY | Combined | Registered | Divergence |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        if row["status"] == NOT_ADJUDICATED:
            lines.append(
                "| `%s` | %s | — | — | — | %s | %s | pipeline-invalid |"
                % (
                    row["cell"],
                    row["category"],
                    NOT_ADJUDICATED,
                    "expected " + json.dumps(row["expected"]),
                )
            )
            continue
        observed = row["observed"]
        lines.append(
            "| `%s` | %s | `%s` | `%s` | `%s` | `%s` | %s | %s |"
            % (
                row["cell"],
                row["category"],
                observed["owp"]["verdict"],
                observed["binding"]["verdict"],
                observed["replay"]["verdict"],
                observed["combined"],
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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--attempt-root", required=True)
    arguments = parser.parse_args(argv)

    attempt_root = Path(arguments.attempt_root)
    if attempt_root.exists():
        raise SystemExit("attempt root already exists: %s" % attempt_root)

    pins_path = STUDY / "harness" / "PINS.json"
    pins = json.loads(pins_path.read_text(encoding="utf-8"))
    registry = json.loads(
        (STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8")
    )
    label = (
        "PILOT" if pins["preregistration"]["sha256"] is None else "REGISTERED"
    )

    jpack_bin = os.environ.get("JPACK_BIN")
    validity = []
    if not jpack_bin or not Path(jpack_bin).is_file():
        validity.append({"scope": "attempt", "problem": "JPACK_BIN is not available"})
        jpack_bin = None
    elif verify.sha256_file(jpack_bin) != pins["jpack"]["binarySha256"]:
        validity.append(
            {"scope": "attempt", "problem": "JPACK_BIN does not match the pinned digest"}
        )
        jpack_bin = None

    work_root = Path(tempfile.mkdtemp(prefix="study014-score-"))
    rows = []
    try:
        for cell in registry["cells"]:
            directory = cell_directory(cell["id"])
            problems = pipeline_problems(directory, cell["expected"])
            if validity and validity[0]["scope"] == "attempt":
                problems = problems + [validity[0]["problem"]]
            if problems:
                validity.extend(
                    {"scope": cell["id"], "problem": problem} for problem in problems
                )
                rows.append(
                    {
                        "cell": cell["id"],
                        "category": cell["category"],
                        "status": NOT_ADJUDICATED,
                        "expected": expected_tuple(cell["expected"]),
                        "observed": None,
                        "divergences": [],
                        "problems": problems,
                    }
                )
                continue
            observed = verify.verify_cell(directory, jpack_bin, work_root)
            expected, divergences = adjudicate(observed, cell["expected"])
            for layer in ("owp", "binding", "replay"):
                if not classify(layer, observed[layer]["verdict"]):
                    validity.append(
                        {
                            "scope": cell["id"],
                            "problem": "layer %s returned a verdict outside the "
                            "registered vocabulary: %s"
                            % (layer, observed[layer]["verdict"]),
                        }
                    )
            rows.append(
                {
                    "cell": cell["id"],
                    "category": cell["category"],
                    "status": "adjudicated",
                    "expected": expected,
                    "observed": observed,
                    "divergences": divergences,
                    "problems": [],
                    "registeredUndetected": bool(cell.get("registeredUndetected")),
                }
            )
    finally:
        shutil.rmtree(work_root, ignore_errors=True)

    invalid = [row for row in rows if row["status"] == NOT_ADJUDICATED]
    diverged = [row for row in rows if row["divergences"]]
    if invalid or any(item["scope"] == "attempt" for item in validity):
        verdict = VERDICT_INVALID
    elif not diverged:
        verdict = VERDICT_HOLDS
    else:
        verdict = VERDICT_FALSIFIED

    results = {
        "study": "014-openworkproof-binding",
        "attemptLabel": label,
        "verdict": verdict,
        "matrixVersion": registry["matrixVersion"],
        "provenance": {
            "pinsSha256": verify.sha256_file(pins_path),
            "matrixSha256": verify.sha256_file(STUDY / "harness" / "MATRIX.json"),
            "specSha256": verify.sha256_file(STUDY / "adapter" / "SPEC.md"),
            "preregistrationSha256": verify.sha256_file(
                STUDY / "PREREGISTRATION.md"
            ),
            "jpackSha256": verify.sha256_file(jpack_bin) if jpack_bin else None,
            "harnessPython": platform.python_version(),
        },
        "validity": {
            "pipelineInvalidCells": [row["cell"] for row in invalid],
            "records": validity,
        },
        "detection": {
            "cells": len(rows),
            "adjudicated": len(rows) - len(invalid),
            "divergentCells": [row["cell"] for row in diverged],
            "rows": rows,
        },
    }
    attempt_root.mkdir(parents=True)
    (attempt_root / "RESULTS.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (attempt_root / "DETECTION-MATRIX.md").write_text(
        detection_matrix(rows), encoding="utf-8"
    )
    print("%s (%s): %d cells, %d divergent, %d pipeline-invalid"
          % (verdict, label, len(rows), len(diverged), len(invalid)))
    for row in diverged:
        for item in row["divergences"]:
            print("  divergence %s %s: expected %s, observed %s"
                  % (row["cell"], item["layer"], item["expected"], item["observed"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
