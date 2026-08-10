"""The scorer — the only thing that publishes an attempt.

Argument surface: the attempt root plus `--include-holdout`, nothing else.
Adjudication is deterministic recomputation from frozen fixture bytes over the
four-layer ceremony (`harness/run_verify.py`); no output embeds a timestamp or
an absolute path, so scoring the same fixtures twice is byte-identical up to
the attempt root's own name.

Regime, inherited from Study 014:

- `ATTEMPT.json` is written before `harness/PINS.json` is parsed, under every
  flag combination, so a malformed registry still leaves a recorded attempt;
  every later failure path persists a terminal pipeline-invalid `RESULTS.json`
  (crashes, `SystemExit`, `KeyboardInterrupt` — recorded, then re-raised).
- Every non-null pin is enforced before any cell is adjudicated; any mismatch
  is terminal. `REGISTERED` requires every freeze pin non-null; otherwise the
  attempt is a `PILOT`, and the enforced pins are enforced under both labels.
- The validity channel is separate from detection: a cell whose fixture fails
  its own manifest, whose artifacts are absent without registration, or whose
  registered byte-identity group diverges is NOT-ADJUDICATED — never a true or
  false detection.
- The scorer refuses an attempt root that already exists; the first invocation
  of the governing command after the freeze is the primary attempt, crash and
  all.
- `--include-holdout` is refused mechanically while `preregistration.sha256`
  or `matrixHoldout.sha256` is null. The holdout construction machinery lands
  together with the reviewer-authored cells during the pre-freeze review
  rounds (014's round-2 shape); until then a post-freeze holdout invocation
  that finds registered holdout cells but no construction hooks is a recorded
  terminal refusal, never a silent skip.
"""

import argparse
import hashlib
import importlib.metadata
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDY / "harness"))
sys.path.insert(0, str(STUDY / "registry"))

import build_fixtures  # noqa: E402  (this study's)
import run_verify  # noqa: E402
import upstream014  # noqa: E402
import verify_currency  # noqa: E402

PINS_PATH = STUDY / "harness" / "PINS.json"
MATRIX_PATH = STUDY / "harness" / "MATRIX.json"
LOCKFILE = STUDY / "upstream" / "requirements-lock-pypi.txt"

LAYERS = ("owp", "binding", "replay", "currency")
ROLES = ("endpoint", "control-gate", "demonstration", "descriptive")
CAPABILITIES = ("none", "tamper", "authority-key", "full-keys")
VARIANTS = ("none", "registry", "config", "chain", "tampered", "resigned")

FREEZE_PINS = ("preregistration", "matrix", "matrixHoldout", "registrySpec",
               "studyManifest")
PINNED_DIGEST_MEMBERS = (
    ("preregistration", "PREREGISTRATION.md"),
    ("matrix", "harness/MATRIX.json"),
    ("matrixHoldout", "harness/MATRIX-HOLDOUT.json"),
    ("registrySpec", "registry/SPEC.md"),
    ("studyManifest", "harness/STUDY-MANIFEST.sha256"),
)

# The frozen cell-id set: a reduced registry must not be able to satisfy zero
# divergence by shrinking the denominator.
EXPECTED_CELL_IDS = frozenset((
    "pos-current", "unchanged", "neg-owp-alive", "neg-snapshot-signature",
    "neg-authority-unpinned", "neg-chain-break",
    "cur-retired-reuse", "cur-successor-current", "cur-concurrent-set",
    "cur-reinstated", "cur-rebind-refused", "cur-series-unknown",
    "cur-authz-rollback-accepted", "cur-split-view-a", "cur-split-view-b",
    "cur-older-snapshot-unpinned", "cur-older-snapshot-pinned",
    "cur-genesis-unpinned", "dem-freshness-legit", "dem-freshness-stale",
))

CELL_REQUIRED_KEYS = {
    "id", "category", "variant", "role", "attackerCapability",
    "registeredAbsences", "construction", "expected", "note",
}
CELL_OPTIONAL_KEYS = {"registeredUndetected", "pair"}


