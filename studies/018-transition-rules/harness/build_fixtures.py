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


def build_payloads():
    """Every registered cell's payload, keyed by cell id."""
    ns = upstream016.load(build=True)
    registry = ns.checkpoint
    authority = registry.private_key("study-018/currency-authority/1")

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
