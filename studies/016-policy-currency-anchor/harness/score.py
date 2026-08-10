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
  or `matrixHoldout.sha256` is null, and refused terminally on an empty
  registered stratum. Post-freeze, the reviewer-authored cells are constructed
  INSIDE the attempt (`<attempt>/holdout-fixtures/`, under a
  `HoldoutAttemptContext` only this scorer mints), adjudicated against the
  reviewer's registered expectations, stamped, re-hashed after adjudication,
  and reported in their own section — no holdout outcome enters a
  locked-stratum count and none can change the R1 verdict (014 §1a).
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
VARIANTS = ("none", "registry", "config", "chain", "artifact", "tampered", "resigned")

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
    "pos-current", "unchanged", "neg-owp-alive", "neg-binding-alive",
    "neg-replay-alive", "neg-snapshot-signature", "neg-authority-unpinned",
    "neg-chain-break",
    "cur-retired-reuse", "cur-successor-current", "cur-concurrent-set",
    "cur-reinstated", "cur-rebind-refused", "cur-series-unknown",
    "cur-workorder-remint-accepted", "cur-split-view-a", "cur-split-view-b",
    "cur-split-view-b-stateful", "cur-older-snapshot-pinned",
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
    authority = pins.get("registryAuthority") or {}
    try:
        import checkpoint as registry_writer
        auth_key = registry_writer.private_key(authority.get("authoritySeedLabel", ""))
        foreign_key = registry_writer.private_key(authority.get("foreignSeedLabel", ""))
        derived = {
            "authorityPublicKey": registry_writer.public_key_b64(auth_key),
            "authorityKeyId": registry_writer.key_id(auth_key),
            "foreignPublicKey": registry_writer.public_key_b64(foreign_key),
            "foreignKeyId": registry_writer.key_id(foreign_key),
            "genesisHead": registry_writer.build_checkpoint(
                auth_key, sequence=1,
                series_id=build_fixtures.SERIES_ID, event="add",
                pack_version="0.1.0",
                pack_digest="sha256:" + build_fixtures.PACK_V1_SHA256,
                effective_from=build_fixtures.T1, previous=None,
            )["checkpointDigest"],
            "otherSeriesGenesisHead": registry_writer.build_checkpoint(
                auth_key, sequence=1,
                series_id=build_fixtures.OTHER_SERIES_ID, event="add",
                pack_version="1.0.0",
                pack_digest=build_fixtures.OTHER_SERIES_DIGEST,
                effective_from=build_fixtures.T1, previous=None,
            )["checkpointDigest"],
        }
    except Exception as error:
        problems.append("registryAuthority pins could not be recomputed: %s" % error)
    else:
        for member, value in sorted(derived.items()):
            if authority.get(member) != value:
                problems.append(
                    "registryAuthority.%s does not match its recomputation" % member
                )
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


def _fork_structure(members, pins):
    """Structural fork validation from the two cells' retained bytes (R1-4;
    round-2 residual: authenticated, not label-compared).

    A genuine split view means: identical genesis checkpoint record; BOTH head
    attestations cryptographically verifying under the SAME pinned authority
    key (taken from the enforced registryAuthority pin — never from the
    snapshots' unauthenticated key-id labels); identical per-series trust pins
    across the two cells; the same attested position; different heads.
    Anything less is two registries that merely differ, and the report says so.
    """
    import base64
    import rfc8785
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    try:
        raw = base64.b64decode(
            (pins.get("registryAuthority") or {}).get("authorityPublicKey", ""),
            validate=True,
        )
        pinned = Ed25519PublicKey.from_public_bytes(raw)
    except (ValueError, TypeError):
        return {"validated": False, "problem": "pinned authority key unreadable"}

    parsed = []
    trust_bytes = []
    for cid in members:
        directory = build_fixtures.cell_directory(STUDY / "fixtures", cid)
        try:
            parsed.append(
                json.loads((directory / "snapshot.json").read_text(encoding="utf-8"))
            )
            config = json.loads(
                (directory / "trustconfig.json").read_text(encoding="utf-8")
            )
        except Exception:
            return {"validated": False, "problem": "cell artifacts unreadable: " + cid}
        trust_bytes.append(
            (config.get("seriesId"), config.get("authorityPublicKey"),
             config.get("genesisHead"))
        )

    def attests_under_pinned(snapshot):
        payload = snapshot["attestation"]["payload"]
        try:
            pinned.verify(
                base64.b64decode(snapshot["attestation"]["signature"], validate=True),
                rfc8785.dumps({"domain": "jps-study016-currency/snapshot/1",
                               "payload": payload}),
            )
            return True
        except (InvalidSignature, ValueError, TypeError):
            return False

    a, b = parsed
    checks = {
        "sameGenesisRecord": a["checkpoints"][0] == b["checkpoints"][0],
        "bothAttestationsVerifyUnderPinnedAuthority": (
            attests_under_pinned(a) and attests_under_pinned(b)
        ),
        "samePerSeriesTrustPins": trust_bytes[0] == trust_bytes[1],
        "samePosition": (
            a["attestation"]["payload"]["position"]
            == b["attestation"]["payload"]["position"]
        ),
        "differentHeads": (
            a["attestation"]["payload"]["head"] != b["attestation"]["payload"]["head"]
        ),
    }
    return {"validated": all(checks.values()), "checks": checks}


