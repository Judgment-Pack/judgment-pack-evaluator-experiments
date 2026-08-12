"""One-time deterministic fixture construction for every registered cell.

A Study 018 cell is `(commitment tuple, registry snapshot, trust configuration,
citation, rule configuration)` — registry-and-rule only (design decision D-1):
no receipt protocol, no evaluator binary, no external clone. Registry views are
built through Study 016's frozen `registry/checkpoint.py`, consumed as a
digest-pinned unmodified upstream; citations and rule configurations through
this study's `rule/citation.py`.

One history serves most of the matrix, so that cells differ in the rule and the
cited head rather than in the world:

    1 add 1.0.0   2 add 2.0.0   3 retire 1.0.0   4 retire 2.0.0   5 reinstate 2.0.0

Against it, the committed decision names `(1.0.0, digest-A)` — a version that
left the supported set at position 3 and never returned. The three registered
rules then disagree about the same evidence, deterministically, which is the
study's positive result and the concrete form of RFC 0011 §2a's separation.

Run: python harness/build_fixtures.py [--out DIR] [--force]
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDY / "harness"))
sys.path.insert(0, str(STUDY / "rule"))

import citation as citations  # noqa: E402
import upstream016  # noqa: E402

SERIES_ID = "https://example.com/judgment-packs/transition-policy"
OTHER_SERIES_ID = "https://example.com/judgment-packs/other-policy"
DIGEST_A = "sha256:" + hashlib.sha256(b"018/pack-1.0.0").hexdigest()
DIGEST_B = "sha256:" + hashlib.sha256(b"018/pack-2.0.0").hexdigest()

T1 = "2026-01-01T00:00:00Z"
T2 = "2026-01-15T00:00:00Z"
T3 = "2026-02-01T00:00:00Z"

CELL_FILES = ("commitment.json", "snapshot.json", "trustconfig.json",
              "citation.json", "ruleconfig.json")
MANIFEST_NAME = "MANIFEST.sha256"
PINS_PATH = STUDY / "harness" / "PINS.json"


class BuildError(RuntimeError):
    """A cell could not be constructed as registered."""


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def commitment_bytes(version="1.0.0", digest=DIGEST_A, series=SERIES_ID):
    return json.dumps(
        {"commitmentVersion": "1",
         "judgment": {"packId": series, "packVersion": version, "packDigest": digest}},
        indent=2, ensure_ascii=False,
    ).encode("utf-8")


def event(kind, version, digest=None, effective=T1, series=SERIES_ID):
    entry = {"event": kind, "seriesId": series, "packVersion": version,
             "effectiveFrom": effective}
    if digest is not None:
        entry["packDigest"] = digest
    return entry


def registered_authority_label():
    """The authority seed label as registered in harness/PINS.json."""
    pins = json.loads(Path(PINS_PATH).read_text(encoding="utf-8"))
    label = (pins.get("registryAuthority") or {}).get("authoritySeedLabel")
    if not isinstance(label, str) or not label:
        raise BuildError("registryAuthority.authoritySeedLabel is not registered")
    return label


def build_payloads():
    """Every registered cell's payload, keyed by cell id."""
    ns = upstream016.load(build=True)
    registry = ns.checkpoint
    # Round-1 R1-13: derived from the registered label, never hard-coded, so
    # the pin binds the fixtures instead of merely describing them.
    authority = registry.private_key(registered_authority_label())

    history = registry.build_registry(authority, [
        event("add", "1.0.0", DIGEST_A, T1),
        event("add", "2.0.0", DIGEST_B, T2),
        event("retire", "1.0.0", effective=T3),
        event("retire", "2.0.0", effective=T3),
        event("reinstate", "2.0.0", effective=T3),
    ])
    heads = [record["checkpointDigest"] for record in history]
    if len(heads) != 5:
        raise BuildError("the registered history is not five events")

    def snap(position=None):
        return registry.snapshot_bytes(
            registry.snapshot_of(authority, history, position=position))

    trust = registry.trustconfig_bytes(
        series_id=SERIES_ID,
        authority_public_key=registry.public_key_b64(authority),
        genesis_head=heads[0])

    cite = lambda position, series=SERIES_ID: citations.citation_bytes(
        series_id=series, cited_head=heads[position - 1])

    def cell(rule, *, position=None, cited=2, window=None, duration=None,
             commitment=None, citation=None, trustconfig=None, series=SERIES_ID):
        return {
            "commitment.json": commitment or commitment_bytes(),
            "snapshot.json": snap(position),
            "trustconfig.json": trustconfig or trust,
            "citation.json": citation if citation is not None else (
                cite(cited) if cited else None),
            "ruleconfig.json": citations.ruleconfig_bytes(
                series_id=series, rule=rule, window_positions=window,
                window_duration=duration),
        }

    cells = {}

    # ---- controls -----------------------------------------------------------
    # The version is still current at position 2: every rule must permit it.
    cells["pos-current-stop"] = cell("stop-at-retirement", position=2, cited=None)
    cells["pos-current-window"] = cell("position-window", position=2, cited=2, window=1)
    cells["pos-current-grandfather"] = cell("grandfather-on-cited-support", position=2, cited=2)
    cells["unchanged"] = dict(cells["pos-current-stop"])
    cells["neg-ruleconfig-malformed"] = cell("grandfather-on-cited-support", cited=2)
    cells["neg-ruleconfig-malformed"]["ruleconfig.json"] = (
        citations.ruleconfig_bytes(series_id=SERIES_ID, rule="grandfather-on-cited-support")
        .replace(b'"rule": "grandfather-on-cited-support"', b'"rule": "invent-a-rule"'))

    # ---- the divergence: identical evidence, three rules ---------------------
    cells["div-stop-at-retirement"] = cell("stop-at-retirement", cited=2)
    cells["div-position-window-open"] = cell("position-window", cited=2, window=5)
    cells["div-position-window-elapsed"] = cell("position-window", cited=2, window=1)
    cells["div-grandfather-on-cited-support"] = cell("grandfather-on-cited-support", cited=2)

    # ---- what the citation is worth, per rule -------------------------------
    cells["cite-absent-stop-unaffected"] = cell("stop-at-retirement", cited=None)
    cells["cite-absent-grandfather-unavailable"] = cell("grandfather-on-cited-support", cited=None)
    cells["cite-unsupported-grandfather"] = cell("grandfather-on-cited-support", cited=4)
    cells["cite-unsupported-window"] = cell("position-window", cited=4, window=5)
    cells["cite-foreign-history"] = cell("grandfather-on-cited-support", cited=2)
    cells["cite-foreign-history"]["citation.json"] = citations.citation_bytes(
        series_id=SERIES_ID,
        cited_head="sha256:" + hashlib.sha256(b"018/not-in-this-history").hexdigest())

    # ---- registered boundaries ----------------------------------------------
    # The backdated citation: an author who chooses what to cite cites early.
    cells["bnd-backdated-citation"] = cell("grandfather-on-cited-support", cited=2)
    # A duration window: no trusted ordering exists offline.
    cells["bnd-duration-window"] = cell("position-window", cited=2, duration="24h")
    # Mint-time refusal is a producer policy, exhibited as a rule that would
    # have refused at the head the producer saw.
    cells["bnd-mint-time-refusal"] = dict(cells["cite-absent-stop-unaffected"])
    # Round-1 R1-1's control: an unauthenticated snapshot must never reach a rule.
    import json as _json
    broken = _json.loads(snap(None).decode("utf-8"))
    signature = broken["checkpoints"][1]["signature"]
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    first = signature[0]
    index = alphabet.index(first) if first in alphabet else 0
    broken["checkpoints"][1]["signature"] = alphabet[(index + 1) % len(alphabet)] + signature[1:]
    cells["neg-currency-unauthenticated"] = cell("grandfather-on-cited-support", cited=2)
    cells["neg-currency-unauthenticated"]["snapshot.json"] = _json.dumps(
        broken, indent=2, ensure_ascii=False).encode("utf-8")

    # Round-2 R2-1's controls: a digest the registry never bound did not depart.
    never_bound = commitment_bytes(digest="sha256:" + "b" * 64)
    cells["neg-never-supported-digest"] = cell("stop-at-retirement", cited=None,
                                               commitment=never_bound)
    cells["neg-never-supported-window"] = cell("position-window", cited=2, window=5,
                                               commitment=never_bound)
    # Round-4 blocker 1: both cells above name a version the registry DID bind,
    # at a digest it did not. The unknown-version case is a different path
    # through the pinned fold — `supported.get(version)` is absent rather than
    # mismatched — and had no vector at all until now.
    cells["neg-never-supported-version"] = cell(
        "grandfather-on-cited-support", cited=2,
        commitment=commitment_bytes(version="9.9.9"))

    # A rule stated for another series confers nothing here.
    cells["bnd-foreign-series-rule"] = cell("grandfather-on-cited-support", cited=2,
                                            series=OTHER_SERIES_ID)
    cells["bnd-foreign-series-rule"]["commitment.json"] = commitment_bytes()
    cells["bnd-foreign-series-rule"]["citation.json"] = cite(2)

    return cells


