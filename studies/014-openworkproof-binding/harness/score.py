"""The scorer — the only thing that publishes.

Adjudicates every registered cell in `harness/MATRIX.json` by deterministic
recomputation from frozen fixture bytes, and writes one attempt record:

    ATTEMPT.json         written before PINS.json is even parsed and under every
                         flag combination, so an attempt that dies anywhere —
                         including one refused for trying to run the holdout too
                         early — is still a recorded attempt
    RESULTS.json         per-cell layer outcomes, the registered expectation,
                         divergence flags, the pins stamp, and a validity section
                         kept strictly separate from the detection section
    DETECTION-MATRIX.md  the per-layer table, published in full whichever way it
                         lands (PREREGISTRATION section 10)
    CONSTRUCTION.json    post-freeze `--include-holdout` only: the per-cell record
                         of the holdout construction this attempt drove, with a
                         digest of every fixture manifest it produced
    holdout-fixtures/    post-freeze `--include-holdout` only: the holdout cells
                         this attempt constructed and adjudicated, written once
                         inside the attempt that read them

Every output write is atomic (temporary file in the same directory, then
`os.replace`), and every step from the holdout refusals and PINS parsing through
provenance hashing, the freeze gates, holdout construction, adjudication and
publication runs inside one terminal catch — `SystemExit` and `KeyboardInterrupt`
included, recorded and then re-raised — so no failure path can leave an attempt
without a record. The two conditions that cannot record themselves are announced
on stderr instead: a marker write that fails (nothing else is then attempted) and
a fallback publication that fails inside the catch.

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

While any freeze pin in `PINS.json` is null — preregistration, matrix,
matrixHoldout, adapterSpec or studyManifest — the attempt is labelled PILOT and
can never be labelled REGISTERED (PREREGISTRATION section 6), and
`--include-holdout` is refused mechanically: the reviewer-authored holdout
stratum may not be executed before the freeze. After the freeze the flag makes
the attempt itself **construct** the holdout stratum (the builder hooks, driven
in-process, inside this attempt's marker and terminal catch, into this attempt's
own `holdout-fixtures/` subtree, with a per-cell `CONSTRUCTION.json` beside each
fixture and every per-cell manifest digest stamped into the attempt record) and
then adjudicate `harness/MATRIX-HOLDOUT.json` into a **separate** stratum section —
its own gates, its own concordance summary, its own rows — that never touches
the locked stratum's counts or the R1 verdict. A construction that upstream
refuses is a constructibility finding; a construction that crashes is this
attempt's terminal record, not a silent rerun.

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


HOLDOUT_FIXTURE_DIRECTORY = "holdout-fixtures"


def holdout_fixture_root(attempt_root):
    """The attempt's own holdout subtree. Round 4: there is no shared one.

    Holdout bytes used to be built into `fixtures/holdout/`, shared across every
    attempt: a later run could rebuild and re-manifest them coherently while an
    earlier attempt's record — which carried no digest of them — went on reading
    as if it had adjudicated the bytes it actually saw. They are now built inside
    the attempt that adjudicates them, in a directory the scorer has just created
    (it refuses an attempt root that already exists), and their per-cell manifest
    and construction-record digests are stamped into that attempt's results.
    """
    return Path(attempt_root) / HOLDOUT_FIXTURE_DIRECTORY


def holdout_cell_directory(attempt_root, cell_id):
    """Where this attempt's copy of a reviewer-authored holdout cell lives."""
    return holdout_fixture_root(attempt_root) / cell_id


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
    """The freeze pin over the *installed* package's own bytes.

    The computation lives in `adapter/verify.py` because the builder re-verifies
    the same pin after it imports the pinned clone's helpers (round 4's import
    laundering finding), and two implementations of one pin would be worth only
    what the weaker of them checks. Failures become `PipelineInvalid` here, which
    is the attempt-scope shape the gates expect.
    """
    try:
        return verify.installed_package_digest(name)
    except PipelineInvalid:
        raise
    except Exception as error:
        raise PipelineInvalid(str(error))


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
# The freeze pins. Every one of them must be non-null for an attempt to carry
# the REGISTERED label: round 3 found that a null matrix, holdout, SPEC or
# study-manifest digest was still accepted in a registered run, so a frozen
# preregistration alone could authorize adjudication over an unpinned registry.
# A single null makes the attempt a PILOT; the non-null ones are enforced under
# BOTH labels, which is what `pin_problems` does.
FREEZE_PIN_MEMBERS = tuple(member for member, _ in PINNED_DIGEST_MEMBERS)
PACK_PATH = STUDY / "fixtures" / "minimal-expense-approval.pack.json"


