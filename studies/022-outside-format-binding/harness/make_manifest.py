"""The whole-study exact-set manifest: the registration, the review record, the matrices, the
adapter specification and code, the harness and its tests, and the baseline fixture. It covers
NEITHER itself NOR harness/PINS.json (the pins hold this manifest's digest; the freeze commit
anchors the pins) NOR README.md and DEVIATIONS.md, which are written after the freeze by design.

Run: python harness/make_manifest.py [--check]
"""
import argparse
import hashlib
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
MANIFEST_PATH = STUDY / "harness" / "STUDY-MANIFEST.sha256"
DOCUMENTS = ("PREREGISTRATION.md", "PREREG-REVIEW.md", "adapter/SPEC.md", "harness/MATRIX.json", "harness/MATRIX-HOLDOUT.json")
GLOBS = ("adapter/**/*", "harness/**/*", "fixtures/baseline/**/*")
ALLOWED_DIRS = ("adapter", "harness", "harness/tests", "fixtures", "fixtures/baseline")  # plus everything under fixtures/baseline
EXCLUDED = ("harness/PINS.json", "harness/STUDY-MANIFEST.sha256", "README.md", "DEVIATIONS.md")


def covered_paths():
    paths = set()
    for relative in DOCUMENTS:
        if (STUDY / relative).is_file():
            paths.add(relative)
    for pattern in GLOBS:
        for p in STUDY.glob(pattern):
            rel = p.relative_to(STUDY).as_posix()
            if "__pycache__" in rel or rel.endswith(".pyc"):
                continue
            if p.is_dir():
                # a directory under adapter/ or harness/ that is not the tests directory could shadow a pinned package on the import path
                if not (rel in ALLOWED_DIRS or rel.startswith("fixtures/baseline/")):
                    raise SystemExit("refusing: unexpected directory %s under the harness roots" % rel)
                continue
            if p.is_symlink():
                raise SystemExit("refusing: symbolic link %s" % rel)
            paths.add(rel)
    return sorted(p for p in paths if p not in EXCLUDED)


def render():
    return "".join("%s  %s\n" % (hashlib.sha256((STUDY / r).read_bytes()).hexdigest(), r) for r in covered_paths())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    text = render()
    if args.check:
        if (MANIFEST_PATH.read_text() if MANIFEST_PATH.exists() else "") != text:
            sys.exit("STUDY-MANIFEST.sha256 does not match the tree")
        print("manifest matches (%d files)" % len(text.splitlines()))
        return
    MANIFEST_PATH.write_text(text)
    print("wrote %s (%d files)" % (MANIFEST_PATH, len(text.splitlines())))


if __name__ == "__main__":
    main()