class PipelineInvalid(RuntimeError):
    """A validity failure that voids the attempt rather than adjudicating."""


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    return sha256_bytes(Path(path).read_bytes())


def atomic_write_bytes(path, payload):
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
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def write_json(path, document):
    atomic_write_bytes(
        path,
        (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
    )


# --------------------------------------------------------------------------
# pins (every non-null member enforced; any mismatch is terminal)
# --------------------------------------------------------------------------

def canonical_dependency_name(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def locked_dependency_names():
    names = set()
    for line in LOCKFILE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "--")):
            continue
        head = stripped.split(";")[0].split()[0]
        if "==" not in head:
            continue
        names.add(canonical_dependency_name(head.split("==")[0].split("[")[0]))
    return names


def sanitized_metadata_roots():
    """`sys.path` minus every entry inside the studies tree (014's round 7)."""
    studies = STUDY.parent.resolve()
    roots = []
    for entry in sys.path:
        try:
            resolved = Path(entry or ".").resolve()
        except OSError:
            continue
        if resolved == studies or studies in resolved.parents:
            continue
        roots.append(str(resolved))
    return roots


def locked_dependency_digest(roots=None):
    locked = locked_dependency_names()
    found = {}
    for dist in importlib.metadata.distributions(
        path=sanitized_metadata_roots() if roots is None else list(roots)
    ):
        raw_name = dist.metadata["Name"] if dist.metadata else None
        if not raw_name:
            continue
        name = canonical_dependency_name(raw_name)
        if name not in locked:
            continue
        location = str(dist.locate_file(""))
        found.setdefault(name, set()).add((dist.version, location))
    pairs = []
    for name in sorted(locked):
        sightings = found.get(name)
        if not sightings:
            raise PipelineInvalid(
                "locked dependency %s is not installed in this interpreter" % name
            )
        if len(sightings) > 1:
            raise PipelineInvalid(
                "locked dependency %s resolves ambiguously (%s)"
                % (name, "; ".join(sorted("%s at %s" % s for s in sightings)))
            )
        ((version, _location),) = sightings
        pairs.append("%s==%s" % (name, version))
    return hashlib.sha256(("\n".join(pairs) + "\n").encode("ascii")).hexdigest()


def matrix_schema_problems(matrix):
    problems = []
    cells = matrix.get("cells")
    if not isinstance(cells, list):
        return ["matrix carries no cell list"]
    seen = set()
    for cell in cells:
        if not isinstance(cell, dict) or not isinstance(cell.get("id"), str):
            problems.append("a cell is not an object with a string id")
            continue
        cid = cell["id"]
        if cid in seen:
            problems.append("duplicate cell id: " + cid)
        seen.add(cid)
        missing = CELL_REQUIRED_KEYS - set(cell)
        unknown = set(cell) - CELL_REQUIRED_KEYS - CELL_OPTIONAL_KEYS
        if missing:
            problems.append("%s lacks %s" % (cid, ", ".join(sorted(missing))))
        if unknown:
            problems.append("%s carries unknown members %s" % (cid, ", ".join(sorted(unknown))))
        if cell.get("role") not in ROLES:
            problems.append("%s carries an unregistered role" % cid)
        if cell.get("attackerCapability") not in CAPABILITIES:
            problems.append("%s carries an unregistered attackerCapability" % cid)
        if cell.get("variant") not in VARIANTS:
            problems.append("%s carries an unregistered variant" % cid)
        expected = cell.get("expected")
        if not isinstance(expected, dict) or set(expected) != set(LAYERS):
            problems.append("%s expected outcomes do not cover exactly the four layers" % cid)
    if seen != EXPECTED_CELL_IDS:
        gone = sorted(EXPECTED_CELL_IDS - seen)
        extra = sorted(seen - EXPECTED_CELL_IDS)
        if gone:
            problems.append("registered cells absent from the matrix: " + ", ".join(gone))
        if extra:
            problems.append("unregistered cells present in the matrix: " + ", ".join(extra))
    for group in matrix.get("identityGroups", ()):
        for cid in group:
            if cid not in seen:
                problems.append("identity group names an unknown cell: " + cid)
    return problems


