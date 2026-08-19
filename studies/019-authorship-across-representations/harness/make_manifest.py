"""Generate `harness/STUDY-MANIFEST.sha256` — the whole-study exact-set manifest.

PORTED from Study 014's `harness/make_manifest.py`
(sha256 `660a350ad8a647a2df9fea443af273c8c20480bd276c5a74336e345a86cadb81`, at
commit `019c95be9e86c575878015954dfec17e4f84e683` — Study 014 pins none of its
own harness sources, so that commit is the whole of this row's source-side
binding; `harness/PORTS.md` records it and `harness/integrity.py` binds it).

One line per covered file, `sha256  <study-relative path>`, sorted by path. The
covered set is exact and closed (`manifest_entries` below): the registered
documents, the frozen policy prose and gold suite, the mutant manifests and
reference implementations, and every harness source — including `harness/e4lib/`,
the scorer's own modules, and including the tests, because a harness test that
can be edited after the freeze is not a guard.
`harness/score.py` will verify this file before it adjudicates anything, and a
harness test verifies it too.

**Four exclusions, each by construction and each asserted by a harness test.**
Every one carries its REASON in `EXCLUDED_DOCUMENTS` itself, so a future reader
deciding whether to re-cover a path reads why it is out rather than guessing.

1. `DEVIATIONS.md` and `README.md` — **ADR 0004**. A file whose purpose is to be
   appended to after the freeze is not a file that must not change: covering
   `DEVIATIONS.md` means the first genuine deviation breaks the anchor the
   deviation exists to protect, and covering `README.md` freezes the status
   banner at whatever it said before the attempt ran. Studies 016–018 covered
   both and never exercised either; 014 and 015 excluded them and are the two
   that needed the mechanism. `harness/tests/test_manifest.py` asserts both
   exclusions hold **while both files exist**, so a future widening fails the
   suite rather than passing quietly and taking the deviation mechanism with it.
2. `PREREG-REVIEW.md` — **ADR 0004 again, ROUND-3 FINDING R3-1.** The review
   record is the SAME SHAPE of file and it was covered anyway: it grows by one
   disposition table per review round, and every round therefore had to
   regenerate the manifest after writing its dispositions or leave the committed
   manifest describing a tree that no longer exists. It went stale that way three
   rounds running — between rounds 1 and 2, again between 2 and 3, and again in
   the round-2 response, which reported a green suite while three enforcement
   tests were red. Round 2's answer was a procedure ("regenerate LAST") and a
   second failing test; a procedure that must be remembered every round is not a
   safeguard, and the third recurrence is the evidence. ADR 0004's own decision
   is the fix: the pre-freeze review record is appendable BY DESIGN, so it leaves
   the covered set by named constant. Nothing is lost — `PREREG-REVIEW.md`
   carries no claim any published number rests on, and the artifacts that do are
   still covered file by file.
3. `harness/PINS.json` — Study 014's round-3 lesson, carried unchanged. The
   manifest must not cover the registry that pins the manifest: that is a cycle
   which cannot be initialized without finding a SHA-256 fixed point. The
   anchor order is LINEAR:

       manifest  covers the registered documents, the artifacts and the code
       PINS      pins the manifest's digest (`studyManifest.sha256`)
       freeze    the freeze commit anchors `PINS.json` itself

**Pending documents.** This study is pre-freeze and several registered
documents do not exist yet (the frozen policy prose, the review record, the
gold suite, the mutant manifests). They are named in `REGISTERED_DOCUMENTS`
anyway, because the registered set is what the freeze must cover and a set
discovered by globbing at freeze time is not a registered set.
`pending_documents()` reports the absent ones, `manifest_entries()` skips them
while they are absent, and `--freeze` REFUSES while any is pending — which is
the freeze-fill procedure's own gate rather than an operator's memory.

Run: <the pinned interpreter> harness/make_manifest.py [--check | --freeze]
"""

import argparse
import hashlib
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
MANIFEST_PATH = STUDY / "harness" / "STUDY-MANIFEST.sha256"

REGISTERED_DOCUMENTS = (
    "PREREGISTRATION.md",
    # `PREREG-REVIEW.md` is NOT here — round-3 R3-1, module head point 2. It is
    # an appendable file and lives in `EXCLUDED_DOCUMENTS` with its reason.
    "policy/POLICY.md",
    "gold/GOLD.json",
    "mutants/MANIFEST-jps.json",
    "mutants/MANIFEST-rego.json",
    "reference/REFERENCE-A.md",
    "reference/REFERENCE-B.md",
    # ROUND-1 FINDING R1-9. The manifest covered the two top-level mutant
    # manifests and the reference PROSE, and none of the bytes the scorer
    # actually executes. These three are executable/control payloads that decide
    # published rates, so they are registered documents like any other and
    # `--freeze` refuses while any is absent.
    "reference/refA/pack.json",
    "reference/refB/policy.rego",
    "controls/off-gold-equivalence.json",
    "harness/PORTS.md",
)

