"""The scorer — the only thing that publishes an attempt.

Argument surface: the attempt root plus `--include-holdout`, nothing else.
Fully deterministic and offline — this study needs no evaluator binary and no
external clone; adjudication recomputes everything from frozen fixture bytes
over the two-layer ceremony (`harness/run_verify.py`). No output embeds a
timestamp or an absolute path.

Regime, inherited from Studies 014/016: the marker precedes the registry
parse and carries `pinsRawSha256` over the exact bytes then parsed (single
read); every non-null pin is enforced before adjudication; `REGISTERED`
requires every freeze pin non-null; the validity channel is separate from
detection (NOT-ADJUDICATED, never a true/false detection); the scorer refuses
an existing attempt root; every failure path after the marker persists a
terminal record (`SystemExit`/`KeyboardInterrupt` recorded, then re-raised);
`--include-holdout` refuses while the preregistration or holdout freeze pin
is null, refuses an empty registered stratum, and refuses registered cells
without construction machinery (the machinery lands with the reviewer's
cells before the freeze). The collusion pair is validated STRUCTURALLY from
the two cells' retained bytes — the same pinned witness key attesting
different heads at the same position, each signature verified — never
asserted by hand.
"""

import argparse
import base64
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDY / "harness"))
sys.path.insert(0, str(STUDY / "witness"))

import build_fixtures  # noqa: E402
import run_verify  # noqa: E402
import upstream016  # noqa: E402
import verify_witness  # noqa: E402

PINS_PATH = STUDY / "harness" / "PINS.json"
MATRIX_PATH = STUDY / "harness" / "MATRIX.json"
HOLDOUT_PATH = STUDY / "harness" / "MATRIX-HOLDOUT.json"
PREREG_PATH = STUDY / "PREREGISTRATION.md"

LAYERS = ("currency", "witness")
ROLES = ("endpoint", "control-gate", "demonstration", "descriptive")
CAPABILITIES = ("none", "tamper", "authority-key", "witness-key")
VARIANTS = ("none", "registry", "config", "sightings", "tampered")

FREEZE_PINS = ("preregistration", "matrix", "matrixHoldout", "witnessSpec",
               "studyManifest")
PINNED_DIGEST_MEMBERS = (
    ("preregistration", "PREREGISTRATION.md"),
    ("matrix", "harness/MATRIX.json"),
    ("matrixHoldout", "harness/MATRIX-HOLDOUT.json"),
    ("witnessSpec", "witness/SPEC.md"),
    ("studyManifest", "harness/STUDY-MANIFEST.sha256"),
)

EXPECTED_CELL_IDS = frozenset((
    "pos-consistent", "unchanged", "neg-sighting-forged",
    "neg-unpinned-conflict", "neg-limits",
    "wit-split-view-caught", "wit-collusion-a", "wit-collusion-b",
    "wit-one-honest", "wit-partition-vacuous", "wit-partition-enforced",
    "wit-retention-horizon", "wit-recency-behind", "cur-retired-interplay",
))

CELL_REQUIRED_KEYS = {
    "id", "category", "variant", "role", "attackerCapability",
    "registeredAbsences", "construction", "expected", "note",
}
CELL_OPTIONAL_KEYS = {"registeredUndetected", "pair"}


class PipelineInvalid(RuntimeError):
    pass


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    return sha256_bytes(Path(path).read_bytes())


def atomic_write_bytes(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix="." + path.name + ".", dir=str(path.parent))
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
        path, (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    )


# --------------------------------------------------------------------------
# pins
# --------------------------------------------------------------------------

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
            problems.append("%s expected outcomes do not cover exactly the two layers" % cid)
    if seen != EXPECTED_CELL_IDS:
        gone = sorted(EXPECTED_CELL_IDS - seen)
        extra = sorted(seen - EXPECTED_CELL_IDS)
        if gone:
            problems.append("registered cells absent from the matrix: " + ", ".join(gone))
        if extra:
            problems.append("unregistered cells present in the matrix: " + ", ".join(extra))
    return problems


