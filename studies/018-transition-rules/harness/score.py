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


def _cache_problems_for(sources):
    """Compare every cache a plain import WOULD accept against its source.

    CPython uses a timestamp cache only when mtime/size match, and a
    *checked* hash cache only when the source hash matches — both are safely
    ignored otherwise. An **unchecked** hash cache is used without validating
    anything (round-2 residual of R1-1), so it is always compared here.
    """
    problems = []
    for source in sources:
        source = Path(source)
        if not source.is_file():
            continue
        cached_path = Path(importlib.util.cache_from_source(str(source)))
        if not cached_path.is_file():
            continue
        where = source.name
        data = cached_path.read_bytes()
        if len(data) < 16:
            problems.append("cached bytecode is truncated for " + where)
            continue
        raw = source.read_bytes()
        flags = int.from_bytes(data[4:8], "little")
        if flags & 0b1:
            # hash-based; bit 1 = check_source. Unchecked caches are used as-is.
            if (flags & 0b10) and data[8:16] != importlib.util.source_hash(raw):
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


def _own_sources():
    return sorted(STUDY.glob("rule/*.py")) + sorted(STUDY.glob("harness/*.py"))


# BOOTSTRAP — runs before any study or third-party module is imported, so the
# check precedes the code it is about to trust (round-2 residual of R1-1/R1-2).
# `__main__` is never loaded from a cache, so this file itself is exempt by
# construction. Stdlib only, deliberately.
_BOOTSTRAP_PROBLEMS = _cache_problems_for(_own_sources())

sys.path.insert(0, str(STUDY / "harness"))
sys.path.insert(0, str(STUDY / "witness"))

import rfc8785  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey  # noqa: E402

import build_fixtures  # noqa: E402  (this study's; imported after the bootstrap)
import run_verify  # noqa: E402
import upstream016  # noqa: E402
import transition  # noqa: E402

PINS_PATH = STUDY / "harness" / "PINS.json"
MATRIX_PATH = STUDY / "harness" / "MATRIX.json"
HOLDOUT_PATH = STUDY / "harness" / "MATRIX-HOLDOUT.json"
HOLDOUT_EVIDENCE_PATH = STUDY / "harness" / "MATRIX-HOLDOUT-EVIDENCE.json"
PREREG_PATH = STUDY / "PREREGISTRATION.md"

LAYERS = ("currency", "transition")
ROLES = ("endpoint", "control-gate", "demonstration", "descriptive")
CAPABILITIES = ("none", "tamper", "authority-key", "full-keys")
VARIANTS = ("none", "registry", "config", "citation", "tampered")

FREEZE_PINS = ("preregistration", "matrix", "matrixHoldout",
               "matrixHoldoutEvidence", "ruleSpec", "studyManifest")
PINNED_DIGEST_MEMBERS = (
    ("preregistration", "PREREGISTRATION.md"),
    ("matrix", "harness/MATRIX.json"),
    ("matrixHoldout", "harness/MATRIX-HOLDOUT.json"),
    ("matrixHoldoutEvidence", "harness/MATRIX-HOLDOUT-EVIDENCE.json"),
    ("ruleSpec", "rule/SPEC.md"),
    ("studyManifest", "harness/STUDY-MANIFEST.sha256"),
)

EXPECTED_CELL_IDS = frozenset((
    "pos-current-stop", "pos-current-window", "pos-current-grandfather", "unchanged",
    "neg-ruleconfig-malformed", "neg-currency-unauthenticated",
    "div-stop-at-retirement", "div-position-window-open",
    "div-position-window-elapsed", "div-grandfather-on-cited-support",
    "cite-absent-stop-unaffected", "cite-absent-grandfather-unavailable",
    "cite-unsupported-grandfather", "cite-unsupported-window", "cite-foreign-history",
    "bnd-backdated-citation", "bnd-duration-window", "bnd-mint-time-refusal",
    "bnd-foreign-series-rule",
))

