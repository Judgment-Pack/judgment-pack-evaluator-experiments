"""Generate `harness/STUDY-MANIFEST.sha256` — the whole-study exact-set manifest.

One line per covered file, `sha256  <study-relative path>`, sorted by path. The
covered set is exact and closed (`manifest_entries` below): the protocol
documents, both matrix strata, every adapter and harness source file —
including `owpflow.py`, where the build-time entropy algorithm lives, which
round 1 found was pinned in prose while sitting in unmanifested mutable code —
and every per-cell fixture manifest of the locked stratum. `score.py` verifies
this file before it adjudicates anything and a harness test verifies it too.

**Two deliberate exclusions, both required for the anchor to be initializable
and to survive a post-freeze holdout construction.**

1. `harness/PINS.json` is NOT covered. Round 2 built a cycle — the manifest
   hashed `PINS.json` while `PINS.json` stored the manifest's own digest — which
   would resist laundering but cannot be initialized without finding a SHA-256
   fixed point. Round 3 replaced it with a linear order:

       manifest  covers code + protocol + locked fixture manifests
       PINS      pins the manifest's digest (`studyManifest.sha256`)
       freeze    the freeze commit (and each attempt's `pinsSha256` stamp)
                 anchors `PINS.json` itself

   Nothing inside the manifest names the manifest, and nothing inside the
   manifest names `PINS.json`, so each link is fillable in one pass.

2. `fixtures/holdout/**` is NOT covered — and after round 4 that subtree does
   not exist at all. Holdout fixtures are constructed after the freeze, into the
   attempt that adjudicates them (`<attempt>/holdout-fixtures/<id>/`), never into
   a shared `fixtures/` subtree that a later run could rebuild under an earlier
   attempt's record. Attempt directories were never covered by this manifest, so
   the exclusion below is no longer load-bearing; it is kept as a **guard**, so
   that re-introducing a shared holdout tree cannot silently start invalidating
   the frozen exact set (or, worse, quietly enter it). Holdout integrity travels
   a different road entirely: the pinned `matrixHoldout.sha256` over the registry
   that specifies the cells, the per-cell `MANIFEST.sha256` and
   `CONSTRUCTION.json` written inside the attempt, and the digests of both
   stamped into that attempt's own record.

The manifest is regenerated during drafting and pinned at the freeze; after the
freeze a regeneration that changes a line is a deviation, not a fix.

Run: <venv>/bin/python harness/make_manifest.py [--check]
"""

import argparse
import hashlib
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
MANIFEST_PATH = STUDY / "harness" / "STUDY-MANIFEST.sha256"

REGISTERED_DOCUMENTS = (
    "PREREGISTRATION.md",
    "PREREG-REVIEW.md",
    "adapter/SPEC.md",
    "harness/MATRIX.json",
    "harness/MATRIX-HOLDOUT.json",
)

# Excluded from the covered set by construction, not by omission. Both are
# asserted by a harness test, so a future edit that quietly re-covers either one
# fails the suite rather than silently re-introducing the round-2 cycle. The
# fixture-root exclusion is a standing guard rather than a live case: no holdout
# fixture is written under `fixtures/` any more (round 4 — they are attempt-local).
EXCLUDED_DOCUMENTS = ("harness/PINS.json",)
EXCLUDED_FIXTURE_ROOTS = ("fixtures/holdout",)


def _is_excluded_fixture(relative):
    return any(
        relative == root or relative.startswith(root + "/")
        for root in EXCLUDED_FIXTURE_ROOTS
    )


def manifest_entries():
    """Every covered path, study-relative, sorted."""
    paths = [STUDY / name for name in REGISTERED_DOCUMENTS]
    paths.extend(sorted((STUDY / "adapter").glob("*.py")))
    paths.extend(sorted((STUDY / "harness").glob("*.py")))
    paths.extend(sorted((STUDY / "harness" / "tests").glob("*.py")))
    paths.extend(sorted((STUDY / "fixtures").rglob("MANIFEST.sha256")))
    seen = []
    for path in paths:
        relative = path.relative_to(STUDY).as_posix()
        if relative in EXCLUDED_DOCUMENTS or _is_excluded_fixture(relative):
            continue
        if relative not in seen:
            seen.append(relative)
    return sorted(seen)


def manifest_text():
    lines = []
    for relative in manifest_entries():
        path = STUDY / relative
        if not path.is_file():
            raise SystemExit("covered file is absent: " + relative)
        lines.append("%s  %s" % (hashlib.sha256(path.read_bytes()).hexdigest(), relative))
    return "\n".join(lines) + "\n"


def manifest_problems():
    """Exact-set comparison of the committed manifest against the tree."""
    if not MANIFEST_PATH.is_file():
        return ["study manifest is absent"]
    committed = {}
    for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, _, relative = line.partition("  ")
        committed[relative] = digest
    problems = []
    actual = {}
    for relative in manifest_entries():
        path = STUDY / relative
        actual[relative] = (
            hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        )
    for relative in sorted(set(committed) | set(actual)):
        if relative not in committed:
            problems.append("covered file is not in the study manifest: " + relative)
        elif relative not in actual:
            problems.append("study manifest lists an uncovered file: " + relative)
        elif actual[relative] is None:
            problems.append("study manifest lists an absent file: " + relative)
        elif actual[relative] != committed[relative]:
            problems.append("study manifest digest does not match: " + relative)
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    if arguments.check:
        problems = manifest_problems()
        for problem in problems:
            print(problem)
        return 1 if problems else 0
    MANIFEST_PATH.write_text(manifest_text(), encoding="utf-8")
    print("wrote %s (%d entries)" % (MANIFEST_PATH.name, len(manifest_entries())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
