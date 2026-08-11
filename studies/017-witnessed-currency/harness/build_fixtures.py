"""One-time deterministic fixture construction for every registered cell.

A Study 017 cell is `(commitment tuple, snapshot, trust configuration,
witness configuration, sightings)` — registry-and-witness only (design
decision D-1): no chains, no evaluator, no external component. Registry
views are built through Study 016's frozen `registry/checkpoint.py`,
consumed as a digest-pinned unmodified upstream; sightings through this
study's `witness/sighting.py`. Everything derives from fixed seeds and
constants; building twice yields byte-identical trees (a harness test
asserts it).

The fork pair V_A / V_C shares its genesis and diverges at position 2 with
BOTH branches keeping the committed version current — so the split-view
cells isolate the witness layer: Layer CURRENCY passes on either branch and
only the sighting comparison can tell them apart.

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
sys.path.insert(0, str(STUDY / "witness"))

import sighting  # noqa: E402
import upstream016  # noqa: E402

SERIES_ID = "https://example.com/judgment-packs/witnessed-policy"
OTHER_SERIES_ID = "https://example.com/judgment-packs/other-policy"
DIGEST_A = "sha256:" + hashlib.sha256(b"study-017/pack-1.0.0").hexdigest()
DIGEST_B = "sha256:" + hashlib.sha256(b"study-017/pack-1.1.0").hexdigest()
DIGEST_C = "sha256:" + hashlib.sha256(b"study-017/pack-2.0.0").hexdigest()

T1 = "2026-01-01T00:00:00Z"
T2 = "2026-01-15T00:00:00Z"
T3 = "2026-02-01T00:00:00Z"

CELL_FILES = (
    "commitment.json",
    "snapshot.json",
    "trustconfig.json",
    "witnessconfig.json",
    "sightings.json",
)
MANIFEST_NAME = "MANIFEST.sha256"


class BuildError(RuntimeError):
    """A cell could not be constructed as registered."""


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def commitment_bytes():
    return json.dumps(
        {"commitmentVersion": "1",
         "judgment": {"packId": SERIES_ID, "packVersion": "1.0.0",
                      "packDigest": DIGEST_A}},
        indent=2, ensure_ascii=False,
    ).encode("utf-8")


def event(kind, version, digest=None, effective=T1):
    entry = {"event": kind, "seriesId": SERIES_ID, "packVersion": version,
             "effectiveFrom": effective}
    if digest is not None:
        entry["packDigest"] = digest
    return entry


def flip_character(value):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    first = value[0]
    index = alphabet.index(first) if first in alphabet else 0
    return alphabet[(index + 1) % len(alphabet)] + value[1:]


def build_payloads():
    """Every registered cell's payload, keyed by cell id."""
    ns = upstream016.load(build=True)
    registry = ns.checkpoint
    authority = registry.private_key(sighting.AUTHORITY_SEED)
    w1 = registry.private_key(sighting.WITNESS_1_SEED)
    w2 = registry.private_key(sighting.WITNESS_2_SEED)
    w3 = registry.private_key(sighting.WITNESS_3_SEED)
    keys = {name: (key, registry.key_id(key), registry.public_key_b64(key))
            for name, key in (("w1", w1), ("w2", w2), ("w3", w3))}

    view_a = registry.build_registry(authority, [
        event("add", "1.0.0", DIGEST_A, T1), event("add", "1.1.0", DIGEST_B, T2),
    ])
    view_c = registry.build_registry(authority, [
        event("add", "1.0.0", DIGEST_A, T1), event("add", "2.0.0", DIGEST_C, T2),
    ])
    if view_a[0]["checkpointDigest"] != view_c[0]["checkpointDigest"]:
        raise BuildError("the fork views do not share their genesis")
    retired = registry.build_registry(authority, [
        event("add", "1.0.0", DIGEST_A, T1), event("add", "1.1.0", DIGEST_B, T2),
        event("retire", "1.0.0", effective=T3),
    ])
    genesis = view_a[0]["checkpointDigest"]
    head_a2 = view_a[1]["checkpointDigest"]
    head_c2 = view_c[1]["checkpointDigest"]
    head_r3 = retired[2]["checkpointDigest"]

    def snap(records, position=None):
        return registry.snapshot_bytes(
            registry.snapshot_of(authority, records, position=position)
        )

    trust = registry.trustconfig_bytes(
        series_id=SERIES_ID,
        authority_public_key=registry.public_key_b64(authority),
        genesis_head=genesis,
    )

    def sight(name, head, position):
        key, key_id, _ = keys[name]
        return sighting.build_sighting(
            key, key_id, series_id=SERIES_ID, head=head, position=position
        )

    def config(names, minimum, required=(), recency="ignore"):
        return sighting.witnessconfig_bytes(
            series_id=SERIES_ID,
            witness_keys=[keys[name][2] for name in names],
            minimum_sightings=minimum,
            required_witnesses=[keys[name][2] for name in required],
            recency_policy=recency,
        )

    def cell(snapshot, witnessconfig, records):
        return {
            "commitment.json": commitment_bytes(),
            "snapshot.json": snapshot,
            "trustconfig.json": trust,
            "witnessconfig.json": witnessconfig,
            "sightings.json": sighting.sightings_bytes(records),
        }

    cells = {}

    # ---- controls -----------------------------------------------------------
    cells["pos-consistent"] = cell(snap(view_a), config(["w2"], 1),
                                   [sight("w2", head_a2, 2)])
    cells["unchanged"] = dict(cells["pos-consistent"])

    malformed = sight("w2", head_a2, 2)
    malformed["sighting"]["position"] = 0
    cells["neg-sighting-malformed"] = cell(snap(view_a), config(["w2"], 1), [malformed])

    cells["neg-limits"] = cell(snap(view_a), config(["w2"], 1),
                               [sight("w2", head_a2, 2)] * 65)

    # The round-1 R1-4 construction, now a standing control: the honest
    # conflicting record carries a well-formed UNPINNED key-id label. Routing
    # by verification must still attribute and compare it.
    relabelled = sight("w2", head_a2, 2)
    relabelled["witnessKeyId"] = "ed25519:" + "0" * 64
    cells["neg-relabel-attack"] = cell(snap(view_c), config(["w2"], 0), [relabelled])

    # ---- endpoints: what a sighting buys ------------------------------------
    cells["wit-split-view-caught"] = cell(snap(view_c), config(["w2"], 0),
                                          [sight("w2", head_a2, 2)])
    cells["wit-collusion-a"] = cell(snap(view_a), config(["w1"], 1),
                                    [sight("w1", head_a2, 2)])
    cells["wit-collusion-b"] = cell(snap(view_c), config(["w1"], 1),
                                    [sight("w1", head_c2, 2)])
    cells["wit-one-honest"] = cell(snap(view_c), config(["w1", "w2"], 1),
                                   [sight("w1", head_c2, 2), sight("w2", head_a2, 2)])

    # ---- endpoints: what delivery control still hides ------------------------
    cells["wit-suppression-omitted"] = cell(snap(view_c), config(["w1", "w2"], 1),
                                            [sight("w1", head_c2, 2)])
    corrupted = sight("w2", head_a2, 2)
    corrupted["signature"] = flip_character(corrupted["signature"])
    cells["wit-suppression-corrupted"] = cell(
        snap(view_c), config(["w1", "w2"], 1),
        [sight("w1", head_c2, 2), corrupted])
    cells["wit-required-witness-absent"] = cell(
        snap(view_c), config(["w1", "w2"], 1, required=["w2"]),
        [sight("w1", head_c2, 2)])

    # ---- endpoints: enforcement and coverage --------------------------------
    cells["wit-zero-sightings-vacuous"] = cell(snap(view_c), config(["w2"], 0), [])
    cells["wit-zero-sightings-enforced"] = cell(snap(view_c), config(["w2"], 1), [])
    cells["wit-prefix-coverage"] = cell(snap(view_c), config(["w2"], 1),
                                        [sight("w2", genesis, 1)])

    # ---- endpoints: recency as configured policy (both arms) ----------------
    cells["wit-recency-refused"] = cell(
        snap(view_a, position=1), config(["w2"], 1, recency="refuse-behind"),
        [sight("w2", head_a2, 2)])
    cells["wit-historical-audit"] = cell(
        snap(view_a, position=1), config(["w2"], 1, recency="ignore"),
        [sight("w2", head_a2, 2)])

    # ---- layer composition ---------------------------------------------------
    cells["cur-retired-interplay"] = cell(snap(retired), config(["w2"], 1),
                                          [sight("w2", head_r3, 3)])

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
        if name in payload and payload[name] is not None:
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
    cells_root = out_root / "cells"
    if cells_root.exists():
        if not arguments.force:
            raise SystemExit("fixtures already exist; pass --force to rebuild")
        shutil.rmtree(cells_root)
    for cell_id, payload in sorted(build_payloads().items()):
        write_cell(cell_directory(out_root, cell_id), payload)
    print("built %d cells under %s" % (len(build_payloads()), out_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# --------------------------------------------------------------------------
# the reviewer-authored holdout stratum — implemented, NEVER run pre-freeze
# --------------------------------------------------------------------------
#
# Hooks for the round-2 reviewer's cells (harness/MATRIX-HOLDOUT.json,
# committed verbatim with attribution). Every route requires a
# `HoldoutAttemptContext` that only harness/score.py mints, after its freeze
# gates pass; each hook re-verifies the context itself, so no route can
# construct a byte while any freeze pin is null or outside a live attempt.
# There is deliberately no command-line route.

import dataclasses  # noqa: E402


@dataclasses.dataclass(frozen=True)
class HoldoutAttemptContext:
    attempt_root: str
    pins_raw_sha256: str
    preregistration_sha256: str
    matrix_holdout_sha256: str


class HoldoutRefused(RuntimeError):
    """The holdout route was driven without a valid post-freeze context."""


def holdout_context_problems(context):
    if not isinstance(context, HoldoutAttemptContext):
        return ["holdout construction requires a HoldoutAttemptContext"]
    problems = []
    pins_raw = (STUDY / "harness" / "PINS.json").read_bytes()
    if hashlib.sha256(pins_raw).hexdigest() != context.pins_raw_sha256:
        problems.append("context pins digest does not match the live registry")
    pins = json.loads(pins_raw.decode("utf-8"))
    for member in ("preregistration", "matrix", "matrixHoldout", "witnessSpec",
                   "studyManifest"):
        if (pins.get(member) or {}).get("sha256") is None:
            problems.append("freeze pin %s is null: the stratum executes only "
                            "after the freeze" % member)
    for attribute, relative in (("preregistration_sha256", "PREREGISTRATION.md"),
                                ("matrix_holdout_sha256", "harness/MATRIX-HOLDOUT.json")):
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


def _holdout_apparatus():
    ns = upstream016.load(build=True)
    registry = ns.checkpoint
    authority = registry.private_key(sighting.AUTHORITY_SEED)
    keys = {name: registry.private_key(seed) for name, seed in (
        ("w1", sighting.WITNESS_1_SEED), ("w2", sighting.WITNESS_2_SEED),
        ("w3", sighting.WITNESS_3_SEED))}
    view = lambda events: registry.build_registry(authority, events)
    a = view([event("add", "1.0.0", DIGEST_A, T1), event("add", "1.1.0", DIGEST_B, T2)])
    c = view([event("add", "1.0.0", DIGEST_A, T1), event("add", "2.0.0", DIGEST_C, T2)])
    a3 = view([event("add", "1.0.0", DIGEST_A, T1), event("add", "1.1.0", DIGEST_B, T2),
               event("add", "2.0.0", DIGEST_C, T3)])
    return registry, authority, keys, {"a": a, "c": c, "a3": a3}


def _holdout_cell(registry, authority, records, position, witness_records,
                  pinned, minimum, required=(), recency="ignore", keys=None):
    return {
        "commitment.json": commitment_bytes(),
        "snapshot.json": registry.snapshot_bytes(
            registry.snapshot_of(authority, records, position=position)),
        "trustconfig.json": registry.trustconfig_bytes(
            series_id=SERIES_ID,
            authority_public_key=registry.public_key_b64(authority),
            genesis_head=records[0]["checkpointDigest"]),
        "witnessconfig.json": sighting.witnessconfig_bytes(
            series_id=SERIES_ID,
            witness_keys=[registry.public_key_b64(keys[n]) for n in pinned],
            minimum_sightings=minimum,
            required_witnesses=[registry.public_key_b64(keys[n]) for n in required],
            recency_policy=recency),
        "sightings.json": sighting.sightings_bytes(witness_records),
    }


def _sight(registry, keys, name, head, position, series=SERIES_ID):
    key = keys[name]
    return sighting.build_sighting(key, registry.key_id(key), series_id=series,
                                   head=head, position=position)


def _holdout_h01(context):
    registry, authority, keys, views = _holdout_apparatus()
    a = views["a"]
    r1 = _sight(registry, keys, "w1", a[0]["checkpointDigest"], 1)
    r2 = _sight(registry, keys, "w2", a[1]["checkpointDigest"], 2)
    r1["witnessKeyId"], r2["witnessKeyId"] = r2["witnessKeyId"], r1["witnessKeyId"]
    return _holdout_cell(registry, authority, a, None, [r1, r2],
                         ["w1", "w2"], 2, ["w1", "w2"], keys=keys)


def _holdout_h02(context):
    registry, authority, keys, views = _holdout_apparatus()
    a, c = views["a"], views["c"]
    honest = _sight(registry, keys, "w1", c[1]["checkpointDigest"], 2)
    impostor = _sight(registry, keys, "w3", a[1]["checkpointDigest"], 2)
    impostor["witnessKeyId"] = registry.key_id(keys["w2"])
    return _holdout_cell(registry, authority, c, None, [honest, impostor],
                         ["w1", "w2"], 1, ["w2"], keys=keys)


def _holdout_h03(context):
    registry, authority, keys, views = _holdout_apparatus()
    a = views["a"]
    return _holdout_cell(registry, authority, a, None,
                         [_sight(registry, keys, "w1", a[0]["checkpointDigest"], 1),
                          _sight(registry, keys, "w2", a[1]["checkpointDigest"], 2)],
                         ["w1", "w2", "w3"], 3, ["w3"], keys=keys)


def _holdout_h04(context):
    registry, authority, keys, views = _holdout_apparatus()
    a = views["a"]
    return _holdout_cell(registry, authority, a, None,
                         [_sight(registry, keys, "w1", a[0]["checkpointDigest"], 1),
                          _sight(registry, keys, "w3", a[1]["checkpointDigest"], 2)],
                         ["w1", "w2", "w3"], 2, ["w2"], keys=keys)


def _holdout_h05(context, recency="ignore"):
    registry, authority, keys, views = _holdout_apparatus()
    a3 = views["a3"]
    return _holdout_cell(registry, authority, a3, 2,
                         [_sight(registry, keys, "w1", a3[1]["checkpointDigest"], 2),
                          _sight(registry, keys, "w2", a3[2]["checkpointDigest"], 3)],
                         ["w1", "w2"], 2, ["w1", "w2"], recency=recency, keys=keys)


def _holdout_h06(context):
    return _holdout_h05(context, recency="refuse-behind")


def _holdout_h07(context):
    registry, authority, keys, views = _holdout_apparatus()
    a, c, a3 = views["a"], views["c"], views["a3"]
    return _holdout_cell(registry, authority, a, 2,
                         [_sight(registry, keys, "w2", a3[2]["checkpointDigest"], 3),
                          _sight(registry, keys, "w1", c[1]["checkpointDigest"], 2)],
                         ["w1", "w2"], 2, ["w1", "w2"], recency="refuse-behind", keys=keys)


def _holdout_h08(context):
    registry, authority, keys, views = _holdout_apparatus()
    a = views["a"]
    payload = _holdout_cell(registry, authority, a, None,
                            [_sight(registry, keys, "w2", a[1]["checkpointDigest"], 2)],
                            ["w2"], 1, ["w2"], keys=keys)
    snapshot = json.loads(payload["snapshot.json"].decode("utf-8"))
    signature = snapshot["checkpoints"][1]["signature"]
    snapshot["checkpoints"][1]["signature"] = flip_character(signature)
    payload["snapshot.json"] = json.dumps(snapshot, indent=2,
                                          ensure_ascii=False).encode("utf-8")
    return payload


def _holdout_h09(context):
    registry, authority, keys, views = _holdout_apparatus()
    a = views["a"]
    return _holdout_cell(registry, authority, a, None,
                         [_sight(registry, keys, "w2", a[1]["checkpointDigest"], 2,
                                 series=OTHER_SERIES_ID)],
                         ["w2"], 0, keys=keys)


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
    "h09": _gated(_holdout_h09),
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
