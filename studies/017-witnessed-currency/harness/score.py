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
import importlib.metadata
import importlib.util
import json
import marshal
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
CAPABILITIES = ("none", "tamper", "authority-key", "witness-key", "delivery")
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
    "pos-consistent", "unchanged", "neg-relabel-attack",
    "neg-sighting-malformed", "neg-limits",
    "wit-split-view-caught", "wit-collusion-a", "wit-collusion-b",
    "wit-one-honest",
    "wit-suppression-omitted", "wit-suppression-corrupted",
    "wit-required-witness-absent",
    "wit-zero-sightings-vacuous", "wit-zero-sightings-enforced",
    "wit-prefix-coverage",
    "wit-recency-refused", "wit-historical-audit",
    "cur-retired-interplay",
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


def bytecode_cache_problems():
    """Refuse when cached bytecode that WOULD BE USED differs from its source.

    A pinned `.py` digest does not describe the bytes the interpreter executes
    if a `__pycache__` entry is loaded instead (round-1 R1-1). Mere existence is
    not the hazard: CPython ignores a cache whose recorded source mtime/size (or
    source hash) does not match and recompiles, and a cache written under
    another tag — pytest's assertion-rewritten copies, for instance — is never
    used by a plain import at all. The hazard is precisely the cache a plain
    import WOULD accept whose code is not this source's, so the check looks at
    exactly `importlib.util.cache_from_source(...)` for every source on the
    adjudication path, unmarshals it, and compares against `compile()` of the
    source. Any difference, or an unreadable entry, refuses. The pinned upstream
    is separately executed from its hashed source bytes and never through this
    path at all.
    """
    problems = []
    sources = sorted(STUDY.glob("witness/*.py")) + sorted(STUDY.glob("harness/*.py"))
    sources += [upstream016.STUDY_016 / relative
                for relative in sorted(upstream016.pinned_files())]
    for source in sources:
        if not source.is_file():
            continue
        cached_path = Path(importlib.util.cache_from_source(str(source)))
        if not cached_path.is_file():
            continue
        where = source.relative_to(STUDY.parent).as_posix()
        data = cached_path.read_bytes()
        if len(data) < 16:
            problems.append("cached bytecode is truncated for " + where)
            continue
        raw = source.read_bytes()
        flags = int.from_bytes(data[4:8], "little")
        if flags & 0b1:
            if data[8:16] != importlib.util.source_hash(raw):
                continue
        else:
            status = source.stat()
            if (int.from_bytes(data[8:12], "little") != int(status.st_mtime) & 0xFFFFFFFF
                    or int.from_bytes(data[12:16], "little") != status.st_size & 0xFFFFFFFF):
                continue
        try:
            cached = marshal.loads(data[16:])
            fresh = compile(raw, str(source), "exec")
        except Exception:
            problems.append("cached bytecode is unreadable for " + where)
            continue
        if cached != fresh:
            problems.append("cached bytecode differs from its source for " + where)
    return problems


def dependency_problems(pins):
    """Enforce the registered third-party versions and their origins.

    The apparatus runs cryptographic and canonicalization code from two
    installed packages before any pin is read; registering their versions is
    the least this study can do about that, and the previous claim that they
    were "transitively pinned by the 016 apparatus" was simply false (round-1
    R1-2).
    """
    problems = []
    registered = (pins.get("dependencies") or {}).get("versions") or {}
    if not registered:
        return ["no dependency versions are registered"]
    studies = STUDY.parent.resolve()
    for name, expected in sorted(registered.items()):
        try:
            found = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            problems.append("registered dependency %s is not installed" % name)
            continue
        if found != expected:
            problems.append("dependency %s is %s; the registry pins %s"
                            % (name, found, expected))
        try:
            origin = Path(importlib.metadata.distribution(name).locate_file("")).resolve()
        except Exception:
            problems.append("dependency %s has no resolvable origin" % name)
            continue
        if origin == studies or studies in origin.parents:
            problems.append("dependency %s resolves inside the studies tree (%s)"
                            % (name, origin))
    return problems