def manifest_text(directory):
    directory = Path(directory)
    lines = []
    for name in sorted(CELL_FILES):
        path = directory / name
        if path.is_file():
            lines.append("%s  %s" % (sha256_hex(path.read_bytes()), name))
    return "\n".join(lines) + "\n"


def _atomic_write(path, payload):
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


def write_cell(directory, payload):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for name in CELL_FILES:
        target = directory / name
        if payload.get(name) is not None:
            _atomic_write(target, payload[name])
        elif target.is_file():
            target.unlink()
    _atomic_write(directory / MANIFEST_NAME, manifest_text(directory).encode("utf-8"))


def cell_directory(out_root, cell_id):
    return Path(out_root) / "cells" / cell_id


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default=str(STUDY / "fixtures"))
    parser.add_argument("--force", action="store_true")
    arguments = parser.parse_args(argv)
    out_root = Path(arguments.out)
    if (out_root / "cells").exists():
        if not arguments.force:
            raise SystemExit("fixtures already exist; pass --force to rebuild")
        shutil.rmtree(out_root / "cells")
    payloads = build_payloads()
    for cell_id, payload in sorted(payloads.items()):
        write_cell(cell_directory(out_root, cell_id), payload)
    print("built %d cells under %s" % (len(payloads), out_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# --------------------------------------------------------------------------
# the reviewer-authored holdout stratum — implemented, NEVER run pre-freeze
# --------------------------------------------------------------------------
#
# Hooks for the round-2 reviewer's cells (harness/MATRIX-HOLDOUT.json,
# committed verbatim with attribution; their structured expectations live in
# harness/MATRIX-HOLDOUT-EVIDENCE.json so that block stays byte-for-byte).
# Every route requires a `HoldoutAttemptContext` that only harness/score.py
# mints after its freeze gates pass, and each hook re-verifies it, so no route
# can construct a byte while any freeze pin is null or outside a live attempt.

import dataclasses  # noqa: E402

NEVER_BOUND_DIGEST = "sha256:" + hashlib.sha256(
    b"018/round-2-holdout-never-bound").hexdigest()
BASE64_ALPHABET = ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
                   "0123456789+/")


@dataclasses.dataclass(frozen=True)
class HoldoutAttemptContext:
    attempt_root: str
    pins_raw_sha256: str
    preregistration_sha256: str
    matrix_holdout_sha256: str
    matrix_holdout_evidence_sha256: str


class HoldoutRefused(RuntimeError):
    """The holdout route was driven without a valid post-freeze context."""


def holdout_context_problems(context):
    if not isinstance(context, HoldoutAttemptContext):
        return ["holdout construction requires a HoldoutAttemptContext"]
    problems = []
    pins_raw = Path(PINS_PATH).read_bytes()
    if hashlib.sha256(pins_raw).hexdigest() != context.pins_raw_sha256:
        problems.append("context pins digest does not match the live registry")
    pins = json.loads(pins_raw.decode("utf-8"))
    for member in ("preregistration", "matrix", "matrixHoldout",
                   "matrixHoldoutEvidence", "ruleSpec", "studyManifest"):
        if (pins.get(member) or {}).get("sha256") is None:
            problems.append("freeze pin %s is null: the stratum executes only "
                            "after the freeze" % member)
    for attribute, relative in (
            ("preregistration_sha256", "PREREGISTRATION.md"),
            ("matrix_holdout_sha256", "harness/MATRIX-HOLDOUT.json"),
            ("matrix_holdout_evidence_sha256", "harness/MATRIX-HOLDOUT-EVIDENCE.json")):
        live = hashlib.sha256((STUDY / relative).read_bytes()).hexdigest()
        if getattr(context, attribute) != live:
            problems.append("context %s does not match the live file" % attribute)
    if not Path(context.attempt_root).is_dir():
        problems.append("context attempt root does not exist")
    return problems


def _require_context(context):
    problems = holdout_context_problems(context)
    if problems:
        raise HoldoutRefused("; ".join(problems))


def _authority(context):
    """Innermost holdout primitive: no key is derived without a valid context.

    Round-3 blocker 5: `_gated` wrapped only the HOLDOUT_HOOKS mapping, so an
    importer could call `_holdout_h01(None)` and construct real registry bytes
    before the freeze. Validation now sits below every route, before any key or
    payload exists, and the wrapper is defence in depth rather than the gate.
    """
    _require_context(context)
    ns = upstream016.load(build=True)
    registry = ns.checkpoint
    pins = json.loads(Path(PINS_PATH).read_text(encoding="utf-8"))
    label = (pins.get("registryAuthority") or {}).get("authoritySeedLabel")
    return registry, registry.private_key(label)


def _holdout_cell(context, registry, authority, events, *, commitment, rule,
                  cited=None, window=None, duration=None,
                  citation_series=SERIES_ID, rule_series=SERIES_ID):
    _require_context(context)
    history = registry.build_registry(authority, events)
    heads = [record["checkpointDigest"] for record in history]
    payload = {
        "commitment.json": commitment,
        "snapshot.json": registry.snapshot_bytes(
            registry.snapshot_of(authority, history)),
        "trustconfig.json": registry.trustconfig_bytes(
            series_id=SERIES_ID,
            authority_public_key=registry.public_key_b64(authority),
            genesis_head=heads[0]),
        "citation.json": None if cited is None else citations.citation_bytes(
            series_id=citation_series, cited_head=heads[cited - 1]),
        "ruleconfig.json": citations.ruleconfig_bytes(
            series_id=rule_series, rule=rule, window_positions=window,
            window_duration=duration),
    }
    return payload, heads


def _h01_events():
    return [event("add", "4.0.0", DIGEST_A), event("add", "9.0.0", DIGEST_B),
            event("retire", "4.0.0"), event("reinstate", "4.0.0"),
            event("retire", "4.0.0"), event("add", "10.0.0", DIGEST_B),
            event("reinstate", "4.0.0")]


def _h04_events():
    return [event("add", "7.0.0", DIGEST_A), event("retire", "7.0.0"),
            event("add", "20.0.0", DIGEST_B), event("reinstate", "7.0.0"),
            event("retire", "7.0.0"), event("reinstate", "7.0.0"),
            event("add", "21.0.0", DIGEST_B), event("retire", "7.0.0"),
            event("add", "22.0.0", DIGEST_B), event("add", "23.0.0", DIGEST_B),
            event("add", "24.0.0", DIGEST_B)]


def _holdout_h01(context):
    _require_context(context)
    registry, authority = _authority(context)
    payload, _ = _holdout_cell(context, registry, authority, _h01_events(),
                               commitment=commitment_bytes("4.0.0", DIGEST_A),
                               rule="stop-at-retirement")
    return payload


def _holdout_h02(context):
    _require_context(context)
    payload = _holdout_h01(context)
    snapshot = json.loads(payload["snapshot.json"].decode("utf-8"))
    signature = snapshot["attestation"]["signature"]
    index = BASE64_ALPHABET.index(signature[0]) if signature[0] in BASE64_ALPHABET else 0
    snapshot["attestation"]["signature"] = (
        BASE64_ALPHABET[(index + 1) % len(BASE64_ALPHABET)] + signature[1:])
    payload["snapshot.json"] = json.dumps(snapshot, indent=2,
                                          ensure_ascii=False).encode("utf-8")
    return payload


def _holdout_h03(context):
    _require_context(context)
    registry, authority = _authority(context)
    payload, _ = _holdout_cell(
        context, registry, authority, _h01_events(),
        commitment=commitment_bytes("4.0.0", NEVER_BOUND_DIGEST),
        rule="position-window", cited=4, window=10)
    return payload


def _holdout_h04(context, cited=6, rule="grandfather-on-cited-support", window=None):
    _require_context(context)
    registry, authority = _authority(context)
    payload, _ = _holdout_cell(context, registry, authority, _h04_events(),
                               commitment=commitment_bytes("7.0.0", DIGEST_A),
                               rule=rule, cited=cited, window=window)
    return payload


def _holdout_h05(context):
    _require_context(context)
    return _holdout_h04(context, cited=5)


def _holdout_h06(context):
    _require_context(context)
    return _holdout_h04(context, cited=6, rule="position-window", window=3)


def _holdout_h07(context):
    _require_context(context)
    return _holdout_h04(context, cited=6, rule="position-window", window=2)


def _holdout_h08(context):
    _require_context(context)
    registry, authority = _authority(context)
    events = [event("add", "20.0.0", DIGEST_B),
              event("add", "7.0.0", DIGEST_A, series=OTHER_SERIES_ID),
              event("retire", "7.0.0", series=OTHER_SERIES_ID),
              event("add", "7.0.0", DIGEST_A),
              event("reinstate", "7.0.0", series=OTHER_SERIES_ID),
              event("retire", "7.0.0")]
    payload, _ = _holdout_cell(context, registry, authority, events,
                               commitment=commitment_bytes("7.0.0", DIGEST_A),
                               rule="grandfather-on-cited-support", cited=2)
    return payload


def _holdout_h09(context):
    _require_context(context)
    registry, authority = _authority(context)
    events = [event("add", "7.0.0", DIGEST_A, series=OTHER_SERIES_ID),
              event("retire", "7.0.0", series=OTHER_SERIES_ID),
              event("reinstate", "7.0.0", series=OTHER_SERIES_ID)]
    payload, _ = _holdout_cell(context, registry, authority, events,
                               commitment=commitment_bytes("7.0.0", DIGEST_A),
                               rule="stop-at-retirement")
    return payload


def _holdout_h10(context):
    _require_context(context)
    registry, authority = _authority(context)
    events = [event("add", "20.0.0", DIGEST_B), event("add", "7.0.0", DIGEST_A),
              event("add", "7.0.0", DIGEST_A, series=OTHER_SERIES_ID)]
    payload, _ = _holdout_cell(context, registry, authority, events,
                               commitment=commitment_bytes("7.0.0", DIGEST_A),
                               rule="grandfather-on-cited-support", cited=3,
                               citation_series=OTHER_SERIES_ID)
    return payload


def _gated(hook):
    def gated_hook(context):
        _require_context(context)
        return hook(context)
    gated_hook.__name__ = hook.__name__
    return gated_hook


HOLDOUT_HOOKS = {
    "h01": _gated(_holdout_h01), "h02": _gated(_holdout_h02),
    "h03": _gated(_holdout_h03), "h04": _gated(_holdout_h04),
    "h05": _gated(_holdout_h05), "h06": _gated(_holdout_h06),
    "h07": _gated(_holdout_h07), "h08": _gated(_holdout_h08),
    "h09": _gated(_holdout_h09), "h10": _gated(_holdout_h10),
}


def builder_version_digest():
    return sha256_hex(Path(__file__).read_bytes())


def construct_holdout(context, out_root, cells):
    """Build every registered holdout cell inside the attempt. Scorer-only."""
    _require_context(context)
    out_root = Path(out_root)
    if Path(context.attempt_root).resolve() not in out_root.resolve().parents:
        raise HoldoutRefused("holdout output must live inside the context's attempt")
    records = {}
    for cell in cells:
        cell_id = cell["id"]
        directory = out_root / cell_id
        record = {"cell": cell_id, "builderVersionDigest": builder_version_digest()}
        hook = HOLDOUT_HOOKS.get(cell_id)
        try:
            if hook is None:
                raise BuildError("no construction hook is registered for " + cell_id)
            write_cell(directory, hook(context))
            record["status"] = "built"
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as error:
            record["status"] = "harness-error"
            record["harnessError"] = "%s: %s" % (type(error).__name__, error)
        directory.mkdir(parents=True, exist_ok=True)
        _atomic_write(directory / "CONSTRUCTION.json",
                      (json.dumps(record, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
        records[cell_id] = record
    return records
