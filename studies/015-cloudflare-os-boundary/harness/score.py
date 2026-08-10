"""The scorer — the only thing that publishes.

Adjudicates every registered cell by deterministic recomputation from frozen fixture
bytes, and writes one attempt record:

    ATTEMPT.json         written before anything else runs — including before the pin
                         registry is parsed — so an attempt that dies at any point is
                         still a recorded attempt
    RESULTS.json         per-cell layer outcomes, the registered expectation, divergence
                         flags, suppressed codes, the pins stamp, and a validity section
                         kept strictly separate from the detection section
    DETECTION-MATRIX.md  the per-layer table, published in full whichever way it lands
                         (PREREGISTRATION section 10)

Decision rule for R1 (PREREGISTRATION section 5), over the LOCKED stratum alone:

    1. any locked cell pipeline-invalid -> "R1 inconclusive - pipeline-invalid"
    2. else any control-gate row diverging -> "R1 inconclusive - control gate failed"
    3. else zero endpoint divergences -> "R1 holds"
    4. else -> "R1 falsified"

The reviewer-authored holdout stratum is scored into a separate object with its own
verdict and its own validity records. Nothing in the holdout can change R1 — round 1
found holdout invalidity leaking into the locked verdict, and that is now structurally
impossible: the two strata are adjudicated into disjoint collections.

Freeze integrity is enforced, not declared. Before anything is adjudicated: every
non-null pin is compared against the live artefact (protocol digests when filled, the
`jpack` binary digest, the vendored external inputs' own digests, the interpreter version
and dependency freeze, and the node/esbuild/typescript identities the probe toolchain
actually used); the whole-study manifest is verified as an exact set; the frozen cell-id
set and per-cell schema are asserted for both strata; the registered fixture typecheck
runs as a scorer precondition rather than only as a test; and the upstream runner's
apparatus self-report is checked against the clone pins. Any mismatch is terminal
pipeline-invalidity.

No output embeds a timestamp or an absolute path, so two runs of the same frozen tree are
byte-identical, and every published file is written atomically.

While `PINS.json` carries a null preregistration digest the attempt is labelled PILOT and
can never be labelled REGISTERED, and `--include-holdout` is refused mechanically: the
reviewer-authored holdout stratum may not be executed before the freeze. That refusal
guards the official publication route; it is not a claim that no one could invoke a layer
function directly (PREREGISTRATION section 8).

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
import typecheck  # noqa: E402
import verify  # noqa: E402

VERDICT_INVALID = "R1 inconclusive — pipeline-invalid"
VERDICT_VOID = "R1 inconclusive — control gate failed"
VERDICT_HOLDS = "R1 holds"
VERDICT_FALSIFIED = "R1 falsified"
NOT_ADJUDICATED = "NOT-ADJUDICATED"

HOLDOUT_CONCORDANT = "holdout concordant"
HOLDOUT_DIVERGENT = "holdout divergent"
HOLDOUT_INVALID = "holdout inconclusive — pipeline-invalid"
HOLDOUT_NOT_RUN = "holdout not run"

UPSTREAM_OUTCOMES = ("pass", "not-engaged", "unavailable") + tuple(
    "fail:" + code for code in verify.UPSTREAM_CODES
)
BINDING_OUTCOMES = ("pass",) + tuple("fail:" + code for code in verify.BINDING_CODES)
REPLAY_OUTCOMES = ("pass", "unavailable") + tuple(
    "fail:" + code for code in verify.REPLAY_CODES
)
LAYER_OUTCOMES = {
    "upstream": UPSTREAM_OUTCOMES,
    "binding": BINDING_OUTCOMES,
    "replay": REPLAY_OUTCOMES,
}
LAYERS = ("upstream", "binding", "replay")

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
UPSTREAM_CHECKS = ("classifyTool", "AutoApprovalDrainer")
# What a cell's construction depends on that stock Cloudflare OS does not itself retain
# (SPEC section 0's provenance table). Registered per cell so no detection can quietly
# rest on instrumentation without saying so.
MODELED_DEPENDENCIES = (
    "stagedCallToolName",
    "stagedCallArguments",
    "stageRevision",
    "applyRevision",
    "commitmentCarrier",
    "connectorOutcome",
    "effectAttestation",
    "drainSnapshot",
    "evidenceArtifacts",
)
CELL_FIELDS = (
    "id",
    "category",
    "variant",
    "role",
    "attackerCapability",
    "mutationConstraint",
    "registeredAbsences",
    "upstreamChecksReplayed",
    "modeledDependencies",
    "construction",
    "expected",
    "note",
)
# The holdout was authored against the pre-round-1 schema; these two fields are the
# study's own later additions and the reviewer never wrote them. They are optional there
# and published as unauthored rather than invented on the reviewer's behalf.
HOLDOUT_OPTIONAL_FIELDS = ("mutationConstraint", "modeledDependencies")
ARTIFACT_FILES = {
    "pack": "pack.json",
    "facts": "facts.json",
    "evidence": "evidence.json",
    "evidenceArtifacts": "evidence-artifacts.json",
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
    "neg-binding-control",
    "neg-replay-control",
    "a01-pack-bytes-drift",
    "a02-disposition-forged",
    "a03-evaluator-digest-forged",
    "a04-judgment-identity-forged",
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
    "b07-stage-revision-mismatch",
    "d02-simulated-as-committed",
    "m01-readonly-bypass",
    "m02-ambiguous-commit",
)


class PipelineInvalid(RuntimeError):
    """An attempt-scope condition that forbids adjudication."""


def cell_directory(cell, stratum="locked-replication"):
    cell_id = cell["id"] if isinstance(cell, dict) else cell
    if stratum == "reviewer-holdout":
        return STUDY / "fixtures" / "holdout" / cell_id
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

    # The vendored external inputs are anchored to their own registered digests, not
    # only to the study manifest (round 1: external identity rested on an internal
    # manifest alone).
    for member, relative in (
        ("sha256", "fixtures/data-request-intake-triage.pack.json"),
        ("conformanceCasesSha256", "fixtures/conformance-cases.json"),
    ):
        expected = (pins.get("pack") or {}).get(member)
        if expected is None:
            problems.append("PINS.json carries no digest for " + relative)
            continue
        path = STUDY / relative
        if not path.is_file() or verify.sha256_file(path) != expected:
            problems.append("vendored input does not match its pinned digest: " + relative)

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
    """The upstream runner's self-report against the clone and toolchain pins."""
    problems = []
    cloudflare = pins.get("cloudflareOs") or {}
    node = pins.get("harnessNode") or {}
    toolchain = pins.get("probeToolchain") or {}
    if not isinstance(apparatus, dict):
        return ["the upstream runner produced no apparatus self-report"]
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
    # The two clone-provided tools that actually transform or check study inputs.
    for key, member in (("esbuildVersion", "esbuild"), ("typescriptVersion", "typescript")):
        expected = toolchain.get(member)
        if expected and apparatus.get(key) != expected:
            problems.append(
                "probe %s is %r, pinned %r" % (member, apparatus.get(key), expected)
            )
    expected_files = cloudflare.get("probedFiles") or {}
    actual_files = apparatus.get("probedFiles") or {}
    for relative in sorted(set(expected_files) | set(actual_files)):
        if expected_files.get(relative) != actual_files.get(relative):
            problems.append("probed upstream file does not match its pin: " + relative)
    return problems


