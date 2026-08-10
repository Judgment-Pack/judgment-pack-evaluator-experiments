"""The scorer — the only thing that publishes.

Adjudicates every registered cell in `harness/MATRIX.json` by deterministic
recomputation from frozen fixture bytes, and writes one attempt record:

    ATTEMPT.json         written before PINS.json is even parsed, so an attempt
                         that dies anywhere is still a recorded attempt
    RESULTS.json         per-cell layer outcomes, the registered expectation,
                         divergence flags, the pins stamp, and a validity section
                         kept strictly separate from the detection section
    DETECTION-MATRIX.md  the per-layer table, published in full whichever way it
                         lands (PREREGISTRATION section 10)

Every output write is atomic (temporary file in the same directory, then
`os.replace`), and every step from PINS parsing through provenance hashing, the
freeze gates, adjudication and publication runs inside one terminal catch, so no
failure path can leave an attempt without a record.

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
preregistration, matrix, holdout-matrix, study-manifest and SPEC digests when
they are filled, the `jpack` binary digest always, the vendored pack bytes
always, a digest over the *installed* `openworkproof` package's own files
always, the interpreter version exactly, and the installed dependency set
through `pip freeze` — verifies `harness/STUDY-MANIFEST.sha256` as an exact set,
and asserts the frozen cell-id set and per-cell schema of the loaded matrix. Any
mismatch is terminal: the attempt is pipeline-invalid and no detection is
adjudicated. Nothing in the published outputs is a timestamp or an absolute
path, so two runs of the same frozen tree are byte-identical.

While `PINS.json` carries a null preregistration digest the attempt is labelled
PILOT and can never be labelled REGISTERED (PREREGISTRATION section 6), and
`--include-holdout` is refused mechanically: the reviewer-authored holdout
stratum may not be executed before the freeze. After the freeze the flag
adjudicates `harness/MATRIX-HOLDOUT.json` into a **separate** stratum section —
its own gates, its own concordance summary, its own rows — that never touches
the locked stratum's counts or the R1 verdict.

Run: JPACK_BIN=... python harness/score.py --attempt-root <new directory>
"""

import argparse
import hashlib
import importlib.util
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
# The holdout stratum is authored by the cross-vendor reviewer, so every cell
# additionally carries its attribution. Same validator otherwise.
HOLDOUT_CELL_FIELDS = CELL_FIELDS + ("author",)
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


def holdout_cell_directory(cell_id):
    """Where a reviewer-authored holdout cell's fixture would live if built."""
    return STUDY / "fixtures" / "holdout" / cell_id


# --------------------------------------------------------------------------
# atomic publication
# --------------------------------------------------------------------------