def pair_reports(matrix, cells, pins):
    reports = {}
    for name, members in (matrix.get("pairs") or {}).items():
        outcomes = {}
        for cid in members:
            record = cells.get(cid) or {}
            outcomes[cid] = (record.get("observed") or {}).get("currency")
        adjudicated = all((cells.get(cid) or {}).get("adjudicated") for cid in members)
        structure = _fork_structure(members, pins)
        reports[name] = {
            "members": list(members),
            "adjudicated": adjudicated,
            "forkStructure": structure,
            "currencyOutcomes": outcomes,
            "contradictoryVerdicts": adjudicated
            and len(set(outcomes.values())) > 1,
            "note": (
                "derived, not asserted: forkStructure is recomputed from the "
                "two snapshot artifacts, and the outcomes above are the "
                "adjudicated ones. What the pair registers as impossible is "
                "detection by a fresh, stateless, per-series-pinned verifier "
                "given exactly one view; the stateful arm "
                "(cur-split-view-b-stateful) shows prior-acceptance state "
                "converting the silence into a refusal"
            ),
        }
    return reports


HOLDOUT_PATH = STUDY / "harness" / "MATRIX-HOLDOUT.json"
PREREG_PATH = STUDY / "PREREGISTRATION.md"


def holdout_schema_problems(holdout):
    """Per-cell schema of the reviewer stratum + a hook for every cell."""
    problems = []
    cells = holdout.get("cells")
    if not isinstance(cells, list) or not cells:
        return ["holdout registry carries no cell list"]
    seen = set()
    for cell in cells:
        if not isinstance(cell, dict) or not isinstance(cell.get("id"), str):
            problems.append("a holdout cell is not an object with a string id")
            continue
        cid = cell["id"]
        if cid in seen:
            problems.append("duplicate holdout cell id: " + cid)
        seen.add(cid)
        missing = CELL_REQUIRED_KEYS - set(cell)
        if missing:
            problems.append("%s lacks %s" % (cid, ", ".join(sorted(missing))))
        if cell.get("role") not in ROLES:
            problems.append("%s carries an unregistered role" % cid)
        if cell.get("attackerCapability") not in CAPABILITIES:
            problems.append("%s carries an unregistered attackerCapability" % cid)
        if cell.get("variant") not in VARIANTS:
            problems.append("%s carries an unregistered variant" % cid)
        expected = cell.get("expected")
        if not isinstance(expected, dict) or set(expected) != set(LAYERS):
            problems.append("%s expected outcomes do not cover exactly the four layers" % cid)
        if cid not in build_fixtures.HOLDOUT_HOOKS:
            problems.append("no construction hook is registered for " + cid)
    return problems


def _stamp_holdout_fixtures(root, cells):
    """Digest stamps for every construction output, taken before adjudication."""
    stamps = {}
    for cell in cells:
        directory = Path(root) / cell["id"]
        files = {}
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                files[path.relative_to(directory).as_posix()] = sha256_file(path)
        stamps[cell["id"]] = files
    return stamps