def unfilled_freeze_pins(pins):
    """The freeze pins still null, in registry order. Empty means frozen."""
    return [
        member
        for member in FREEZE_PIN_MEMBERS
        if (pins.get(member) or {}).get("sha256") is None
    ]


def attempt_label(pins):
    """`REGISTERED` iff every freeze pin is filled; `PILOT` otherwise."""
    return "PILOT" if unfilled_freeze_pins(pins) else "REGISTERED"


def pin_problems(pins, jpack_bin):
    """Every non-null pin compared against the live artefact. Hard, not advisory.

    Two pins are unconditional rather than fill-at-freeze: the vendored pack
    bytes (the study never fetches the pack, so nothing else would notice a
    substitution) and `openworkproof.installedPackageDigest` (the freeze has to
    be anchored to the package the verification path imports, not to a mutable
    local-file URL in a `pip freeze` line).

    The anchor order is linear (round 3): the study manifest covers the code, the
    protocol documents and the locked stratum's fixture manifests but NOT this
    registry; this registry pins the manifest's digest; the freeze commit and
    each attempt's `pinsSha256` stamp anchor this registry. `make_manifest.py`
    can still rewrite the manifest, but after the freeze it cannot rewrite the
    digest this registry pins it at, and this registry cannot be edited without
    changing the digest the freeze commit and every attempt record carry.
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


def publish_terminal(attempt_root, label, problems, provenance, suppress=False):
    """`terminal_invalid`, with the last failure mode reported rather than lost.

    Round 3's terminal-path gap: if the fallback publication itself failed — the
    atomic write inside the catch — the attempt died silently, which is the exact
    thing the terminal record exists to prevent. There is nowhere left to write
    such a failure, so it is announced on stderr together with the problems it
    would have recorded. `suppress` is for the `SystemExit`/`KeyboardInterrupt`
    path, where the original termination, not the publication failure, is what
    must reach the caller.
    """
    try:
        return terminal_invalid(attempt_root, label, problems, provenance)
    except BaseException as failure:
        print(
            "study014: the terminal pipeline-invalid record could not be published "
            "under %s: %s: %s" % (attempt_root, type(failure).__name__, failure),
            file=sys.stderr,
        )
        print(
            "study014: the problems it would have recorded were: %s"
            % ("; ".join(problems) or "(none)"),
            file=sys.stderr,
        )
        if suppress:
            return None
        raise


# --------------------------------------------------------------------------
# the attempt
# --------------------------------------------------------------------------

def preflight_pins():
    """PINS read for the holdout refusals alone. Unreadable reads as empty.

    Round 3 moved this *behind* the attempt marker: it used to run before the
    attempt directory existed, so a malformed registry under `--include-holdout`
    exited with no marker and no record at all. The refusals are unchanged; what
    changed is that they now happen inside an attempt that is already on disk, so
    a refusal — like every other termination — leaves a terminal record.
    """
    try:
        return json.loads(
            (STUDY / "harness" / "PINS.json").read_text(encoding="utf-8")
        )
    except Exception:
        return None


def marker_text(label, include_holdout):
    """The attempt marker's bytes. `label` is None until PINS.json parses."""
    marker = {"study": "014-openworkproof-binding", "stratum": "locked-replication"}
    if label is not None:
        marker["attemptLabel"] = label
    marker["includeHoldout"] = bool(include_holdout)
    marker["marker"] = "written before any cell ran"
    return json.dumps(marker, indent=2) + "\n"


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


def adjudicate_holdout(attempt_root, registry, jpack_bin, work_root, validity):
    """Adjudicate the holdout stratum into rows of its own. Never merged.

    Reads the attempt's own `holdout-fixtures/` subtree and nothing else (round
    4), so the bytes adjudicated here are the bytes this attempt constructed.
    """
    rows = []
    for cell in registry["cells"]:
        rows.append(
            adjudicate_cell(
                cell,
                jpack_bin,
                work_root,
                validity,
                directory=holdout_cell_directory(attempt_root, cell["id"]),
                scope="holdout",
            )
        )
    return holdout_summary(rows)