CELL_REQUIRED_KEYS = {
    "id", "category", "variant", "role", "attackerCapability",
    "registeredAbsences", "construction", "expected", "note",
}
CELL_OPTIONAL_KEYS = {"registeredUndetected", "pair", "expectedRuleEvidence"}


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
    """The bootstrap result for this study's own modules (computed before they
    were imported), plus the pinned upstream's sources. The upstream is also
    executed from its hashed bytes and never through import machinery."""
    problems = list(_BOOTSTRAP_PROBLEMS)
    problems.extend(_cache_problems_for(
        upstream016.STUDY_016 / relative for relative in sorted(upstream016.pinned_files())))
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
        # Authenticate the ORIGIN of the module actually imported, not merely
        # the distribution's (round-2 residual of R1-2): a shadowing copy on an
        # earlier path entry would otherwise satisfy a version check while
        # different code ran. Package CONTENTS are not digest-pinned here, and
        # the preregistration records that as a stated limitation rather than
        # claiming otherwise.
        module = sys.modules.get(name.replace("-", "_"))
        if module is None:
            problems.append("registered dependency %s is not imported" % name)
            continue
        module_file = getattr(module, "__file__", None)
        if module_file is None:
            problems.append("dependency %s exposes no __file__ to authenticate" % name)
            continue
        resolved = Path(module_file).resolve()
        try:
            owned = {Path(origin, entry).resolve()
                     for entry in (importlib.metadata.distribution(name).files or ())}
        except Exception:
            owned = set()
        if not owned:
            problems.append("dependency %s declares no file inventory to check against" % name)
        elif resolved not in owned:
            problems.append("dependency %s is imported from %s, which its own "
                            "distribution does not own" % (name, resolved))
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
    keys = pins.get("registryAuthority") or {}
    try:
        ns = upstream016.load(build=True)
        registry = ns.checkpoint
        label = keys.get("authoritySeedLabel")
        if not isinstance(label, str) or not label:
            problems.append("registryAuthority.authoritySeedLabel is not registered")
        else:
            registry.private_key(label)
    except Exception as error:
        problems.append("registryAuthority pins could not be recomputed: %s" % error)
    if transition.RULES != ("stop-at-retirement", "position-window", "grandfather-on-cited-support"):
        problems.append("the registered rule vocabulary has drifted")
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

def identity_group_problems(matrix):
    """Registered byte-identity: every cell file identical across each group.

    This study's group is the exhibit itself — an honest citation and a
    chosen-early one are the same bytes — so a divergence is a validity
    failure on those cells, never a finding.
    """
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
                        "registered byte-identity with %s diverges at %s" % (reference, name))
    return problems


def adjudicate(matrix):
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
            cells[cid] = {"role": cell["role"], "adjudicated": False,
                          "problems": problems, "expected": cell["expected"]}
            continue
        outcome = run_verify.verify_cell(directory)
        observed = {layer: outcome[layer]["outcome"] for layer in LAYERS}
        divergent = sorted(
            layer for layer in LAYERS if observed[layer] != cell["expected"][layer]
        )
        # The registered structured expectation is adjudicated, not decorative
        # (round-2 residual of R1-9): a cell that registers whether a comparison
        # happened diverges if it did not.
        for field, value in (cell.get("expectedRuleEvidence") or {}).items():
            if outcome["transition"].get(field) != value:
                divergent = sorted(set(divergent) | {"transition:" + field})
        cells[cid] = {
            "role": cell["role"], "adjudicated": True,
            "expected": cell["expected"], "observed": observed,
            "combined": outcome["combined"],
            "divergentLayers": divergent, "divergent": bool(divergent),
            "registeredUndetected": bool(cell.get("registeredUndetected")),
            "ruleEvidence": {
                "citedPosition": outcome["transition"].get("citedPosition"),
                "retiredAtPosition": outcome["transition"].get("retiredAtPosition"),
            },
            "detail": {layer: outcome[layer].get("detail") for layer in LAYERS},
        }
    return cells


def pair_reports(matrix, cells, pins):
    """This study registers no pairs; identity groups carry its byte-identity
    exhibit instead, and the scorer verifies those."""
    return {}


def holdout_schema_problems(holdout):
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
            problems.append("%s expected outcomes do not cover exactly the two layers" % cid)
        if cid not in build_fixtures.HOLDOUT_HOOKS:
            problems.append("no construction hook is registered for " + cid)
    return problems


def _stamp_holdout(root, cells):
    stamps = {}
    for cell in cells:
        directory = Path(root) / cell["id"]
        stamps[cell["id"]] = {
            path.relative_to(directory).as_posix(): sha256_file(path)
            for path in sorted(directory.rglob("*")) if path.is_file()
        }
    return stamps


def _holdout_integrity(root, stamps):
    report = []
    for cell_id, files in sorted(stamps.items()):
        directory = Path(root) / cell_id
        seen = set()
        for relative, stamped in sorted(files.items()):
            path = directory / relative
            final = sha256_file(path) if path.is_file() else None
            report.append({"cell": cell_id, "path": relative, "stampedSha256": stamped,
                           "finalSha256": final, "match": final == stamped})
            seen.add(relative)
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                relative = path.relative_to(directory).as_posix()
                if relative not in seen:
                    report.append({"cell": cell_id, "path": relative,
                                   "stampedSha256": None,
                                   "finalSha256": sha256_file(path), "match": False})
    return report