def pin_problems(pins, jpack_bin):
    problems = []
    interpreter = "%d.%d.%d" % sys.version_info[:3]
    pinned_python = (pins.get("harnessPython") or {}).get("version")
    if interpreter != pinned_python:
        problems.append(
            "interpreter %s does not match the pinned %s" % (interpreter, pinned_python)
        )
    if not jpack_bin or not Path(jpack_bin).is_file():
        problems.append("JPACK_BIN is not available")
    elif sha256_file(jpack_bin) != (pins.get("jpack") or {}).get("binarySha256"):
        problems.append("JPACK_BIN does not match the pinned digest")
    for slot in ("v1", "v2"):
        pack = (pins.get("packs") or {}).get(slot) or {}
        path = STUDY / pack.get("path", "")
        if not path.is_file():
            problems.append("vendored pack %s is absent" % slot)
        elif sha256_file(path) != pack.get("sha256"):
            problems.append("vendored pack %s does not match its pinned digest" % slot)
    problems.extend(upstream014.problems())
    ns = upstream014.load() if not problems else None
    if ns is not None:
        expected = (pins.get("openworkproof") or {}).get("installedPackageDigest")
        observed = ns.verify.installed_package_digest()
        if observed != expected:
            problems.append("installed openworkproof package does not match its pin")
        expected_lock = (pins.get("openworkproof") or {}).get("lockedDependencyDigest")
        try:
            observed_lock = locked_dependency_digest()
        except PipelineInvalid as error:
            problems.append(str(error))
        else:
            if observed_lock != expected_lock:
                problems.append("installed dependency set does not match lockedDependencyDigest")
    for member, relative in PINNED_DIGEST_MEMBERS:
        pinned = (pins.get(member) or {}).get("sha256")
        if pinned is None:
            continue
        path = STUDY / relative
        if not path.is_file():
            problems.append("%s is pinned but absent" % relative)
        elif sha256_file(path) != pinned:
            problems.append("%s does not match its freeze pin" % relative)
    manifest_pin = (pins.get("studyManifest") or {}).get("sha256")
    if manifest_pin is not None:
        import make_manifest
        problems.extend(make_manifest.verify_problems())
    return problems


# --------------------------------------------------------------------------
# adjudication
# --------------------------------------------------------------------------

def identity_group_problems(matrix):
    """Registered byte-identity: every cell file identical across each group."""
    problems = {}
    for group in matrix.get("identityGroups", ()):
        reference = group[0]
        for name in build_fixtures.CELL_FILES:
            digests = set()
            for cid in group:
                path = build_fixtures.cell_directory(STUDY / "fixtures", cid) / name
                digests.add(sha256_file(path) if path.is_file() else None)
            if len(digests) > 1:
                for cid in group:
                    problems.setdefault(cid, []).append(
                        "registered byte-identity with %s diverges at %s"
                        % (reference, name)
                    )
    return problems


def adjudicate(matrix, jpack_bin, work_root):
    identity_problems = identity_group_problems(matrix)
    cells = {}
    for cell in matrix["cells"]:
        cid = cell["id"]
        directory = build_fixtures.cell_directory(STUDY / "fixtures", cid)
        problems = []
        if not directory.is_dir():
            problems.append("cell fixture directory is absent")
        else:
            problems.extend(run_verify.manifest_problems(directory))
            problems.extend(run_verify.required_file_problems(directory, cell))
        problems.extend(identity_problems.get(cid, []))
        if problems:
            cells[cid] = {
                "role": cell["role"],
                "adjudicated": False,
                "problems": problems,
                "expected": cell["expected"],
            }
            continue
        work_dir = Path(tempfile.mkdtemp(prefix=cid + "-", dir=str(work_root)))
        outcome = run_verify.verify_cell(directory, jpack_bin, work_dir)
        observed = {layer: outcome[layer]["outcome"] for layer in LAYERS}
        divergent = sorted(
            layer for layer in LAYERS if observed[layer] != cell["expected"][layer]
        )
        cells[cid] = {
            "role": cell["role"],
            "adjudicated": True,
            "expected": cell["expected"],
            "observed": observed,
            "combined": outcome["combined"],
            "divergentLayers": divergent,
            "divergent": bool(divergent),
            "registeredUndetected": bool(cell.get("registeredUndetected")),
            "detail": {
                layer: outcome[layer].get("detail") for layer in LAYERS
            },
        }
    return cells