def _holdout_integrity(root, stamps):
    """Post-adjudication re-hash of every stamped artifact (014 round-5)."""
    report = []
    for cell_id, files in sorted(stamps.items()):
        directory = Path(root) / cell_id
        seen = set()
        for relative, stamped in sorted(files.items()):
            path = directory / relative
            final = sha256_file(path) if path.is_file() else None
            report.append({"cell": cell_id, "path": relative,
                           "stampedSha256": stamped, "finalSha256": final,
                           "match": final == stamped})
            seen.add(relative)
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                relative = path.relative_to(directory).as_posix()
                if relative not in seen:
                    report.append({"cell": cell_id, "path": relative,
                                   "stampedSha256": None,
                                   "finalSha256": sha256_file(path),
                                   "match": False})
    return report


def adjudicate_holdout(holdout, attempt_root, pins_raw_sha256, jpack_bin, work_root):
    """Construct inside the attempt, adjudicate, report separately (014 §1a)."""
    context = build_fixtures.HoldoutAttemptContext(
        attempt_root=str(attempt_root),
        pins_raw_sha256=pins_raw_sha256,
        preregistration_sha256=sha256_file(PREREG_PATH),
        matrix_holdout_sha256=sha256_file(HOLDOUT_PATH),
    )
    fixtures_root = Path(attempt_root) / "holdout-fixtures"
    construction = build_fixtures.construct_holdout(
        context, fixtures_root, holdout["cells"]
    )
    stamps = _stamp_holdout_fixtures(fixtures_root, holdout["cells"])
    cells = {}
    for cell in holdout["cells"]:
        cid = cell["id"]
        record = construction.get(cid, {})
        if record.get("status") != "built":
            cells[cid] = {
                "role": cell["role"], "adjudicated": False,
                "problems": ["construction status: %s" % record.get("status"),
                             record.get("harnessError", "")],
                "expected": cell["expected"],
            }
            continue
        directory = fixtures_root / cid
        problems = run_verify.manifest_problems(directory)
        problems += run_verify.required_file_problems(directory, cell)
        if problems:
            cells[cid] = {"role": cell["role"], "adjudicated": False,
                          "problems": problems, "expected": cell["expected"]}
            continue
        work_dir = Path(tempfile.mkdtemp(prefix=cid + "-", dir=str(work_root)))
        outcome = run_verify.verify_cell(directory, jpack_bin, work_dir)
        observed = {layer: outcome[layer]["outcome"] for layer in LAYERS}
        divergent = sorted(
            layer for layer in LAYERS if observed[layer] != cell["expected"][layer]
        )
        cells[cid] = {
            "role": cell["role"], "adjudicated": True,
            "expected": cell["expected"], "observed": observed,
            "combined": outcome["combined"],
            "divergentLayers": divergent, "divergent": bool(divergent),
            "detail": {layer: outcome[layer].get("detail") for layer in LAYERS},
        }
    integrity = _holdout_integrity(fixtures_root, stamps)
    gates = sorted(cid for cid, r in cells.items()
                   if r["role"] == "control-gate"
                   and (not r["adjudicated"] or r["divergent"]))
    invalid = sorted(cid for cid, r in cells.items() if not r["adjudicated"])
    divergent = sorted(cid for cid, r in cells.items()
                       if r["adjudicated"] and r["divergent"]
                       and r["role"] != "control-gate")
    integrity_clean = all(item["match"] for item in integrity)
    if invalid or not integrity_clean:
        summary = "holdout inconclusive - validity problem"
    elif gates:
        summary = "holdout inconclusive - control gate failed"
    elif divergent:
        summary = "holdout DIVERGENT"
    else:
        summary = "holdout concordant - %d/%d adjudicated, 0 divergent" % (
            len(cells), len(cells)
        )
    return {
        "reviewer": holdout.get("reviewer"),
        "construction": construction,
        "fixtureDigests": stamps,
        "cells": cells,
        "postAdjudicationIntegrity": integrity,
        "gatesFailed": gates,
        "notAdjudicated": invalid,
        "divergent": divergent,
        "summary": summary,
        "note": ("reported separately: no holdout outcome enters a locked-stratum "
                 "count and none can change the R1 verdict"),
    }


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