# --------------------------------------------------------------------------
# holdout construction, inside the attempt
# --------------------------------------------------------------------------

CONSTRUCTION_RECORD_NAME = "CONSTRUCTION.json"


def read_construction_record(directory):
    """The persisted per-cell construction record, or None if there is none."""
    path = Path(directory) / CONSTRUCTION_RECORD_NAME
    if not path.is_file():
        return None
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except Exception as error:
        return {
            "status": "unreadable",
            "detail": "%s: %s" % (type(error).__name__, error),
        }
    if not isinstance(record, dict):
        return {"status": "unreadable", "detail": "the record is not a JSON object"}
    return record


def construction_problems(cell_id, directory):
    """Adjudicate a holdout cell's *construction* from its persisted record.

    Returns `(problems, finding)`. `problems is None` means the cell was built
    and the ordinary per-cell ceremony should run. Otherwise `problems` is the
    validity text and `finding` is the constructibility finding when — and only
    when — a genuine attempt captured an upstream refusal verbatim.

    Round 3's rule, in one place: a proven upstream refusal is a finding
    (PREREGISTRATION section 1a); a harness failure is a validity problem; and an
    absent fixture with no record at all is a validity problem too, because
    absence on its own does not say whether the construction was attempted,
    aborted, or deleted.
    """
    record = read_construction_record(directory)
    if record is None:
        return (
            [
                "holdout fixture carries no construction record: %s is absent, so "
                "nothing shows whether the registered construction was attempted, "
                "refused, or never run. Unexplained absence is a validity problem "
                "and is NOT a constructibility finding" % CONSTRUCTION_RECORD_NAME
            ],
            None,
        )
    status = record.get("status")
    if status == "built":
        return None, None
    if status == "refused":
        upstream = record.get("upstreamError")
        if not isinstance(upstream, str) or not upstream.strip():
            return (
                [
                    "holdout construction record claims an upstream refusal but "
                    "carries no upstream error: an uncaptured refusal is a validity "
                    "problem, not a constructibility finding"
                ],
                None,
            )
        finding = {
            "cell": cell_id,
            "finding": "constructibility-refusal",
            "detail": record.get("detail"),
            "upstreamError": upstream,
            "upstreamErrorType": record.get("upstreamErrorType"),
            "builderVersionDigest": record.get("builderVersionDigest"),
        }
        return (
            [
                "the registered construction was attempted and upstream refused to "
                "publish it — a constructibility finding under PREREGISTRATION "
                "section 1a, NOT-ADJUDICATED and never a detection or a miss. "
                "Upstream said: %s" % upstream
            ],
            finding,
        )
    if status == "harness-error":
        return (
            [
                "holdout construction failed inside this harness: %s. That is a "
                "validity problem, never a constructibility finding"
                % record.get("harnessError")
            ],
            None,
        )
    return (
        [
            "holdout construction record is not usable (status %r): %s"
            % (status, record.get("detail"))
        ],
        None,
    )


def holdout_fixture_digests(attempt_root, cell_ids):
    """Per-cell digests over what this attempt actually constructed.

    Round 4's blocker: an attempt published holdout outcomes without binding the
    bytes they came from, so the same record could be paired with any later,
    coherently re-manifested tree. Two digests per cell — over the per-cell
    `MANIFEST.sha256` (which itself covers every artifact byte) and over the
    per-cell `CONSTRUCTION.json` — go into the attempt record, so the attempt
    states which bytes it adjudicated. `None` where the file is absent, which is
    itself a statement: a refused construction has a record and no manifest.

    These are the *pre*-adjudication stamps; `post_adjudication_integrity` hashes
    the same artifacts again at the end and publishes the comparison (round 5).
    """
    digests = {}
    for cell_id in cell_ids:
        directory = holdout_cell_directory(attempt_root, cell_id)
        manifest = directory / verify.MANIFEST_NAME
        record = directory / CONSTRUCTION_RECORD_NAME
        digests[cell_id] = {
            "manifestSha256": (
                verify.sha256_file(manifest) if manifest.is_file() else None
            ),
            "constructionSha256": (
                verify.sha256_file(record) if record.is_file() else None
            ),
        }
    return digests


def manifest_stamps(directory):
    """`{name: sha256}` from a per-cell `MANIFEST.sha256`; empty when absent."""
    path = Path(directory) / verify.MANIFEST_NAME
    stamps = {}
    if not path.is_file():
        return stamps
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, _, name = line.partition("  ")
        stamps[name] = digest
    return stamps


