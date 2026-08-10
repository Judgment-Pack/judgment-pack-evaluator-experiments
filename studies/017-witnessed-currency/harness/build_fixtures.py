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

    def config(names, minimum):
        return sighting.witnessconfig_bytes(
            series_id=SERIES_ID,
            witness_keys=[keys[name][2] for name in names],
            minimum_sightings=minimum,
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

    # ---- controls ----------------------------------------------------------
    cells["pos-consistent"] = cell(snap(view_a), config(["w2"], 1),
                                   [sight("w2", head_a2, 2)])
    cells["unchanged"] = dict(cells["pos-consistent"])

    forged = sight("w2", head_a2, 2)
    forged["signature"] = flip_character(forged["signature"])
    cells["neg-sighting-forged"] = cell(snap(view_a), config(["w2"], 1), [forged])

    cells["neg-unpinned-conflict"] = cell(snap(view_c), config(["w2"], 0),
                                          [sight("w3", head_a2, 2)])

    over_cap = [sight("w2", head_a2, 2)] * 65
    cells["neg-limits"] = cell(snap(view_a), config(["w2"], 1), over_cap)

    # ---- endpoints ---------------------------------------------------------
    cells["wit-split-view-caught"] = cell(snap(view_c), config(["w2"], 0),
                                          [sight("w2", head_a2, 2)])
    cells["wit-collusion-a"] = cell(snap(view_a), config(["w1"], 1),
                                    [sight("w1", head_a2, 2)])
    cells["wit-collusion-b"] = cell(snap(view_c), config(["w1"], 1),
                                    [sight("w1", head_c2, 2)])
    cells["wit-one-honest"] = cell(snap(view_c), config(["w1", "w2"], 1),
                                   [sight("w1", head_c2, 2), sight("w2", head_a2, 2)])
    cells["wit-partition-vacuous"] = cell(snap(view_c), config(["w2"], 0), [])
    cells["wit-partition-enforced"] = cell(snap(view_c), config(["w2"], 1), [])
    cells["wit-retention-horizon"] = cell(snap(view_c), config(["w2"], 1),
                                          [sight("w2", genesis, 1)])
    cells["wit-recency-behind"] = cell(snap(view_a, position=1), config(["w2"], 1),
                                       [sight("w2", head_a2, 2)])
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