def pin_problems(pins):
    problems = []
    interpreter = "%d.%d.%d" % sys.version_info[:3]
    pinned_python = (pins.get("harnessPython") or {}).get("version")
    if interpreter != pinned_python:
        problems.append("interpreter %s does not match the pinned %s" % (interpreter, pinned_python))
    problems.extend(upstream016.problems())
    keys = pins.get("witnessAuthority") or {}
    try:
        ns = upstream016.load(build=True)
        registry = ns.checkpoint
        import sighting
        derived = {}
        for member, seed in (
            ("authorityPublicKey", sighting.AUTHORITY_SEED),
            ("witness1PublicKey", sighting.WITNESS_1_SEED),
            ("witness2PublicKey", sighting.WITNESS_2_SEED),
            ("witness3PublicKey", sighting.WITNESS_3_SEED),
        ):
            derived[member] = registry.public_key_b64(registry.private_key(seed))
        genesis = registry.build_checkpoint(
            registry.private_key(sighting.AUTHORITY_SEED), sequence=1,
            series_id=build_fixtures.SERIES_ID, event="add", pack_version="1.0.0",
            pack_digest=build_fixtures.DIGEST_A,
            effective_from=build_fixtures.T1, previous=None,
        )["checkpointDigest"]
        derived["genesisHead"] = genesis
    except Exception as error:
        problems.append("witnessAuthority pins could not be recomputed: %s" % error)
    else:
        for member, value in sorted(derived.items()):
            if keys.get(member) != value:
                problems.append("witnessAuthority.%s does not match its recomputation" % member)
    if verify_witness.DOMAIN_CHECKPOINT != "jps-study016-currency/checkpoint/1":
        problems.append("witness layer checkpoint domain drifted from the pinned upstream's")
    for member, relative in PINNED_DIGEST_MEMBERS:
        pinned = (pins.get(member) or {}).get("sha256")
        if pinned is None:
            continue
        path = STUDY / relative
        if not path.is_file():
            problems.append("%s is pinned but absent" % relative)
        elif sha256_file(path) != pinned:
            problems.append("%s does not match its freeze pin" % relative)
    if (pins.get("studyManifest") or {}).get("sha256") is not None:
        import make_manifest
        problems.extend(make_manifest.verify_problems())
    return problems


# --------------------------------------------------------------------------
# adjudication
# --------------------------------------------------------------------------

def _collusion_structure(members, pins):
    """The pair exhibit, recomputed from retained bytes: the same pinned
    witness key attests different heads at the same position across the two
    cells, each sighting cryptographically verified under that key."""
    import rfc8785
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    encoded = (pins.get("witnessAuthority") or {}).get("witness1PublicKey", "")
    try:
        raw = base64.b64decode(encoded, validate=True)
        key = Ed25519PublicKey.from_public_bytes(raw)
        key_id = "ed25519:" + hashlib.sha256(raw).hexdigest()
    except (ValueError, TypeError):
        return {"validated": False, "problem": "pinned colluding-witness key unreadable"}
    attested = []
    for cid in members:
        directory = build_fixtures.cell_directory(STUDY / "fixtures", cid)
        try:
            document = json.loads((directory / "sightings.json").read_text(encoding="utf-8"))
        except Exception:
            return {"validated": False, "problem": "sightings unreadable: " + cid}
        found = None
        for record in document.get("sightings", ()):
            if record.get("witnessKeyId") != key_id:
                continue
            payload = record["sighting"]
            try:
                key.verify(
                    base64.b64decode(record["signature"], validate=True),
                    rfc8785.dumps({"domain": verify_witness.DOMAIN_SIGHTING,
                                   "payload": payload}),
                )
            except (InvalidSignature, ValueError, TypeError):
                return {"validated": False,
                        "problem": "colluding sighting does not verify: " + cid}
            found = payload
        if found is None:
            return {"validated": False, "problem": "no colluding sighting: " + cid}
        attested.append(found)
    a, b = attested
    checks = {
        "sameWitnessKey": True,
        "bothSightingsVerify": True,
        "samePosition": a["position"] == b["position"],
        "differentHeads": a["head"] != b["head"],
    }
    return {"validated": all(checks.values()), "checks": checks}


def adjudicate(matrix):
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
        if problems:
            cells[cid] = {"role": cell["role"], "adjudicated": False,
                          "problems": problems, "expected": cell["expected"]}
            continue
        outcome = run_verify.verify_cell(directory)
        observed = {layer: outcome[layer]["outcome"] for layer in LAYERS}
        divergent = sorted(
            layer for layer in LAYERS if observed[layer] != cell["expected"][layer]
        )
        cells[cid] = {
            "role": cell["role"], "adjudicated": True,
            "expected": cell["expected"], "observed": observed,
            "combined": outcome["combined"],
            "divergentLayers": divergent, "divergent": bool(divergent),
            "registeredUndetected": bool(cell.get("registeredUndetected")),
            "detail": {layer: outcome[layer].get("detail") for layer in LAYERS},
        }
    return cells


def pair_reports(matrix, cells, pins):
    reports = {}
    for name, members in (matrix.get("pairs") or {}).items():
        outcomes = {
            cid: (cells.get(cid) or {}).get("observed", {}).get("witness")
            for cid in members
        }
        adjudicated = all((cells.get(cid) or {}).get("adjudicated") for cid in members)
        reports[name] = {
            "members": list(members),
            "adjudicated": adjudicated,
            "equivocationStructure": _collusion_structure(members, pins),
            "witnessOutcomes": outcomes,
            "note": (
                "derived, not asserted: the equivocation is recomputed from the "
                "two cells' retained sightings under the pinned colluding key. "
                "Each run is internally valid and satisfies its enforcement "
                "clause; the witness's contradiction exists only across the "
                "pair — the independence clause of the witness contract, "
                "exhibited"
            ),
        }
    return reports


def decide(cells):
    invalid = sorted(cid for cid, record in cells.items() if not record["adjudicated"])
    if invalid:
        return "R1 inconclusive - pipeline-invalid", invalid
    gates = sorted(cid for cid, record in cells.items()
                   if record["role"] == "control-gate" and record["divergent"])
    if gates:
        return "R1 inconclusive - control gate failed", gates
    divergent = sorted(cid for cid, record in cells.items()
                       if record["role"] == "endpoint" and record["divergent"])
    if not divergent:
        return "R1 holds", []
    return "R1 falsified", divergent


