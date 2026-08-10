"""Generate `harness/STUDY-MANIFEST.sha256` — the whole-study exact-set manifest.

One line per covered file, `sha256  <study-relative path>`, sorted by path. The
covered set is exact and closed (`manifest_entries` below): the protocol
documents, the pin registry, both matrix strata, every adapter and harness
source file — including `owpflow.py`, where the build-time entropy algorithm
lives, which round 1 found was pinned in prose while sitting in unmanifested
mutable code — and every per-cell fixture manifest. `score.py` verifies this
file before it adjudicates anything and a harness test verifies it too.

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
    "harness/PINS.json",
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