def pin_problems(pins):
    problems = []
    problems.extend(bytecode_cache_problems())
    problems.extend(dependency_problems(pins))
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
        # Derive from the REGISTERED labels, so a changed label is a mismatch
        # rather than silently unenforced (round-1 R1-13); the code constants
        # must equal the registered labels too.
        derived = {}
        for key_member, label_member, constant in (
            ("authorityPublicKey", "authoritySeedLabel", sighting.AUTHORITY_SEED),
            ("witness1PublicKey", "witness1SeedLabel", sighting.WITNESS_1_SEED),
            ("witness2PublicKey", "witness2SeedLabel", sighting.WITNESS_2_SEED),
            ("witness3PublicKey", "witness3SeedLabel", sighting.WITNESS_3_SEED),
        ):
            label = keys.get(label_member)
            if label != constant:
                problems.append("witnessAuthority.%s does not match the builder constant"
                                % label_member)
            derived[key_member] = registry.public_key_b64(registry.private_key(label or ""))
        genesis = registry.build_checkpoint(
            registry.private_key(keys.get("authoritySeedLabel") or ""), sequence=1,
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
    pinned_in_config = []
    counted = []
    head_matches_view = []
    for cid in members:
        directory = build_fixtures.cell_directory(STUDY / "fixtures", cid)
        try:
            document = json.loads((directory / "sightings.json").read_text(encoding="utf-8"))
            config = json.loads((directory / "witnessconfig.json").read_text(encoding="utf-8"))
            snapshot = json.loads((directory / "snapshot.json").read_text(encoding="utf-8"))
        except Exception:
            return {"validated": False, "problem": "cell artifacts unreadable: " + cid}
        # Attribution by VERIFICATION, exactly as the layer does it.
        found = []
        for record in document.get("sightings", ()):
            payload = record.get("sighting")
            if not isinstance(payload, dict):
                continue
            try:
                key.verify(
                    base64.b64decode(record["signature"], validate=True),
                    rfc8785.dumps({"domain": verify_witness.DOMAIN_SIGHTING,
                                   "payload": payload}),
                )
            except Exception:
                continue
            found.append(payload)
        if len(found) != 1:
            return {"validated": False,
                    "problem": "expected exactly one record from the colluding key: " + cid}
        payload = found[0]
        if payload.get("seriesId") != config.get("seriesId"):
            return {"validated": False, "problem": "sighting series is not the cell's: " + cid}
        pinned_in_config.append(encoded in (config.get("witnessKeys") or []))
        counted.append(int(config.get("minimumSightings") or 0) >= 1)
        digests = [
            "sha256:" + hashlib.sha256(
                rfc8785.dumps({"domain": verify_witness.DOMAIN_CHECKPOINT,
                               "payload": record["checkpoint"]})
            ).hexdigest()
            for record in snapshot.get("checkpoints", ())
        ]
        position = payload.get("position")
        head_matches_view.append(
            isinstance(position, int) and 1 <= position <= len(digests)
            and digests[position - 1] == payload.get("head"))
        attested.append(payload)
    a, b = attested
    checks = {
        "oneRecordFromTheSameKeyInEachCell": True,
        "bothSightingsVerifyUnderThatKey": True,
        "keyPinnedInBothConfigurations": all(pinned_in_config),
        "bothSatisfyTheEnforcementFloor": all(counted),
        "eachHeadMatchesItsOwnPresentedView": all(head_matches_view),
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
            "witnessEvidence": {
                "comparisonPerformed": outcome["witness"].get("comparisonPerformed"),
                "validSightings": outcome["witness"].get("validSightings"),
                "unattributedSightings": outcome["witness"].get("unattributedSightings"),
            },
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
        # The upstream digests used for every later check come from the bytes
        # the marker stamped, never from a re-read (round-1 R1-3).
        try:
            upstream016.bind_pins((pins.get("study016") or {}).get("files") or {})
        except upstream016.Upstream016Error as error:
            return terminal(str(error))
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
        # A registered pair whose structure does not validate is a validity
        # failure on the attempt, never a silent footnote (round-1 R1-6).
        broken = sorted(name for name, report in pairs.items()
                        if not report["equivocationStructure"].get("validated"))
        if broken:
            return terminal("registered pair structure did not validate",
                            ["pair %s: %s" % (name, json.dumps(
                                pairs[name]["equivocationStructure"])) for name in broken])
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
