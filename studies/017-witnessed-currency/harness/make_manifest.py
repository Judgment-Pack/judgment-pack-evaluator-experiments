"""The whole-study exact-set manifest (the 014/016 linear anchor, link 1).

Covers the protocol documents, both matrix strata, every registry/ and
harness/ source file, the harness tests, the upstream records, both vendored
pack fixtures, and every per-cell fixture manifest of the locked stratum. It
covers NEITHER itself NOR `harness/PINS.json` — the registry pins the
manifest's digest (`studyManifest.sha256`), and the freeze commit anchors the
registry, so after the freeze regenerating the manifest cannot rewrite the
digest it is pinned at.

Run: python harness/make_manifest.py [--check]
"""

import argparse
import hashlib
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
MANIFEST_PATH = STUDY / "harness" / "STUDY-MANIFEST.sha256"

DOCUMENTS = (
    "README.md",
    "PREREGISTRATION.md",
    "PREREG-REVIEW.md",
    "DEVIATIONS.md",
    "witness/SPEC.md",
    "harness/MATRIX.json",
    "harness/MATRIX-HOLDOUT.json",
    "harness/MATRIX-HOLDOUT-EVIDENCE.json",
)
GLOBS = (
    "witness/*.py",
    "harness/*.py",
    "harness/tests/*.py",
        "fixtures/cells/*/MANIFEST.sha256",
)
EXCLUDED = ("harness/PINS.json", "harness/STUDY-MANIFEST.sha256")


def covered_paths():
    paths = set()
    for relative in DOCUMENTS:
        if (STUDY / relative).is_file():
            paths.add(relative)
    for pattern in GLOBS:
        for path in STUDY.glob(pattern):
            if path.is_file():
                paths.add(path.relative_to(STUDY).as_posix())
    return sorted(paths - set(EXCLUDED))


def manifest_text():
    lines = []
    for relative in covered_paths():
        digest = hashlib.sha256((STUDY / relative).read_bytes()).hexdigest()
        lines.append("%s  %s" % (digest, relative))
    return "\n".join(lines) + "\n"


def verify_problems():
    """Exact-set verification: listed = covered, and every digest matches."""
    if not MANIFEST_PATH.is_file():
        return ["the study manifest is absent"]
    listed = {}
    for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, _, relative = line.partition("  ")
        listed[relative] = digest
    problems = []
    covered = covered_paths()
    for relative in covered:
        digest = hashlib.sha256((STUDY / relative).read_bytes()).hexdigest()
        if relative not in listed:
            problems.append("covered file is not listed: " + relative)
        elif listed[relative] != digest:
            problems.append("listed file does not match its digest: " + relative)
    for relative in sorted(set(listed) - set(covered)):
        problems.append("listed file is not covered on disk: " + relative)
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    if arguments.check:
        problems = verify_problems()
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1 if problems else 0
    MANIFEST_PATH.write_text(manifest_text(), encoding="utf-8")
    print("wrote %s (%d files)" % (MANIFEST_PATH.name, len(covered_paths())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
