"""The whole-study exact-set manifest (the 014/016 linear anchor, link 1).

Covers the preregistration, the review record, the registered matrices, the
vendored policies and their manifest, and every harness source file. It
covers NEITHER itself NOR harness/PINS.json (the pins hold this manifest's
digest; the freeze commit anchors the pins) NOR README.md and DEVIATIONS.md,
which are written after the freeze by design (tools/check_freeze_sets.py).

Run: python harness/make_manifest.py [--check]
"""
import argparse
import hashlib
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
MANIFEST_PATH = STUDY / "harness" / "STUDY-MANIFEST.sha256"
DOCUMENTS = ("PREREGISTRATION.md", "PREREG-REVIEW.md", "harness/MATRIX.json", "harness/MATRIX-HOLDOUT.json",
             "fixtures/policies/MANIFEST.sha256")
GLOBS = ("harness/*.py", "harness/tests/*.py", "fixtures/policies/*.json")
EXCLUDED = ("harness/PINS.json", "harness/STUDY-MANIFEST.sha256", "README.md", "DEVIATIONS.md")


def covered_paths():
    paths = set()
    for relative in DOCUMENTS:
        if (STUDY / relative).is_file():
            paths.add(relative)
    for pattern in GLOBS:
        for p in STUDY.glob(pattern):
            if p.is_file():
                paths.add(p.relative_to(STUDY).as_posix())
    return sorted(p for p in paths if p not in EXCLUDED)


def render():
    lines = []
    for relative in covered_paths():
        digest = hashlib.sha256((STUDY / relative).read_bytes()).hexdigest()
        lines.append("%s  %s" % (digest, relative))
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    text = render()
    if args.check:
        current = MANIFEST_PATH.read_text() if MANIFEST_PATH.exists() else ""
        if current != text:
            sys.exit("STUDY-MANIFEST.sha256 does not match the tree")
        print("manifest matches (%d files)" % len(text.splitlines()))
        return
    MANIFEST_PATH.write_text(text)
    print("wrote %s (%d files)" % (MANIFEST_PATH, len(text.splitlines())))


if __name__ == "__main__":
    main()
