"""Generate `harness/STUDY-MANIFEST.sha256` — the whole-study exact-set manifest.

One line per covered file, `sha256  <study-relative path>`, sorted by path. The covered
set is exact and closed (`manifest_entries` below): every top-level protocol document, the
pin registry, both matrix strata, every adapter and harness source file, every probe source
(the node side is study apparatus exactly as the Python side is), the vendored fixture
inputs (the pack and the conformance seed cases), and every per-cell fixture manifest.
`score.py` verifies this file before it adjudicates anything and a harness test verifies
it too.

What it deliberately does **not** cover is `DEVIATIONS.md` and `README.md`
(`EXCLUDED_DOCUMENTS`, ADR 0004): the appendable files, which must stay editable after the
freeze precisely so a correction has somewhere to land. They are candidates like every
other top-level `.md` and are removed by the filter, so the exclusion is a decision the
code makes rather than an accident of which globs were written.

The manifest is regenerated during drafting and pinned at the freeze; after the freeze a
regeneration that changes a line is a deviation, not a fix.

Run: <venv>/bin/python harness/make_manifest.py [--check]
"""

import argparse
import hashlib
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
    "harness/requirements.txt",
    "fixtures/data-request-intake-triage.pack.json",
    "fixtures/conformance-cases.json",
)

# Out of the covered set BY CONSTRUCTION, not by omission (ADR 0004). The manifest covers
# what must not change, and a file whose whole purpose is to be appended to after the
# freeze is not that: `DEVIATIONS.md` is the only place a post-freeze correction may land,
# so covering it would mean the first genuine deviation broke the anchor the deviation
# exists to protect. `README.md` is navigation and carries a status banner that must be
# able to go from "nothing has run" to a result.
#
# Round 6 (R6-7) found this safeguard tautological as first written: no candidate glob
# reached a top-level `.md` at all, so the filter below never met either name and deleting
# the constant produced the identical manifest. The candidate population now includes
# every top-level `*.md` — so a new protocol document is covered the moment it is written,
# and these two are covered by nothing because the filter removes them. A harness test
# disables the constant and asserts both files enter the manifest, which is the assertion
# the old test claimed and could not make.
EXCLUDED_DOCUMENTS = ("DEVIATIONS.md", "README.md")


def manifest_entries():
    """Every covered path, study-relative, sorted."""
    paths = [STUDY / name for name in REGISTERED_DOCUMENTS]
    paths.extend(sorted(STUDY.glob("*.md")))
    paths.extend(sorted((STUDY / "adapter").glob("*.py")))
    paths.extend(sorted((STUDY / "harness").glob("*.py")))
    paths.extend(sorted((STUDY / "harness" / "tests").glob("*.py")))
    paths.extend(sorted((STUDY / "probes").glob("*.ts")))
    paths.extend(sorted((STUDY / "probes" / "stubs").glob("*.ts")))
    paths.extend(sorted((STUDY / "fixtures").rglob("MANIFEST.sha256")))
    seen = []
    for path in paths:
        relative = path.relative_to(STUDY).as_posix()
        if relative in EXCLUDED_DOCUMENTS:
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