def holdout_evidence_expectations():
    """The structured-evidence expectations for the reviewer's cells.

    Kept in a SEPARATE pinned file so the reviewer's block stays byte-for-byte
    as authored (round-3 R3-1): these values are read off that block's own
    construction text, registered and pinned at the freeze, and adjudicated as
    additional divergence channels.
    """
    if not HOLDOUT_EVIDENCE_PATH.is_file():
        return {}
    return json.loads(HOLDOUT_EVIDENCE_PATH.read_text(encoding="utf-8"))["cells"]


EVIDENCE_FIELDS = {"citedPosition": (int, type(None)), "retiredAtPosition": (int, type(None))}


def holdout_evidence_problems(holdout, evidence):
    """Exact per-cell validation of the reviewer stratum's structured
    expectations, retargeted to THIS study's fields (round-1 R1-3: the path was
    copied from Study 017 and still demanded witness fields this study never
    produces). A partial entry would silently drop a divergence channel."""
    problems = []
    registered = {c["id"] for c in holdout["cells"]}
    for cid in sorted(registered - set(evidence)):
        problems.append("no registered evidence for " + cid)
    for cid in sorted(set(evidence) - registered):
        problems.append("evidence registered for unknown cell " + cid)
    for cid in sorted(registered & set(evidence)):
        fields = evidence[cid]
        if not isinstance(fields, dict) or set(fields) != set(EVIDENCE_FIELDS):
            problems.append("%s evidence does not carry exactly %s"
                            % (cid, ", ".join(sorted(EVIDENCE_FIELDS))))
            continue
        for field in sorted(EVIDENCE_FIELDS):
            value = fields[field]
            if value is not None and (not isinstance(value, int)
                                      or isinstance(value, bool) or value < 1):
                problems.append("%s evidence %s is neither null nor a positive integer"
                                % (cid, field))
    return problems