def _integrity_entry(cell_id, attempt_root, directory, name, stamped):
    path = Path(directory) / name
    final = verify.sha256_file(path) if path.is_file() else None
    return {
        "cell": cell_id,
        "path": (
            Path(directory).relative_to(Path(attempt_root)).as_posix() + "/" + name
        ),
        "stampedSha256": stamped,
        "finalSha256": final,
        "match": stamped == final,
    }


def post_adjudication_integrity(attempt_root, fixture_digests):
    """Re-hash the holdout subtree after adjudication and compare to its stamps.

    Round 5's finding on the round-4 closure: the attempt-local subtree is bound
    to the attempt by digests taken *before* adjudication, and ordinary writable
    files can be atomically replaced — or whole cell directories removed — while
    the attempt is still running. Sampling a hash and never looking again means
    the published record says which bytes were adjudicated only if nothing moved.

    So every stamped artifact is hashed once more at the end and compared:

      * the per-cell `MANIFEST.sha256` and `CONSTRUCTION.json`, against the
        digests stamped into the attempt record by `holdout_fixture_digests`;
      * every file the per-cell manifest lists, against its manifest line (which
        is itself under the manifest digest above, so the chain is closed);
      * any file present in a cell directory that no stamp covers, which is
        recorded as an unstamped arrival rather than passed over.

    A `None` stamp compared with an absent file matches: a refused construction
    has a record and no manifest, and it must keep having none.
    """
    files = []
    for cell_id in sorted(fixture_digests or {}):
        stamps = fixture_digests[cell_id] or {}
        directory = holdout_cell_directory(attempt_root, cell_id)
        stamped_names = {verify.MANIFEST_NAME, CONSTRUCTION_RECORD_NAME}
        for member, name in (
            ("manifestSha256", verify.MANIFEST_NAME),
            ("constructionSha256", CONSTRUCTION_RECORD_NAME),
        ):
            files.append(
                _integrity_entry(
                    cell_id, attempt_root, directory, name, stamps.get(member)
                )
            )
        for name, digest in sorted(manifest_stamps(directory).items()):
            stamped_names.add(name)
            files.append(
                _integrity_entry(cell_id, attempt_root, directory, name, digest)
            )
        present = (
            sorted(item.name for item in Path(directory).iterdir() if item.is_file())
            if Path(directory).is_dir()
            else []
        )
        for name in present:
            if name in stamped_names:
                continue
            files.append(_integrity_entry(cell_id, attempt_root, directory, name, None))
    mismatched = [entry for entry in files if not entry["match"]]
    problems = [
        "holdout fixture drifted after adjudication: %s was stamped %s and now "
        "hashes %s" % (entry["path"], entry["stampedSha256"], entry["finalSha256"])
        for entry in mismatched
    ]
    return {
        "checked": len(files),
        "intact": not mismatched,
        "files": files,
        "mismatches": [entry["path"] for entry in mismatched],
        "problems": problems,
    }


def attach_post_adjudication_integrity(attempt_root, construction, holdout, validity):
    """Publish the re-hash comparison and make any drift a validity problem."""
    integrity = post_adjudication_integrity(
        attempt_root, (construction or {}).get("fixtureDigests") or {}
    )
    for problem in integrity["problems"]:
        validity.append(
            {
                "scope": HOLDOUT_FIXTURE_DIRECTORY,
                "stratum": "holdout",
                "problem": problem,
            }
        )
    holdout = dict(holdout, postAdjudicationIntegrity=integrity)
    if not integrity["intact"]:
        # The locked-stratum verdict is never recomputed from holdout state; what
        # drift voids is the holdout stratum's own conclusion.
        holdout["summary"] = "holdout inconclusive — fixtures drifted after adjudication"
    return holdout