def cell_schema_problems(cells, scope, optional_fields=()):
    """Per-cell schema, asserted not assumed — for both strata."""
    problems = []
    for cell in cells:
        cell_id = cell.get("id", "<unnamed>")
        missing_fields = [
            field
            for field in CELL_FIELDS
            if field not in cell and field not in optional_fields
        ]
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
        if "mutationConstraint" in cell and not (
            isinstance(cell["mutationConstraint"], str) and cell["mutationConstraint"]
        ):
            problems.append("%s%s: mutationConstraint is not a statement" % (scope, cell_id))
        absences = cell["registeredAbsences"]
        if not isinstance(absences, list) or any(
            name not in ARTIFACT_FILES for name in absences
        ):
            problems.append(
                "%s%s: registeredAbsences %r is invalid" % (scope, cell_id, absences)
            )
        replayed = cell["upstreamChecksReplayed"]
        if not isinstance(replayed, list) or any(
            name not in UPSTREAM_CHECKS for name in replayed
        ):
            problems.append(
                "%s%s: upstreamChecksReplayed %r is invalid" % (scope, cell_id, replayed)
            )
        if "modeledDependencies" in cell:
            modeled = cell["modeledDependencies"]
            if not isinstance(modeled, list) or any(
                name not in MODELED_DEPENDENCIES for name in modeled
            ):
                problems.append(
                    "%s%s: modeledDependencies %r is invalid" % (scope, cell_id, modeled)
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
    """Holdout gate: non-empty, attributed, id-disjoint, constructed, same cell shape."""
    problems = []
    cells = holdout.get("cells")
    if not isinstance(cells, list):
        return ["holdout carries no cell list"]
    if not cells:
        problems.append(
            "holdout stratum is empty — an empty holdout is not a passing holdout"
        )
    if not holdout.get("reviewer"):
        problems.append("holdout carries no reviewer attribution")
    if holdout.get("stratum") != "reviewer-holdout":
        problems.append("holdout does not declare the reviewer-holdout stratum")
    if not holdout.get("matrixVersion"):
        problems.append("holdout carries no matrixVersion")
    overlap = [cell.get("id") for cell in cells if cell.get("id") in REGISTERED_CELL_IDS]
    if overlap:
        problems.append("holdout reuses locked cell ids: %s" % overlap)
    ids = [cell.get("id") for cell in cells]
    if len(ids) != len(set(ids)):
        problems.append("holdout cell ids are not unique")
    problems.extend(
        cell_schema_problems(cells, "holdout ", optional_fields=HOLDOUT_OPTIONAL_FIELDS)
    )
    for cell in cells:
        if not cell_directory(cell, "reviewer-holdout").is_dir():
            problems.append(
                "holdout %s has no constructed fixture under fixtures/holdout/"
                % cell.get("id")
            )
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
    combined = (
        "pass"
        if all(expectation[layer] in ("pass", "not-engaged") for layer in LAYERS)
        else "fail"
    )
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
    """Out-of-vocabulary observations and replay-set drift are non-adjudicable."""
    problems = []
    seen = observed_tuple(observed)
    for layer in LAYERS:
        if seen[layer] not in LAYER_OUTCOMES[layer]:
            problems.append(
                "layer %s returned an outcome outside the registered vocabulary: %s"
                % (layer, seen[layer])
            )
    replayed = observed.get("upstreamEngaged")
    if replayed is None or sorted(replayed) != sorted(cell["upstreamChecksReplayed"]):
        problems.append(
            "the upstream runner replayed %r, which is not the registered "
            "upstreamChecksReplayed %r" % (replayed, cell["upstreamChecksReplayed"])
        )
    return problems


# --------------------------------------------------------------------------
# publication
# --------------------------------------------------------------------------

def detection_matrix(rows, holdout_rows):
    lines = [
        "# Detection matrix — Study 015",
        "",
        "Per-cell, per-layer outcome adjudicated against the registered expectations.",
        "Every registered cell appears; nothing is excluded. Only `endpoint` rows of the",
        "locked stratum count toward R1; `control-gate` rows are validity gates, and",
        "`demonstration` and `descriptive` rows count toward nothing.",
        "",
        "`not-engaged` means the replayed upstream policy functions had nothing in that",
        "construction to decide — it is not an endorsement. `Suppressed` lists every",
        "further binding code that also fired; adjudication is on the first one alone.",
        "",
        "## Locked replication",
        "",
    ]
    lines.extend(_matrix_table(rows))
    lines.extend(["", "## Reviewer holdout", ""])
    if not holdout_rows:
        lines.append(
            "Not run in this attempt (`--include-holdout` was not passed, or the "
            "preregistration is not yet frozen)."
        )
    else:
        lines.append(
            "Authored by the pre-freeze cross-vendor reviewer and never executed before "
            "the freeze. These expectations predict the **reviewed** apparatus; where a "
            "round-1 fix closed a blind spot the reviewer predicted, the divergence "
            "below is the primary result, not an error."
        )
        lines.append("")
        lines.extend(_matrix_table(holdout_rows))
    return "\n".join(lines) + "\n"


def _matrix_table(rows):
    lines = [
        "| Cell | Role | Attacker | Replayed | UPSTREAM | BINDING | REPLAY | Combined "
        "| Registered | Divergence | Suppressed |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        if row["status"] == NOT_ADJUDICATED:
            lines.append(
                "| `%s` | %s | %s | — | — | — | — | %s | %s | pipeline-invalid | — |"
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
            "| `%s` | %s | %s | %s | `%s` | `%s` | `%s` | `%s` | %s | %s | %s |"
            % (
                row["cell"],
                row["role"],
                row["attackerCapability"],
                ", ".join(row["upstreamReplayed"]) or "—",
                seen["upstream"],
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
                ", ".join("`%s`" % code for code in row["suppressed"]) or "—",
            )
        )
    return lines


def _write_atomic(path, text):
    """Publish atomically: a crash mid-write leaves no torn file behind."""
    path = Path(path)
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def write_outputs(attempt_root, results, rows, holdout_rows):
    attempt_root.mkdir(parents=True, exist_ok=True)
    _write_atomic(
        attempt_root / "RESULTS.json",
        json.dumps(results, indent=2, ensure_ascii=False) + "\n",
    )
    _write_atomic(
        attempt_root / "DETECTION-MATRIX.md", detection_matrix(rows, holdout_rows)
    )


def terminal_invalid(attempt_root, label, problems, provenance, include_holdout=False):
    """Persist a terminal pipeline-invalid record. Every failure path lands here."""
    results = {
        "study": "015-cloudflare-os-boundary",
        "attemptLabel": label,
        "includeHoldout": bool(include_holdout),
        "verdict": VERDICT_INVALID,
        "provenance": provenance,
        "validity": {
            "pipelineInvalidCells": [],
            "records": [{"scope": "attempt", "problem": problem} for problem in problems],
        },
        "detection": {"cells": 0, "adjudicated": 0, "divergentCells": [], "rows": []},
        "holdout": {
            "verdict": HOLDOUT_INVALID if include_holdout else HOLDOUT_NOT_RUN,
            "cells": 0,
            "divergentCells": [],
            "records": [],
            "rows": [],
        },
    }
    write_outputs(attempt_root, results, [], [])
    return results


# --------------------------------------------------------------------------
# the attempt
# --------------------------------------------------------------------------

def run(attempt_root, include_holdout=False):
    attempt_root = Path(attempt_root)
    if attempt_root.exists():
        raise SystemExit("attempt root already exists: %s" % attempt_root)

    # The attempt marker lands before ANYTHING else — including before the pin registry
    # is read, which round 1 found could fail unrecorded.
    attempt_root.mkdir(parents=True)
    provenance = {"harnessPython": platform.python_version()}
    _write_atomic(
        attempt_root / "ATTEMPT.json",
        json.dumps(
            {
                "study": "015-cloudflare-os-boundary",
                "includeHoldout": bool(include_holdout),
                "marker": "written before the pin registry was parsed",
            },
            indent=2,
        )
        + "\n",
    )

    pins_path = STUDY / "harness" / "PINS.json"
    try:
        pins = json.loads(pins_path.read_text(encoding="utf-8"))
    except Exception as error:
        return terminal_invalid(
            attempt_root,
            "PILOT",
            ["the pin registry is unreadable: %s" % error],
            provenance,
            include_holdout,
        )

    frozen = (pins.get("preregistration") or {}).get("sha256") is not None
    label = "REGISTERED" if frozen else "PILOT"

    if frozen and not include_holdout:
        # A registered publication must carry the holdout: round 2 found that omitting
        # it produced a REGISTERED R1 with the prospective stratum silently absent.
        raise SystemExit(
            "a REGISTERED attempt must include the holdout: the preregistration is "
            "frozen, so --include-holdout is required and its result is published "
            "beside R1 (PREREGISTRATION section 1a)"
        )

    if include_holdout and not frozen:
        raise SystemExit(
            "--include-holdout is refused: harness/PINS.json carries a null "
            "preregistration digest, so the preregistration is still DRAFT and the "
            "reviewer-authored holdout stratum may not be executed"
        )

    jpack_bin = os.environ.get("JPACK_BIN")
    provenance.update(
        {
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
        }
    )

    try:
        registry = json.loads(
            (STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8")
        )
        holdout = (
            json.loads(
                (STUDY / "harness" / "MATRIX-HOLDOUT.json").read_text(encoding="utf-8")
            )
            if include_holdout
            else None
        )
    except Exception as error:
        return terminal_invalid(
            attempt_root,
            label,
            ["a registry is unreadable: %s" % error],
            provenance,
            include_holdout,
        )

    # Locked gates only. A holdout defect must never make the locked stratum
    # inconclusive (round 2, blocker 5), so the holdout's own gate runs separately and
    # its problems land in the holdout's own validity records.
    gate_problems = []
    gate_problems.extend(pin_problems(pins, jpack_bin))
    gate_problems.extend(make_manifest.manifest_problems())
    gate_problems.extend(matrix_problems(registry))
    if gate_problems:
        return terminal_invalid(
            attempt_root, label, gate_problems, provenance, include_holdout
        )

    holdout_gate = holdout_problems(holdout) if holdout is not None else []

    # The registered fixture typecheck is a scorer precondition, not only a test: a
    # published score may not call itself valid without it (round 1, finding 8).
    try:
        typecheck_result = typecheck.typecheck_problems(include_holdout=False)
    except Exception as error:
        typecheck_result = ["the fixture typecheck could not run: %s" % error]
    provenance["fixtureTypecheck"] = "clean" if not typecheck_result else "failed"
    if typecheck_result:
        return terminal_invalid(
            attempt_root,
            label,
            ["fixture typecheck: " + problem for problem in typecheck_result],
            provenance,
            include_holdout,
        )

    locked_cells = [dict(cell, stratum="locked-replication") for cell in registry["cells"]]
    holdout_cells = (
        [dict(cell, stratum="reviewer-holdout") for cell in holdout.get("cells") or []]
        if holdout is not None and not holdout_gate
        else []
    )

    # Separate runner batches: a holdout fixture that crashes the runner must not take
    # the locked attempt with it (round 2, blocker 5).
    try:
        upstream_verdicts = cf_runner.ceremony(
            [(cell["id"], cell_directory(cell, "locked-replication"))
             for cell in locked_cells]
        )
    except Exception as error:
        return terminal_invalid(
            attempt_root,
            label,
            ["the upstream runner failed: %s: %s" % (type(error).__name__, error)],
            provenance,
            include_holdout,
        )
    provenance["upstreamApparatus"] = upstream_verdicts.get("apparatus")
    apparatus_gate = apparatus_problems(pins, upstream_verdicts.get("apparatus"))
    if apparatus_gate:
        return terminal_invalid(
            attempt_root, label, apparatus_gate, provenance, include_holdout
        )

    holdout_verdicts = None
    holdout_runner_problem = None
    if holdout_cells:
        try:
            holdout_verdicts = cf_runner.ceremony(
                [(cell["id"], cell_directory(cell, "reviewer-holdout"))
                 for cell in holdout_cells]
            )
        except Exception as error:
            holdout_runner_problem = (
                "the upstream runner failed over the holdout stratum: %s: %s"
                % (type(error).__name__, error)
            )
        else:
            try:
                holdout_typecheck = typecheck.typecheck_problems(include_holdout=True)
            except Exception as error:
                holdout_typecheck = [
                    "the holdout fixture typecheck could not run: %s" % error
                ]
            if holdout_typecheck:
                holdout_runner_problem = "; ".join(holdout_typecheck)

    cells = locked_cells + (holdout_cells if holdout_verdicts is not None else [])

    validity = []
    holdout_validity = []
    rows = []
    holdout_rows = []
    work_root = Path(tempfile.mkdtemp(prefix="study015-score-"))
    try:
        for cell in cells:
            is_holdout = cell["stratum"] == "reviewer-holdout"
            sink = holdout_validity if is_holdout else validity
            verdicts = holdout_verdicts if is_holdout else upstream_verdicts
            row = adjudicate_cell(cell, jpack_bin, work_root, verdicts, sink)
            (holdout_rows if is_holdout else rows).append(row)
    except Exception as error:
        return terminal_invalid(
            attempt_root,
            label,
            [item["problem"] for item in validity]
            + [
                "the harness crashed while adjudicating: %s: %s"
                % (type(error).__name__, error)
            ],
            provenance,
            include_holdout,
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

    holdout_validity.extend(
        {"scope": "holdout-gate", "problem": problem} for problem in holdout_gate
    )
    if holdout_runner_problem:
        holdout_validity.append(
            {"scope": "holdout-apparatus", "problem": holdout_runner_problem}
        )
    holdout_invalid = [row for row in holdout_rows if row["status"] == NOT_ADJUDICATED]
    holdout_diverged = [row for row in holdout_rows if row["divergences"]]
    if holdout is None:
        holdout_verdict = HOLDOUT_NOT_RUN
    elif holdout_gate or holdout_runner_problem or holdout_invalid:
        holdout_verdict = HOLDOUT_INVALID
    elif holdout_diverged:
        holdout_verdict = HOLDOUT_DIVERGENT
    else:
        holdout_verdict = HOLDOUT_CONCORDANT

    results = {
        "study": "015-cloudflare-os-boundary",
        "attemptLabel": label,
        "includeHoldout": bool(include_holdout),
        "verdict": verdict,
        "matrixVersion": registry["matrixVersion"],
        "provenance": provenance,
        "validity": {
            "pipelineInvalidCells": [row["cell"] for row in invalid],
            "controlGateFailures": [row["cell"] for row in failed_gates],
            "records": validity,
        },
        "detection": {
            "stratum": "locked-replication",
            "cells": len(rows),
            "adjudicated": len(rows) - len(invalid),
            "endpointCells": len(endpoints),
            "endpointDivergentCells": [row["cell"] for row in diverged_endpoints],
            "divergentCells": [row["cell"] for row in diverged],
            "rows": rows,
        },
        "holdout": {
            "stratum": "reviewer-holdout",
            "verdict": holdout_verdict,
            "note": "scored separately; nothing here can change R1",
            "cells": len(holdout_rows),
            "divergentCells": [row["cell"] for row in holdout_diverged],
            "pipelineInvalidCells": [row["cell"] for row in holdout_invalid],
            "records": holdout_validity,
            "rows": holdout_rows,
        },
    }
    write_outputs(attempt_root, results, rows, holdout_rows)
    return results


def adjudicate_cell(cell, jpack_bin, work_root, upstream_verdicts, validity):
    """One cell. Never raises: a crash here is a NOT-ADJUDICATED row."""
    shared = {
        "cell": cell["id"],
        "stratum": cell.get("stratum", "locked-replication"),
        "category": cell["category"],
        "role": cell["role"],
        "attackerCapability": cell["attackerCapability"],
        "mutationConstraint": cell.get("mutationConstraint"),
        "modeledDependencies": cell.get("modeledDependencies"),
        "expected": expected_tuple(cell["expected"]),
    }
    observed = None
    try:
        directory = cell_directory(cell, shared["stratum"])
        problems = pipeline_problems(directory, cell)
        if not problems:
            observed = verify.verify_cell(
                directory, jpack_bin, work_root, upstream_verdicts, cell_id=cell["id"]
            )
            problems = vocabulary_problems(cell, observed)
    except Exception as error:
        problems = [
            "the harness raised while verifying: %s: %s" % (type(error).__name__, error)
        ]
        observed = None
    if problems:
        validity.extend({"scope": cell["id"], "problem": problem} for problem in problems)
        return dict(
            shared,
            status=NOT_ADJUDICATED,
            observed=None,
            observedOutcomes=None,
            upstreamReplayed=[],
            suppressed=[],
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
        upstreamReplayed=list(observed.get("upstreamEngaged") or []),
        suppressed=list(observed["binding"].get("suppressed") or []),
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
    holdout = results.get("holdout") or {}
    print(
        "  holdout: %s (%d cells, %d divergent)"
        % (
            holdout.get("verdict"),
            holdout.get("cells", 0),
            len(holdout.get("divergentCells") or []),
        )
    )
    for record in results["validity"]["records"]:
        print("  validity %s: %s" % (record["scope"], record["problem"]))
    for record in holdout.get("records") or []:
        print("  holdout validity %s: %s" % (record["scope"], record["problem"]))
    for row in detection["rows"] + (holdout.get("rows") or []):
        for item in row["divergences"]:
            print(
                "  divergence %s (%s/%s) %s: expected %s, observed %s"
                % (
                    row["cell"],
                    row["stratum"],
                    row["role"],
                    item["layer"],
                    item["expected"],
                    item["observed"],
                )
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