def adjudicate_holdout(holdout, attempt_root, pins_raw_sha256):
    """Construct inside the attempt, adjudicate, report separately (014/016 §1a)."""
    context = build_fixtures.HoldoutAttemptContext(
        attempt_root=str(attempt_root),
        pins_raw_sha256=pins_raw_sha256,
        preregistration_sha256=sha256_file(PREREG_PATH),
        matrix_holdout_sha256=sha256_file(HOLDOUT_PATH),
        matrix_holdout_evidence_sha256=sha256_file(HOLDOUT_EVIDENCE_PATH),
    )
    evidence_expectations = holdout_evidence_expectations()
    root = Path(attempt_root) / "holdout-fixtures"
    construction = build_fixtures.construct_holdout(context, root, holdout["cells"])
    stamps = _stamp_holdout(root, holdout["cells"])
    cells = {}
    for cell in holdout["cells"]:
        cid = cell["id"]
        record = construction.get(cid, {})
        if record.get("status") != "built":
            cells[cid] = {"role": cell["role"], "adjudicated": False,
                          "problems": ["construction status: %s" % record.get("status"),
                                       record.get("harnessError", "")],
                          "expected": cell["expected"]}
            continue
        directory = root / cid
        problems = run_verify.manifest_problems(directory)
        problems += run_verify.required_file_problems(directory, cell)
        if problems:
            cells[cid] = {"role": cell["role"], "adjudicated": False,
                          "problems": problems, "expected": cell["expected"]}
            continue
        outcome = run_verify.verify_cell(directory)
        observed = {layer: outcome[layer]["outcome"] for layer in LAYERS}
        divergent = sorted(l for l in LAYERS if observed[l] != cell["expected"][l])
        # The reviewer's cells register structured evidence values; adjudicate
        # each as its own divergence channel (round-3 R3-1), so a regression
        # that reached the same outcome by different evidence still diverges.
        for field, value in (evidence_expectations.get(cid) or {}).items():
            if outcome["transition"].get(field) != value:
                divergent = sorted(set(divergent) | {"transition:" + field})
        cells[cid] = {
            "role": cell["role"], "adjudicated": True, "expected": cell["expected"],
            "expectedRuleEvidence": evidence_expectations.get(cid) or {},
            "observed": observed, "combined": outcome["combined"],
            "divergentLayers": divergent, "divergent": bool(divergent),
            "ruleEvidence": {
                "citedPosition": outcome["transition"].get("citedPosition"),
                "retiredAtPosition": outcome["transition"].get("retiredAtPosition"),
            },
            "detail": {l: outcome[l].get("detail") for l in LAYERS},
        }
    integrity = _holdout_integrity(root, stamps)
    invalid = sorted(c for c, r in cells.items() if not r["adjudicated"])
    gates = sorted(c for c, r in cells.items() if r["role"] == "control-gate"
                   and (not r["adjudicated"] or r["divergent"]))
    divergent = sorted(c for c, r in cells.items() if r["adjudicated"] and r["divergent"]
                       and r["role"] != "control-gate")
    clean = all(item["match"] for item in integrity)
    if invalid or not clean:
        summary = "holdout inconclusive - validity problem"
    elif gates:
        summary = "holdout inconclusive - control gate failed"
    elif divergent:
        summary = "holdout DIVERGENT"
    else:
        summary = "holdout concordant - %d/%d adjudicated, 0 divergent" % (len(cells), len(cells))
    return {"reviewer": holdout.get("reviewer"), "construction": construction,
            "fixtureDigests": stamps, "cells": cells,
            "postAdjudicationIntegrity": integrity, "notAdjudicated": invalid,
            "gatesFailed": gates, "divergent": divergent, "summary": summary,
            "note": "reported separately: no holdout outcome enters a locked-stratum "
                    "count and none can change the R1 verdict"}


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
        "# Decision matrix — Study 018 (%s)" % label,
        "",
        "Layers: CURRENCY is Study 016's frozen verifier, unchanged — membership at",
        "snapshot; TRANSITION is this study's rule evaluator (rule/SPEC.md §3), which",
        "consumes that verdict as a fact and answers usability under a stated rule.",
        "",
        "| Cell | Role | Layer | Expected | Observed | Rule evidence |",
        "|---|---|---|---|---|---|",
    ]
    for cell in matrix["cells"]:
        cid = cell["id"]
        record = cells[cid]
        if not record["adjudicated"]:
            lines.append("| %s | %s | — | — | NOT-ADJUDICATED: %s | — |"
                         % (cid, record["role"], "; ".join(record["problems"])))
            continue
        evidence = record.get("ruleEvidence") or {}
        for layer in LAYERS:
            expected = record["expected"][layer]
            observed = record["observed"][layer]
            marker = " ≠" if expected != observed else ""
            shown = "—" if layer != "transition" else (
                "compared=%s, attributed=%s, unattributed=%s"
                % (evidence.get("comparisonPerformed"),
                   evidence.get("validSightings"),
                   evidence.get("unattributedSightings")))
            lines.append("| %s | %s | %s | `%s` | `%s`%s | %s |"
                         % (cid, record["role"], layer, expected, observed, marker, shown))
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
        "study": "018-transition-rules",
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

        holdout = None
        if arguments.include_holdout:
            # EVERY freeze pin must be non-null before the stratum may execute
            # (round-4 R4-1): with the evidence pin null the run would merely be
            # labelled PILOT while the holdout still ran, which would let the
            # structured expectations be chosen after observing results.
            null_pins = sorted(member for member in FREEZE_PINS
                               if (pins.get(member) or {}).get("sha256") is None)
            if null_pins:
                return terminal(
                    "--include-holdout is refused while a freeze pin is null: "
                    + ", ".join(null_pins))
            holdout = json.loads(HOLDOUT_PATH.read_text(encoding="utf-8"))
            if not holdout.get("cells"):
                return terminal(
                    "the registered holdout stratum is empty: an empty holdout "
                    "is not a passing holdout and leaves the postdictivity "
                    "finding open"
                )
            schema_problems = holdout_schema_problems(holdout)
            if schema_problems:
                return terminal("holdout registry enforcement failed", schema_problems)
            # Missing or partial structured expectations are terminal, never a
            # silent empty map (round-4 R4-1).
            if not HOLDOUT_EVIDENCE_PATH.is_file():
                return terminal("the registered holdout evidence map is absent")
            evidence = holdout_evidence_expectations()
            evidence_problems = holdout_evidence_problems(holdout, evidence)
            if evidence_problems:
                return terminal("holdout evidence expectations are incomplete",
                                evidence_problems)

        problems = pin_problems(pins)
        if problems:
            return terminal("pin enforcement failed", problems)
        matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        schema_problems = matrix_schema_problems(matrix)
        if schema_problems:
            return terminal("matrix schema enforcement failed", schema_problems)

        cells = adjudicate(matrix)
        holdout_report = None
        if holdout is not None:
            holdout_report = adjudicate_holdout(holdout, attempt_root, pins_raw_sha256)
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
            "holdout": holdout_report,
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