# The registered payload SETS, each an exact one-level glob. Same finding: every
# scorer input carries a per-file hash, so a single mutant payload edited after
# the freeze fails the exact-set comparison rather than being covered only by a
# manifest that names its directory.
#
# `mutants/jps` and `mutants/rego` are the mutant payloads `e4lib/e4.py` loads by
# path out of the two MANIFESTs; `controls/reviewer-mutants` is the sealed set
# `e4lib/reviewer.py` executes at the attempt (round-1 R1-10), whose bytes are
# committed verbatim during the review rounds and must not move afterwards.
# A directory that does not exist yet contributes nothing and is not fabricated;
# once it exists, the glob is exact and an added file is as loud as a deleted one.
REGISTERED_PAYLOAD_SETS = (
    ("mutants/jps", "*.json"),
    ("mutants/rego", "*.rego"),
    ("controls/reviewer-mutants", "*.json"),
    ("controls/reviewer-mutants", "*.rego"),
)

# Excluded from the covered set by construction, not by omission — a MAPPING
# rather than a bare tuple, because ADR 0004 asks for a named constant and a
# name without its reason is the thing a later widening argues past. All four
# are asserted by a harness test (`harness/tests/test_manifest.py`).
EXCLUDED_DOCUMENTS = {
    "DEVIATIONS.md":
        "ADR 0004: appendable by design. Post-freeze corrections go here, so "
        "covering it means the first genuine deviation breaks the anchor the "
        "deviation exists to protect.",
    "README.md":
        "ADR 0004: appendable by design. The status banner must be able to move "
        "as the study's state moves; covering it freezes the banner at whatever "
        "it said before the attempt ran.",
    "PREREG-REVIEW.md":
        "ADR 0004, round-3 finding R3-1: appendable by design. The pre-freeze "
        "review record grows by one disposition table per round, so covering it "
        "made every round's dispositions stale the committed manifest — three "
        "rounds running. The registered claims live in PREREGISTRATION.md and "
        "the artifacts, all of which stay covered.",
    "harness/PINS.json":
        "Study 014's round-3 linear-anchor rule: the manifest must not cover "
        "the registry that pins the manifest, or the anchor cannot be "
        "initialized without finding a SHA-256 fixed point.",
}

# Files this module and its neighbours WRITE, which therefore cannot be covered:
# the manifest cannot contain its own digest, and a scratch temporary is not a
# reviewed byte.
EXCLUDED_ARTIFACTS = ("harness/STUDY-MANIFEST.sha256",)


def _excluded(relative):
    return relative in EXCLUDED_DOCUMENTS or relative in EXCLUDED_ARTIFACTS


def pending_documents():
    """Registered documents that do not exist yet, in registered order."""
    return [name for name in REGISTERED_DOCUMENTS
            if not (STUDY / name).is_file()]


def manifest_entries():
    """Every covered path, study-relative, sorted.

    A registered document that does not exist yet is skipped rather than
    fabricated (`pending_documents()` names it, and `--freeze` refuses while any
    is pending). Everything else is discovered by an exact glob over the three
    code directories, so a harness source added after the freeze fails the
    exact-set comparison instead of entering it unnoticed.

    `harness/e4lib/` is globbed for the reason ADR 0004's manifest exists: the
    scorer's ten modules are reviewed sources that decide every published rate,
    and reviewed sources outside the exact-set manifest are exactly the hole the
    manifest closes (`harness/SCAFFOLD.md` item M1, point 4). The glob is one
    level and not recursive, matching the other three: a nested package added
    later must be registered here rather than swept in."""
    paths = [STUDY / name for name in REGISTERED_DOCUMENTS
             if (STUDY / name).is_file()]
    for directory, pattern in REGISTERED_PAYLOAD_SETS:
        paths.extend(sorted((STUDY / directory).glob(pattern)))
    paths.extend(sorted((STUDY / "harness").glob("*.py")))
    paths.extend(sorted((STUDY / "harness").glob("*.sh")))
    paths.extend(sorted((STUDY / "harness" / "e4lib").glob("*.py")))
    paths.extend(sorted((STUDY / "harness" / "tests").glob("*.py")))
    seen = []
    for path in paths:
        relative = path.relative_to(STUDY).as_posix()
        if _excluded(relative):
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
    parser.add_argument("--freeze", action="store_true",
                        help="write the manifest, refusing while any registered "
                             "document is still pending")
    arguments = parser.parse_args(argv)
    pending = pending_documents()
    if arguments.check:
        problems = manifest_problems()
        for problem in problems:
            print(problem)
        for name in pending:
            print("pending registered document (not covered yet): " + name)
        return 1 if problems else 0
    if arguments.freeze and pending:
        for name in pending:
            print("refused: registered document is absent: " + name)
        return 1
    MANIFEST_PATH.write_text(manifest_text(), encoding="utf-8")
    print("wrote %s (%d entries, %d registered documents pending)"
          % (MANIFEST_PATH.name, len(manifest_entries()), len(pending)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