def pair_reports(matrix, cells):
    reports = {}
    for name, members in (matrix.get("pairs") or {}).items():
        outcomes = {}
        for cid in members:
            record = cells.get(cid) or {}
            outcomes[cid] = (record.get("observed") or {}).get("currency")
        adjudicated = all((cells.get(cid) or {}).get("adjudicated") for cid in members)
        reports[name] = {
            "members": list(members),
            "adjudicated": adjudicated,
            "currencyOutcomes": outcomes,
            "contradictoryVerdicts": adjudicated
            and len(set(outcomes.values())) > 1,
            "forkRevealedToEitherRun": False if adjudicated else None,
            "note": (
                "each run is internally valid under the same two pins; the "
                "contradiction exists only across the pair, which no single "
                "offline run can observe"
            ),
        }
    return reports


def decide(cells):
    """The ordered, exhaustive decision rule (PREREGISTRATION section 5)."""
    invalid = sorted(cid for cid, record in cells.items() if not record["adjudicated"])
    if invalid:
        return "R1 inconclusive - pipeline-invalid", invalid
    gates = sorted(
        cid for cid, record in cells.items()
        if record["role"] == "control-gate" and record["divergent"]
    )
    if gates:
        return "R1 inconclusive - control gate failed", gates
    divergent = sorted(
        cid for cid, record in cells.items()
        if record["role"] == "endpoint" and record["divergent"]
    )
    if not divergent:
        return "R1 holds", []
    return "R1 falsified", divergent