def atomic_write_bytes(path, payload):
    """Write `payload` to `path` through a same-directory temp file + rename.

    A finalization crash must not be able to leave a half-written RESULTS.json
    that reads as an attempt outcome.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(
        prefix="." + path.name + ".", dir=str(path.parent)
    )
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        # `mkstemp` is 0600 by design; published attempt records are ordinary
        # readable artefacts, so the mode is restored before the rename.
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def atomic_write_text(path, text):
    atomic_write_bytes(path, text.encode("utf-8"))


# --------------------------------------------------------------------------
# freeze integrity (validity channel, before any cell runs)
# --------------------------------------------------------------------------

def installed_package_digest(name="openworkproof"):
    """A deterministic digest over the *installed* package's own source files.

    Round 2's blocker: every OWP pin was either a mutable local-file URL (the
    `pip freeze` line) or an unverified declaration (the commit string), so the
    package the verification path actually imports was never checked. This walks
    the installed package directory resolved through `importlib`, sorts by
    study-relative path, and hashes `path \\0 bytes \\0` for every file that is
    not a `__pycache__` artefact — so a byte edit anywhere inside the installed
    package, including a schema JSON, changes the value.
    """
    spec = importlib.util.find_spec(name)
    if spec is None or not spec.origin:
        raise PipelineInvalid("the %s package is not importable" % name)
    root = Path(spec.origin).resolve().parent
    if not root.is_dir():
        raise PipelineInvalid("the %s package directory is not readable" % name)
    relatives = sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    digest = hashlib.sha256()
    for relative in relatives:
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update((root / relative).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def pip_freeze_sha256():
    """SHA-256 of `pip freeze` in the interpreter that is running the scorer."""
    completed = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"], capture_output=True, timeout=300
    )
    if completed.returncode != 0:
        raise PipelineInvalid("pip freeze failed in the running interpreter")
    return hashlib.sha256(completed.stdout).hexdigest()


PINNED_DIGEST_MEMBERS = (
    ("preregistration", "PREREGISTRATION.md"),
    ("matrix", "harness/MATRIX.json"),
    ("matrixHoldout", "harness/MATRIX-HOLDOUT.json"),
    ("studyManifest", "harness/STUDY-MANIFEST.sha256"),
    ("adapterSpec", "adapter/SPEC.md"),
)
PACK_PATH = STUDY / "fixtures" / "minimal-expense-approval.pack.json"


def pin_problems(pins, jpack_bin):
    """Every non-null pin compared against the live artefact. Hard, not advisory.

    Two pins are unconditional rather than fill-at-freeze: the vendored pack
    bytes (the study never fetches the pack, so nothing else would notice a
    substitution) and `openworkproof.installedPackageDigest` (the freeze has to
    be anchored to the package the verification path imports, not to a mutable
    local-file URL in a `pip freeze` line). `studyManifest.sha256` is the anchor
    outside the regenerable set: `make_manifest.py` can rewrite the manifest, but
    after the freeze it cannot rewrite the digest the registry pins it at.
    """
    problems = []

    for member, relative in PINNED_DIGEST_MEMBERS:
        expected = (pins.get(member) or {}).get("sha256")
        if expected is None:
            continue
        path = STUDY / relative
        if not path.is_file():
            problems.append("pinned artefact is absent: " + relative)
        elif verify.sha256_file(path) != expected:
            problems.append("pinned digest does not match: " + relative)

    expected_pack = (pins.get("pack") or {}).get("sha256")
    if expected_pack is None:
        problems.append("PINS.json carries no pack digest")
    elif not PACK_PATH.is_file():
        problems.append("the vendored pack artefact is absent")
    elif verify.sha256_file(PACK_PATH) != expected_pack:
        problems.append("the vendored pack bytes do not match the pinned digest")

    expected_package = (pins.get("openworkproof") or {}).get("installedPackageDigest")
    if not expected_package:
        problems.append("PINS.json carries no installed openworkproof package digest")
    else:
        try:
            actual_package = installed_package_digest()
        except Exception as error:
            problems.append("the installed openworkproof package is unreadable: %s" % error)
        else:
            if actual_package != expected_package:
                problems.append(
                    "the installed openworkproof package does not match its pinned digest"
                )

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


def cell_schema_problems(cells, required_fields, label):
    """The per-cell schema of a registry stratum, asserted not assumed."""
    problems = []
    ids = [cell.get("id") for cell in cells]
    if len(ids) != len(set(ids)):
        problems.append("%s cell ids are not unique" % label)
    for cell in cells:
        cell_id = cell.get("id", "<unnamed>")
        missing_fields = [field for field in required_fields if field not in cell]
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


def matrix_problems(registry):
    """The frozen cell-id set and the per-cell schema, asserted not assumed."""
    cells = registry.get("cells")
    if not isinstance(cells, list):
        return ["matrix carries no cell list"]
    problems = []
    ids = [cell.get("id") for cell in cells]
    if tuple(ids) != REGISTERED_CELL_IDS:
        missing = [item for item in REGISTERED_CELL_IDS if item not in ids]
        extra = [item for item in ids if item not in REGISTERED_CELL_IDS]
        problems.append(
            "matrix cell set is not the frozen set: missing=%s unregistered=%s "
            "ordered=%s" % (missing, extra, list(ids) == list(REGISTERED_CELL_IDS))
        )
    problems.extend(cell_schema_problems(cells, CELL_FIELDS, "matrix"))
    return problems


def holdout_problems(registry, locked_ids=REGISTERED_CELL_IDS):
    """The holdout stratum's own schema gate: same validator, plus attribution.

    Two extra properties the locked stratum does not need. Every cell carries an
    `author` (the stratum exists to be attributable to the cross-vendor reviewer,
    and a cell without attribution is not a holdout cell), and no holdout id may
    collide with a locked id — an overlap would let a holdout row be read as a
    replication of a locked one, or vice versa.
    """
    cells = registry.get("cells")
    if not isinstance(cells, list):
        return ["holdout matrix carries no cell list"]
    problems = []
    if registry.get("stratum") != "reviewer-holdout":
        problems.append("holdout matrix is not labelled the reviewer-holdout stratum")
    if not cells:
        problems.append(
            "holdout matrix carries no cells: an empty holdout is not a passing holdout"
        )
    problems.extend(cell_schema_problems(cells, HOLDOUT_CELL_FIELDS, "holdout"))
    for cell in cells:
        author = cell.get("author")
        if not isinstance(author, str) or not author.strip():
            problems.append(
                "%s: holdout cells must carry their author" % cell.get("id", "<unnamed>")
            )
    overlap = sorted(
        {cell.get("id") for cell in cells} & set(locked_ids)
    )
    if overlap:
        problems.append("holdout cell ids collide with the locked stratum: %s" % overlap)
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
    """An out-of-vocabulary observation is non-adjudicable, never a divergence.

    Two independent gates, both on the validity channel. The registered
    `{verdict, code}` pair is checked *before* the outcome string, so an unknown
    verdict carrying a known code cannot be normalized into a registered
    `fail:<code>` and a bare `unavailable` cannot stand in for the registered
    (`unavailable`, `replay-unavailable`) pair.
    """
    problems = []
    for layer in LAYERS:
        record = observed[layer]
        problem = verify.pair_problem(layer, record)
        if problem is not None:
            problems.append(problem)
        seen = record["outcome"]
        if seen not in LAYER_OUTCOMES[layer]:
            problems.append(
                "layer %s returned an outcome outside the registered vocabulary: %s"
                % (layer, seen)
            )
    return problems


# --------------------------------------------------------------------------
# publication
# --------------------------------------------------------------------------

def matrix_table(rows):
    lines = [
        "| Cell | Role | Attacker | OWP | BINDING | REPLAY | Combined | Registered | Divergence |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        if row["status"] == NOT_ADJUDICATED:
            lines.append(
                "| `%s` | %s | %s | — | — | — | %s | %s | %s |"
                % (
                    row["cell"],
                    row["role"],
                    row["attackerCapability"],
                    NOT_ADJUDICATED,
                    "expected " + json.dumps(row["expected"]),
                    "; ".join(row["problems"]) or "pipeline-invalid",
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
    return lines


def detection_matrix(rows, holdout=None):
    lines = [
        "# Detection matrix — Study 014",
        "",
        "## Locked-replication stratum",
        "",
        "Per-cell, per-layer outcome adjudicated against `harness/MATRIX.json`",
        "(locked-replication stratum). Every registered cell appears; nothing is",
        "excluded. Only `endpoint` rows count toward R1; `control-gate` rows are",
        "validity gates, `demonstration` and `descriptive` rows count toward nothing.",
        "",
    ]
    lines.extend(matrix_table(rows))
    if holdout is not None:
        lines.extend(
            [
                "",
                "## Reviewer-holdout stratum",
                "",
                "Adjudicated against `harness/MATRIX-HOLDOUT.json`, authored by the",
                "cross-vendor reviewer and never executed before the freeze. This stratum",
                "is scored **separately**: its control-gate rows gate this stratum alone,",
                "its outcomes enter no locked-stratum count, and it never changes the R1",
                "verdict. Stratum summary: **%s** — %d cell(s), %d adjudicated, %d"
                % (
                    holdout["summary"],
                    holdout["cells"],
                    holdout["adjudicated"],
                    len(holdout["endpointDivergentCells"]),
                ),
                "endpoint divergence(s).",
                "",
            ]
        )
        lines.extend(matrix_table(holdout["rows"]))
    return "\n".join(lines) + "\n"


def write_outputs(attempt_root, results, rows, holdout=None):
    attempt_root = Path(attempt_root)
    attempt_root.mkdir(parents=True, exist_ok=True)
    atomic_write_text(
        attempt_root / "RESULTS.json",
        json.dumps(results, indent=2, ensure_ascii=False) + "\n",
    )
    atomic_write_text(
        attempt_root / "DETECTION-MATRIX.md", detection_matrix(rows, holdout)
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

def preflight_pins():
    """PINS read for the argument-surface refusals alone, before anything exists.

    A refusal here must not create an attempt directory, so this read is
    deliberately outside the terminal record: if it fails, `run()` creates the
    attempt and lets the terminal path record the same failure properly.
    """
    try:
        return json.loads(
            (STUDY / "harness" / "PINS.json").read_text(encoding="utf-8")
        )
    except Exception:
        return None


def holdout_summary(rows):
    """The holdout stratum's own concordance verdict, scored on its own gates."""
    invalid = [row for row in rows if row["status"] == NOT_ADJUDICATED]
    gates = [row for row in rows if row["role"] == "control-gate"]
    endpoints = [row for row in rows if row["role"] == "endpoint"]
    failed_gates = [row for row in gates if row["divergences"]]
    diverged_endpoints = [row for row in endpoints if row["divergences"]]
    diverged = [row for row in rows if row["divergences"]]
    if invalid:
        summary = "holdout inconclusive — pipeline-invalid"
    elif failed_gates:
        summary = "holdout inconclusive — control gate failed"
    elif not diverged_endpoints:
        summary = "holdout concordant"
    else:
        summary = "holdout divergent"
    return {
        "stratum": "reviewer-holdout",
        "summary": summary,
        "cells": len(rows),
        "adjudicated": len(rows) - len(invalid),
        "endpointCells": len(endpoints),
        "pipelineInvalidCells": [row["cell"] for row in invalid],
        "controlGateFailures": [row["cell"] for row in failed_gates],
        "endpointDivergentCells": [row["cell"] for row in diverged_endpoints],
        "divergentCells": [row["cell"] for row in diverged],
        "rows": rows,
    }