def construct_holdout(attempt_root, registry, pins, jpack_bin):
    """Build the holdout stratum as part of this attempt, and record every cell.

    Round 3's finding: construction ran in a separate command, so a crash left no
    attempt-scope trace and could be quietly rerun until it worked. Construction
    now happens here — inside the attempt marker and inside the terminal catch —
    and the per-cell records land both beside the fixtures and in the attempt.
    A crash anywhere in it propagates and becomes this attempt's terminal
    pipeline-invalid record.

    Round 4's finding: the fixtures are written into `<attempt>/holdout-fixtures/`
    rather than a shared `fixtures/holdout/`, and every per-cell manifest digest
    and construction-record digest is stamped into the attempt's own record. The
    attempt root is created by this run and refused if it already exists, so the
    subtree is written once and cannot be re-manifested under this attempt's
    published outcomes afterwards.

    The pre-freeze guard is repeated here rather than assumed from the caller:
    the reviewer-authored stratum may not be built while any freeze pin is null.
    """
    unfilled = unfilled_freeze_pins(pins)
    if unfilled:
        raise PipelineInvalid(
            "holdout construction is refused while these freeze pins are null: %s"
            % ", ".join(unfilled)
        )
    import build_fixtures  # noqa: E402 - build path, imported only post-freeze

    # Round 5: the builder's holdout routes are gated on this object, and this is
    # the only place in the study that constructs one. It is minted *after* the
    # freeze-pin check above, and it carries the live digests of the three
    # documents that decide whether a holdout construction is lawful, so a route
    # called from anywhere else — a script, a test, a future helper — refuses
    # instead of quietly building the reviewer's stratum.
    attempt = build_fixtures.HoldoutAttemptContext(
        attempt_root=Path(attempt_root),
        pins_sha256=verify.sha256_file(STUDY / "harness" / "PINS.json"),
        prereg_sha256=verify.sha256_file(STUDY / "PREREGISTRATION.md"),
        holdout_sha256=verify.sha256_file(STUDY / "harness" / "MATRIX-HOLDOUT.json"),
    )
    cell_ids = [cell["id"] for cell in registry["cells"]]
    records = build_fixtures.construct_holdout(
        attempt,
        jpack_bin,
        holdout_fixture_root(attempt_root),
        os.environ.get("OWP_SOURCE"),
        cell_ids,
    )
    published = {
        "study": "014-openworkproof-binding",
        "stratum": "reviewer-holdout",
        "fixtureRoot": HOLDOUT_FIXTURE_DIRECTORY,
        "builderVersionDigest": build_fixtures.builder_version_digest(),
        "records": [records[cell_id] for cell_id in cell_ids],
        "fixtureDigests": holdout_fixture_digests(attempt_root, cell_ids),
    }
    atomic_write_text(
        Path(attempt_root) / CONSTRUCTION_RECORD_NAME,
        json.dumps(published, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
    )
    return published


def run(attempt_root, include_holdout=False):
    attempt_root = Path(attempt_root)
    if attempt_root.exists():
        raise SystemExit("attempt root already exists: %s" % attempt_root)

    # The marker lands FIRST — before `PINS.json` is read, under every flag
    # combination, including `--include-holdout`. Round 3 found that a malformed
    # registry under that flag exited before anything was written at all, which
    # is precisely the silent-absence hole the marker exists to close. The
    # holdout refusals still fire; they now fire inside an attempt that is
    # already on disk, so a refusal leaves a terminal record like every other
    # termination.
    #
    # A marker-write failure is the one condition with nowhere to record itself.
    # It is reported on stderr and NOTHING else is attempted.
    try:
        attempt_root.mkdir(parents=True)
        atomic_write_text(
            attempt_root / "ATTEMPT.json", marker_text(None, include_holdout)
        )
    except BaseException as error:
        print(
            "study014: the attempt marker could not be written under %s: %s: %s"
            % (attempt_root, type(error).__name__, error),
            file=sys.stderr,
        )
        print(
            "study014: nothing further was attempted — an attempt that cannot be "
            "marked is not run",
            file=sys.stderr,
        )
        raise SystemExit(2)

    label = "PILOT"
    provenance = {}
    try:
        preflight = preflight_pins() or {}
        if include_holdout:
            if (preflight.get("preregistration") or {}).get("sha256") is None:
                raise SystemExit(
                    "--include-holdout is refused: harness/PINS.json carries a null "
                    "preregistration digest, so the preregistration is still DRAFT "
                    "and the reviewer-authored holdout stratum may not be executed"
                )
            if (preflight.get("matrixHoldout") or {}).get("sha256") is None:
                raise SystemExit(
                    "--include-holdout is refused: harness/PINS.json carries a null "
                    "matrixHoldout digest, so the holdout stratum the scorer would "
                    "adjudicate is not the one the freeze pinned"
                )

        pins_path = STUDY / "harness" / "PINS.json"
        pins = json.loads(pins_path.read_text(encoding="utf-8"))
        # REGISTERED requires EVERY freeze pin filled, not the preregistration
        # digest alone (round 3): a null matrix, holdout, SPEC or study-manifest
        # digest leaves the registry the attempt adjudicates unpinned.
        label = attempt_label(pins)
        # The label is only knowable once PINS parses; the marker is rewritten
        # atomically rather than being withheld until then.
        atomic_write_text(
            attempt_root / "ATTEMPT.json", marker_text(label, include_holdout)
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
            return publish_terminal(
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
            return publish_terminal(attempt_root, label, gate_problems, provenance)

        # Construction runs INSIDE the attempt (round 3): after the freeze gates,
        # before adjudication, under the marker and the terminal catch. It writes
        # into this attempt's own `holdout-fixtures/` subtree (round 4), so the
        # frozen study manifest — which covers `fixtures/` and never an attempt
        # directory — is untouched by it.
        construction = None
        if holdout_registry is not None:
            construction = construct_holdout(
                attempt_root, holdout_registry, pins, jpack_bin
            )

        validity = []
        rows = []
        holdout = None
        work_root = Path(tempfile.mkdtemp(prefix="study014-score-"))
        try:
            for cell in registry["cells"]:
                rows.append(adjudicate_cell(cell, jpack_bin, work_root, validity))
            if holdout_registry is not None:
                holdout = adjudicate_holdout(
                    attempt_root, holdout_registry, jpack_bin, work_root, validity
                )
                if construction is not None:
                    # Round 5: the stamps were taken before adjudication, so the
                    # subtree is hashed again now and the comparison published.
                    holdout = attach_post_adjudication_integrity(
                        attempt_root, construction, holdout, validity
                    )
        except Exception as error:
            return publish_terminal(
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
            # from the locked rows alone and is not recomputed here. The
            # construction records and the digests of the bytes they produced
            # travel with it (round 4), so the stratum's outcomes and the
            # artifacts they were read from are published as one object.
            if construction is not None:
                holdout = dict(
                    holdout,
                    construction=construction["records"],
                    fixtureRoot=construction["fixtureRoot"],
                    fixtureDigests=construction["fixtureDigests"],
                )
            results["holdout"] = holdout
        write_outputs(attempt_root, results, rows, holdout)
        return results
    except (SystemExit, KeyboardInterrupt) as error:
        # A refusal, a `--help`-style exit, a Ctrl-C: the attempt still ends with
        # a record and the original termination still reaches the caller. Round 3
        # found both of these escaping the catch entirely.
        publish_terminal(
            attempt_root,
            label,
            [
                "the attempt terminated before it could publish: %s: %s"
                % (type(error).__name__, error)
            ],
            provenance,
            suppress=True,
        )
        raise
    except BaseException as error:
        return publish_terminal(
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
    live under `<attempt>/holdout-fixtures/<id>/` and their validity records are
    tagged so a holdout problem can never be read as a locked-stratum problem.

    A holdout cell is adjudicated from its persisted `CONSTRUCTION.json`, not
    from whether a directory happens to exist (round 3). A captured upstream
    refusal is a **constructibility finding** (PREREGISTRATION §1a), reported
    NOT-ADJUDICATED with the upstream error verbatim, and is never a detection or
    a miss. A harness failure, or an absence with no construction record at all,
    is a plain validity problem and is never a finding.
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
    observed = None
    finding = None
    try:
        directory = cell_directory(cell["id"]) if directory is None else Path(directory)
        if scope == "holdout":
            problems, finding = construction_problems(cell["id"], directory)
            if problems is None:
                problems = pipeline_problems(directory, cell)
                if not problems:
                    observed = verify.verify_cell(directory, jpack_bin, work_root)
                    problems = vocabulary_problems(cell["id"], observed)
        else:
            problems = pipeline_problems(directory, cell)
            if not problems:
                observed = verify.verify_cell(directory, jpack_bin, work_root)
                problems = vocabulary_problems(cell["id"], observed)
    except Exception as error:
        problems = ["harness raised while verifying: %s: %s" % (type(error).__name__, error)]
        observed = None
        finding = None
    if finding is not None:
        shared["constructibility"] = finding
    if problems:
        record = {"scope": cell["id"], "stratum": scope or "locked-replication"}
        for problem in problems:
            entry = dict(record, problem=problem)
            if finding is not None:
                entry["finding"] = finding["finding"]
            validity.append(entry)
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