def detection_matrix_markdown(label, matrix, cells, pairs, verdict, causes,
                              holdout_report=None):
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
        structure = report["forkStructure"]
        lines.append(
            "- **%s** (%s): fork structurally validated from bytes: %s%s; "
            "contradictory adjudicated verdicts: %s. %s"
            % (
                name,
                ", ".join(report["members"]),
                structure.get("validated"),
                "" if structure.get("validated")
                else " (%s)" % structure.get("problem", structure.get("checks")),
                report["contradictoryVerdicts"],
                report["note"],
            )
        )
    if holdout_report is not None:
        lines += ["", "## Reviewer holdout (separate stratum)", "",
                  "| Cell | Role | Layer | Expected | Observed |",
                  "|---|---|---|---|---|"]
        for cid in sorted(holdout_report["cells"]):
            record = holdout_report["cells"][cid]
            if not record["adjudicated"]:
                lines.append("| %s | %s | — | — | NOT-ADJUDICATED: %s |"
                             % (cid, record["role"],
                                "; ".join(p for p in record["problems"] if p)))
                continue
            for layer in LAYERS:
                expected = record["expected"][layer]
                observed = record["observed"][layer]
                marker = " ≠" if expected != observed else ""
                lines.append("| %s | %s | %s | `%s` | `%s`%s |"
                             % (cid, record["role"], layer, expected, observed, marker))
        lines += ["", "**%s**" % holdout_report["summary"]]
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

    # The marker precedes the registry PARSE under every flag combination, and
    # it carries the raw-byte digest of the registry it is about to trust
    # (round-1 R1-12): even a malformed PINS.json leaves an attempt record
    # tied to the exact registry bytes it saw.
    try:
        pins_raw_bytes = PINS_PATH.read_bytes()
        pins_raw_sha256 = sha256_bytes(pins_raw_bytes)
    except OSError:
        pins_raw_bytes = None
        pins_raw_sha256 = None
    write_json(attempt_root / "ATTEMPT.json", {
        "attemptRoot": attempt_root.name,
        "includeHoldout": bool(arguments.include_holdout),
        "study": "016-policy-currency-anchor",
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
        # The SAME bytes the marker hashed are the bytes parsed here (round-2
        # residual of R1-12): no second read, no hash/parse divergence window.
        pins = json.loads(pins_raw_bytes.decode("utf-8"))
        label = "REGISTERED" if all(
            (pins.get(member) or {}).get("sha256") is not None
            for member in FREEZE_PINS
        ) else "PILOT"

        holdout = None
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
            if not holdout.get("cells"):
                return terminal(
                    "the registered holdout stratum is empty: an empty holdout "
                    "is not a passing holdout (PREREGISTRATION section 1a) and "
                    "leaves the postdictivity finding open - refused, never "
                    "silently adjudicated as locked-only (round-1 R1-11)"
                )
            schema_problems = holdout_schema_problems(holdout)
            if schema_problems:
                return terminal("holdout registry enforcement failed", schema_problems)

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
        holdout_report = None
        if holdout is not None:
            work_root_holdout = Path(tempfile.mkdtemp(prefix="study016-holdout-"))
            try:
                holdout_report = adjudicate_holdout(
                    holdout, attempt_root, pins_raw_sha256,
                    os.environ.get("JPACK_BIN"), work_root_holdout,
                )
            finally:
                shutil.rmtree(work_root_holdout, ignore_errors=True)
        pairs = pair_reports(matrix, cells, pins)
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
            "pinsRawSha256": pins_raw_sha256,
            "matrixSha256": sha256_file(MATRIX_PATH),
            "verdict": "%s (%s)" % (verdict, label),
            "verdictCells": causes,
            "summary": summary,
            "cells": {cid: cells[cid] for cid in sorted(cells)},
            "pairs": pairs,
            "holdout": holdout_report,
        }
        write_json(attempt_root / "RESULTS.json", results)
        atomic_write_bytes(
            attempt_root / "DETECTION-MATRIX.md",
            detection_matrix_markdown(
                label, matrix, cells, pairs, results["verdict"], causes,
                holdout_report,
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