def detection_matrix_markdown(label, matrix, cells, pairs, verdict, causes):
    lines = [
        "# Detection matrix — Study 016 (%s)" % label,
        "",
        "Layers: OWP / BINDING / REPLAY are Study 014's frozen adapter, unchanged;",
        "CURRENCY is this study's registry membership step (registry/SPEC.md §3).",
        "Adjudication is on registered outcome strings alone; `≠` marks a divergence.",
        "",
        "| Cell | Role | Layer | Expected | Observed |",
        "|---|---|---|---|---|",
    ]
    for cell in matrix["cells"]:
        cid = cell["id"]
        record = cells[cid]
        if not record["adjudicated"]:
            lines.append(
                "| %s | %s | — | — | NOT-ADJUDICATED: %s |"
                % (cid, record["role"], "; ".join(record["problems"]))
            )
            continue
        for layer in LAYERS:
            expected = record["expected"][layer]
            observed = record["observed"][layer]
            marker = " ≠" if expected != observed else ""
            lines.append(
                "| %s | %s | %s | `%s` | `%s`%s |"
                % (cid, record["role"], layer, expected, observed, marker)
            )
    lines += ["", "## Registered pairs", ""]
    for name, report in sorted(pairs.items()):
        lines.append(
            "- **%s** (%s): contradictory verdicts: %s; fork revealed to either "
            "run: %s. %s"
            % (
                name,
                ", ".join(report["members"]),
                report["contradictoryVerdicts"],
                report["forkRevealedToEitherRun"],
                report["note"],
            )
        )
    lines += ["", "## Verdict", "", "**%s**" % verdict]
    if causes:
        lines.append("")
        lines.append("Cells: " + ", ".join(causes))
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# the attempt
# --------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--include-holdout", action="store_true")
    arguments = parser.parse_args(argv)

    attempt_root = Path(arguments.attempt_root)
    if attempt_root.exists():
        print("the attempt root already exists; a new attempt needs a new root",
              file=sys.stderr)
        return 2
    attempt_root.mkdir(parents=True)

    # The marker precedes the registry parse under every flag combination.
    write_json(attempt_root / "ATTEMPT.json", {
        "attemptRoot": attempt_root.name,
        "includeHoldout": bool(arguments.include_holdout),
        "study": "016-policy-currency-anchor",
    })

    def terminal(problem, problems=None):
        write_json(attempt_root / "RESULTS.json", {
            "attemptRoot": attempt_root.name,
            "pipelineInvalid": True,
            "problem": problem,
            "problems": problems or [],
        })
        print("pipeline-invalid: %s" % problem, file=sys.stderr)
        return 2

    try:
        pins = json.loads(PINS_PATH.read_text(encoding="utf-8"))
        label = "REGISTERED" if all(
            (pins.get(member) or {}).get("sha256") is not None
            for member in FREEZE_PINS
        ) else "PILOT"

        if arguments.include_holdout:
            if (pins.get("preregistration") or {}).get("sha256") is None or (
                pins.get("matrixHoldout") or {}
            ).get("sha256") is None:
                return terminal(
                    "--include-holdout is refused while the preregistration or "
                    "holdout-matrix freeze pin is null"
                )
            holdout = json.loads(
                (STUDY / "harness" / "MATRIX-HOLDOUT.json").read_text(encoding="utf-8")
            )
            if holdout.get("cells"):
                return terminal(
                    "registered holdout cells exist but this scorer carries no "
                    "holdout construction machinery yet; the machinery lands "
                    "with the reviewer's cells before the freeze"
                )

        problems = pin_problems(pins, os.environ.get("JPACK_BIN"))
        if problems:
            return terminal("pin enforcement failed", problems)
        matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        schema_problems = matrix_schema_problems(matrix)
        if schema_problems:
            return terminal("matrix schema enforcement failed", schema_problems)

        work_root = Path(tempfile.mkdtemp(prefix="study016-attempt-"))
        try:
            cells = adjudicate(matrix, os.environ.get("JPACK_BIN"), work_root)
        finally:
            shutil.rmtree(work_root, ignore_errors=True)
        pairs = pair_reports(matrix, cells)
        verdict, causes = decide(cells)
        summary = {
            "cells": len(cells),
            "adjudicated": sum(1 for r in cells.values() if r["adjudicated"]),
            "endpoints": sum(1 for r in cells.values() if r["role"] == "endpoint"),
            "endpointDivergences": len(causes) if verdict == "R1 falsified" else 0,
            "registeredUndetectedConfirmed": sorted(
                cid for cid, r in cells.items()
                if r.get("registeredUndetected") and r["adjudicated"]
                and not r["divergent"]
            ),
        }
        results = {
            "attemptRoot": attempt_root.name,
            "label": label,
            "includeHoldout": bool(arguments.include_holdout),
            "pipelineInvalid": False,
            "pinsSha256": sha256_file(PINS_PATH),
            "matrixSha256": sha256_file(MATRIX_PATH),
            "verdict": "%s (%s)" % (verdict, label),
            "verdictCells": causes,
            "summary": summary,
            "cells": {cid: cells[cid] for cid in sorted(cells)},
            "pairs": pairs,
        }
        write_json(attempt_root / "RESULTS.json", results)
        atomic_write_bytes(
            attempt_root / "DETECTION-MATRIX.md",
            detection_matrix_markdown(
                label, matrix, cells, pairs, results["verdict"], causes
            ).encode("utf-8"),
        )
        print(results["verdict"])
        return 0
    except SystemExit:
        raise
    except KeyboardInterrupt:
        terminal("interrupted")
        raise
    except BaseException as error:
        terminal("%s: %s" % (type(error).__name__, error))
        raise


if __name__ == "__main__":
    raise SystemExit(main())