def detection_matrix_markdown(label, matrix, cells, pairs, verdict, causes):
    lines = [
        "# Detection matrix — Study 017 (%s)" % label,
        "",
        "Layers: CURRENCY is Study 016's frozen verifier, unchanged; WITNESS is",
        "this study's sighting-comparison step (witness/SPEC.md §2).",
        "",
        "| Cell | Role | Layer | Expected | Observed |",
        "|---|---|---|---|---|",
    ]
    for cell in matrix["cells"]:
        cid = cell["id"]
        record = cells[cid]
        if not record["adjudicated"]:
            lines.append("| %s | %s | — | — | NOT-ADJUDICATED: %s |"
                         % (cid, record["role"], "; ".join(record["problems"])))
            continue
        for layer in LAYERS:
            expected = record["expected"][layer]
            observed = record["observed"][layer]
            marker = " ≠" if expected != observed else ""
            lines.append("| %s | %s | %s | `%s` | `%s`%s |"
                         % (cid, record["role"], layer, expected, observed, marker))
    lines += ["", "## Registered pairs", ""]
    for name, report in sorted(pairs.items()):
        structure = report["equivocationStructure"]
        lines.append(
            "- **%s** (%s): witness equivocation structurally validated from "
            "bytes: %s%s. %s"
            % (name, ", ".join(report["members"]), structure.get("validated"),
               "" if structure.get("validated")
               else " (%s)" % structure.get("problem", structure.get("checks")),
               report["note"])
        )
    lines += ["", "## Verdict", "", "**%s**" % verdict]
    if causes:
        lines += ["", "Cells: " + ", ".join(causes)]
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

    try:
        pins_raw_bytes = PINS_PATH.read_bytes()
        pins_raw_sha256 = sha256_bytes(pins_raw_bytes)
    except OSError:
        pins_raw_bytes = None
        pins_raw_sha256 = None
    write_json(attempt_root / "ATTEMPT.json", {
        "attemptRoot": attempt_root.name,
        "includeHoldout": bool(arguments.include_holdout),
        "study": "017-witnessed-currency",
        "pinsRawSha256": pins_raw_sha256,
    })

    def terminal(problem, problems=None):
        write_json(attempt_root / "RESULTS.json", {
            "attemptRoot": attempt_root.name,
            "pipelineInvalid": True,
            "pinsRawSha256": pins_raw_sha256,
            "problem": problem,
            "problems": problems or [],
        })
        print("pipeline-invalid: %s" % problem, file=sys.stderr)
        return 2

    try:
        if pins_raw_bytes is None:
            return terminal("the pin registry is unreadable")
        pins = json.loads(pins_raw_bytes.decode("utf-8"))
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
            holdout = json.loads(HOLDOUT_PATH.read_text(encoding="utf-8"))
            if not holdout.get("cells"):
                return terminal(
                    "the registered holdout stratum is empty: an empty holdout "
                    "is not a passing holdout and leaves the postdictivity "
                    "finding open"
                )
            return terminal(
                "registered holdout cells exist but this scorer carries no "
                "holdout construction machinery yet; the machinery lands with "
                "the reviewer's cells before the freeze"
            )

        problems = pin_problems(pins)
        if problems:
            return terminal("pin enforcement failed", problems)
        matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        schema_problems = matrix_schema_problems(matrix)
        if schema_problems:
            return terminal("matrix schema enforcement failed", schema_problems)

        cells = adjudicate(matrix)
        pairs = pair_reports(matrix, cells, pins)
        verdict, causes = decide(cells)
        summary = {
            "cells": len(cells),
            "adjudicated": sum(1 for r in cells.values() if r["adjudicated"]),
            "endpoints": sum(1 for r in cells.values() if r["role"] == "endpoint"),
            "endpointDivergences": len(causes) if verdict == "R1 falsified" else 0,
            "registeredUndetectedConfirmed": sorted(
                cid for cid, r in cells.items()
                if r.get("registeredUndetected") and r["adjudicated"] and not r["divergent"]
            ),
        }
        results = {
            "attemptRoot": attempt_root.name,
            "label": label,
            "includeHoldout": bool(arguments.include_holdout),
            "pipelineInvalid": False,
            "pinsRawSha256": pins_raw_sha256,
            "matrixSha256": sha256_file(MATRIX_PATH),
            "verdict": "%s (%s)" % (verdict, label),
            "verdictCells": causes,
            "summary": summary,
            "cells": {cid: cells[cid] for cid in sorted(cells)},
            "pairs": pairs,
            "holdout": None,
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
    except SystemExit as error:
        terminal("SystemExit: %r" % (error.code,))
        raise
    except KeyboardInterrupt:
        terminal("interrupted")
        raise
    except BaseException as error:
        terminal("%s: %s" % (type(error).__name__, error))
        raise


if __name__ == "__main__":
    raise SystemExit(main())