def adjudicate_holdout(registry, jpack_bin, work_root, validity):
    """Adjudicate the holdout stratum into rows of its own. Never merged."""
    rows = []
    for cell in registry["cells"]:
        rows.append(
            adjudicate_cell(
                cell,
                jpack_bin,
                work_root,
                validity,
                directory=holdout_cell_directory(cell["id"]),
                scope="holdout",
            )
        )
    return holdout_summary(rows)


def run(attempt_root, include_holdout=False):
    attempt_root = Path(attempt_root)
    if attempt_root.exists():
        raise SystemExit("attempt root already exists: %s" % attempt_root)

    # Argument-surface refusals come first, so a refused invocation creates
    # nothing at all. Everything after the marker lands in a terminal record.
    preflight = preflight_pins() or {}
    if include_holdout:
        if (preflight.get("preregistration") or {}).get("sha256") is None:
            raise SystemExit(
                "--include-holdout is refused: harness/PINS.json carries a null "
                "preregistration digest, so the preregistration is still DRAFT and "
                "the reviewer-authored holdout stratum may not be executed"
            )
        if (preflight.get("matrixHoldout") or {}).get("sha256") is None:
            raise SystemExit(
                "--include-holdout is refused: harness/PINS.json carries a null "
                "matrixHoldout digest, so the holdout stratum the scorer would "
                "adjudicate is not the one the freeze pinned"
            )

    # The attempt marker lands before PINS.json is even parsed, so an attempt
    # that dies anywhere is still a recorded attempt rather than a silent absence.
    attempt_root.mkdir(parents=True)
    atomic_write_text(
        attempt_root / "ATTEMPT.json",
        json.dumps(
            {
                "study": "014-openworkproof-binding",
                "stratum": "locked-replication",
                "includeHoldout": bool(include_holdout),
                "marker": "written before any cell ran",
            },
            indent=2,
        )
        + "\n",
    )

    label = "PILOT"
    provenance = {}
    try:
        pins_path = STUDY / "harness" / "PINS.json"
        pins = json.loads(pins_path.read_text(encoding="utf-8"))
        frozen = (pins.get("preregistration") or {}).get("sha256") is not None
        label = "REGISTERED" if frozen else "PILOT"
        # The label is only knowable once PINS parses; the marker is rewritten
        # atomically rather than being withheld until then.
        atomic_write_text(
            attempt_root / "ATTEMPT.json",
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
            "installedPackageDigest": installed_package_digest(),
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

        holdout_registry = None
        gate_problems = []
        gate_problems.extend(pin_problems(pins, jpack_bin))
        gate_problems.extend(make_manifest.manifest_problems())
        gate_problems.extend(matrix_problems(registry))
        if include_holdout:
            try:
                holdout_registry = json.loads(
                    (STUDY / "harness" / "MATRIX-HOLDOUT.json").read_text(
                        encoding="utf-8"
                    )
                )
            except Exception as error:
                gate_problems.append("holdout matrix is unreadable: %s" % error)
            else:
                gate_problems.extend(holdout_problems(holdout_registry))
        if gate_problems:
            return terminal_invalid(attempt_root, label, gate_problems, provenance)

        validity = []
        rows = []
        holdout = None
        work_root = Path(tempfile.mkdtemp(prefix="study014-score-"))
        try:
            for cell in registry["cells"]:
                rows.append(adjudicate_cell(cell, jpack_bin, work_root, validity))
            if holdout_registry is not None:
                holdout = adjudicate_holdout(
                    holdout_registry, jpack_bin, work_root, validity
                )
        except Exception as error:
            return terminal_invalid(
                attempt_root,
                label,
                [item["problem"] for item in validity]
                + [
                    "harness crashed while adjudicating: %s: %s"
                    % (type(error).__name__, error)
                ],
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
        if holdout is not None:
            # A separate section, never merged: the R1 verdict above is computed
            # from the locked rows alone and is not recomputed here.
            results["holdout"] = holdout
        write_outputs(attempt_root, results, rows, holdout)
        return results
    except (SystemExit, KeyboardInterrupt):
        raise
    except BaseException as error:
        return terminal_invalid(
            attempt_root,
            label,
            [
                "the scorer failed outside cell adjudication: %s: %s"
                % (type(error).__name__, error)
            ],
            provenance,
        )


def adjudicate_cell(cell, jpack_bin, work_root, validity, directory=None, scope=None):
    """One cell. Never raises: a crash here is a NOT-ADJUDICATED row.

    `directory` and `scope` are the holdout stratum's only difference: its cells
    live under `fixtures/holdout/<id>/` and their validity records are tagged so
    a holdout problem can never be read as a locked-stratum problem. A holdout
    fixture directory that does not exist is a **constructibility finding**
    (PREREGISTRATION §1a) recorded as NOT-ADJUDICATED, never a silent drop and
    never a detection.
    """
    shared = {
        "cell": cell["id"],
        "category": cell["category"],
        "role": cell["role"],
        "attackerCapability": cell["attackerCapability"],
        "expected": expected_tuple(cell["expected"]),
        "registeredUndetected": bool(cell.get("registeredUndetected")),
    }
    if scope is not None:
        shared["stratum"] = scope
    if cell.get("author"):
        shared["author"] = cell["author"]
    try:
        directory = cell_directory(cell["id"]) if directory is None else Path(directory)
        if scope == "holdout" and not directory.is_dir():
            problems = [
                "holdout fixture is absent: the registered construction was not "
                "built, which is a constructibility finding under PREREGISTRATION "
                "section 1a and NOT-ADJUDICATED — never a silent drop"
            ]
            observed = None
        else:
            problems = pipeline_problems(directory, cell)
            if not problems:
                observed = verify.verify_cell(directory, jpack_bin, work_root)
                problems = vocabulary_problems(cell["id"], observed)
    except Exception as error:
        problems = ["harness raised while verifying: %s: %s" % (type(error).__name__, error)]
        observed = None
    if problems:
        validity.extend(
            {"scope": cell["id"], "stratum": scope or "locked-replication",
             "problem": problem}
            for problem in problems
        )
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
    holdout = results.get("holdout")
    if holdout is not None:
        print(
            "holdout stratum: %s — %d cells, %d adjudicated, %d endpoint-divergent, "
            "%d pipeline-invalid"
            % (
                holdout["summary"],
                holdout["cells"],
                holdout["adjudicated"],
                len(holdout["endpointDivergentCells"]),
                len(holdout["pipelineInvalidCells"]),
            )
        )
        for row in holdout["rows"]:
            for item in row["divergences"]:
                print(
                    "  holdout divergence %s (%s) %s: expected %s, observed %s"
                    % (
                        row["cell"],
                        row["role"],
                        item["layer"],
                        item["expected"],
                        item["observed"],
                    )
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
