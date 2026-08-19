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

**ROUND-5 FINDING R5-6: a registered payload SET is pending like a registered
document.** `pending_documents()` used to walk `REGISTERED_DOCUMENTS` only, so
`--freeze` returned success over a tree with both mutant payload roots absent
and wrote a manifest with zero mutant payload entries — the exact hole the
per-file hashes exist to close, opened one level up at the directory. A
registered set is pending while its root is absent OR its glob is empty; the
scorer's own refusal (`score.py`) comes at attempt time, which is after the
freeze it was supposed to gate.

**ROUND-6 FINDING R6-5: a payload SET is closed, not merely non-empty.** R5-6's
gate asked whether each registered glob matched at least one file, so a tree
carrying one arbitrary file per payload directory froze successfully with the
other several hundred mutants missing — the scorer discovers that at ATTEMPT
time, which is again after the anchor. `payload_closure_problems()` derives the
expected filenames from the two frozen mutant MANIFESTs — the same rule
`e4lib/e4.py`'s `load_mutants()` uses, `<id>.json` for arm A and the record's
`file` for arm B, over EVERY record and not only the valid ones — and requires a
bijection with the directory and with the covered set: a named payload that is
absent, a file the manifest does not name, and a covered set that is not exactly
that set are three separate problems and all three refuse the freeze.

**ROUND-5 FINDING R5-1: tracked bytecode is a manifest problem.** A `.pyc`
committed beside a reviewed source is a byte that runs unreviewed, and it is
invisible to an exact-set manifest that globs `*.py` and `*.sh`. The round-4
response committed one; `integrity.verify_bytecode()` refused the tree on the
next checkout and the suite of record described a tree that HEAD was not.
`tracked_bytecode()` reads the INDEX (`git ls-files`) rather than the working
tree, because the failure is a committed byte and a working tree can be clean
of it while the index is not; `manifest_problems()` reports it and `--freeze`
refuses on it.

Run: <the pinned interpreter> harness/make_manifest.py [--check | --freeze]
"""

import argparse
import hashlib
import json
import subprocess
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


# Bytecode, by the two names it can be committed under. `__pycache__/` catches
# the directory whatever the interpreter tag; the suffixes catch a sourceless
# cache dropped anywhere else.
BYTECODE_SUFFIXES = (".pyc", ".pyo")


def tracked_paths(study=None):
    """Every path git has in the INDEX under the study, study-relative posix.

    Returns None when the study is not inside a git checkout — the caller then
    has nothing to check rather than a false clean bill.
    """
    root = Path(study) if study is not None else STUDY
    try:
        completed = subprocess.run(["git", "ls-files", "-z", "--", "."],
                                   cwd=str(root), capture_output=True)
    except OSError:
        return None
    if completed.returncode != 0:
        return None
    return [name for name in completed.stdout.decode("utf-8").split("\0") if name]


def tracked_bytecode(study=None):
    """ROUND-5 FINDING R5-1. Tracked compiled bytecode, sorted.

    Read from the index and not from the working tree: `git rm --cached`
    without the disk delete, and a disk delete without the `git rm`, are both
    states where one of the two lies about the other. The manifest's job is to
    describe what is COMMITTED.
    """
    tracked = tracked_paths(study)
    if tracked is None:
        return []
    found = []
    for name in tracked:
        parts = name.split("/")
        if "__pycache__" in parts or name.endswith(BYTECODE_SUFFIXES):
            found.append(name)
    return sorted(found)


def pending_payload_sets(study=None):
    """ROUND-5 FINDING R5-6. Registered payload sets that no file answers to.

    A set is pending while its root is absent or its glob matches nothing. The
    two states are reported separately because they are different mistakes —
    the directory was never created, or it was created and never filled — and
    both must block the freeze, exactly as an absent registered document does.
    """
    root = Path(study) if study is not None else STUDY
    pending = []
    for directory, pattern in REGISTERED_PAYLOAD_SETS:
        here = root / directory
        if not here.is_dir():
            pending.append(("%s/%s" % (directory, pattern), "directory absent"))
        elif not sorted(here.glob(pattern)):
            pending.append(("%s/%s" % (directory, pattern), "no file matches"))
    return pending


# ROUND-6 FINDING R6-5: the payload sets are CLOSED against the manifests that
# name them, file for file.
#
# R5-6 closed the empty root and stopped there: `pending_payload_sets()` asks
# whether the glob matches anything, so one arbitrary file per directory froze a
# tree whose mutants were almost all missing. The scorer discovers that at
# ATTEMPT time (`e4lib/e4.py` raises `E4-MISSING-MUTANT` when it cannot open a
# payload) — after the anchor the gate exists to hold.
#
# The expected filename is not invented here: it is the one `load_mutants()`
# computes. Arm A's manifest is a LIST of records keyed by `id`, and the payload
# is `<id>.json`; arm B's is a mapping with a `mutants` list whose records carry
# `file`. EVERY record counts, not only the valid ones — arm B's dropped mutant
# has a payload on disk, and a file the manifest does not name is as loud as one
# it names and cannot find.
PAYLOAD_MANIFESTS = (
    ("mutants/jps", "*.json", "mutants/MANIFEST-jps.json", "id"),
    ("mutants/rego", "*.rego", "mutants/MANIFEST-rego.json", "file"),
)


def _manifest_records(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("mutants"), list):
        return data["mutants"]
    return None


def expected_payloads(study=None, directory=None):
    """`{directory: sorted expected filenames}` derived from the frozen mutant
    manifests, or an entry of None where the manifest cannot be read."""
    root = Path(study) if study is not None else STUDY
    out = {}
    for where, _pattern, manifest, key in PAYLOAD_MANIFESTS:
        if directory is not None and where != directory:
            continue
        path = root / manifest
        if not path.is_file():
            out[where] = None
            continue
        try:
            records = _manifest_records(json.loads(path.read_text(encoding="utf-8")))
        except (ValueError, UnicodeDecodeError):
            records = None
        if records is None:
            out[where] = None
            continue
        names = []
        for record in records:
            if not isinstance(record, dict):
                names = None
                break
            if key == "id":
                value = record.get("id")
                names.append("%s.json" % value if value else None)
            else:
                names.append(record.get("file"))
        out[where] = None if names is None or None in names else sorted(names)
    return out


def payload_closure_problems(study=None):
    """R6-5. Exact closure: manifest ↔ directory ↔ covered set.

    Every payload the manifest names must exist, no other file may sit in the
    directory, and the study manifest must cover exactly that set. A manifest
    that cannot be read is a problem in itself — the whole point is that the
    freeze may not anchor a payload tree nobody has counted.
    """
    root = Path(study) if study is not None else STUDY
    problems = []
    expected = expected_payloads(study)
    covered = None
    for where, pattern, manifest, _key in PAYLOAD_MANIFESTS:
        here = root / where
        if not (root / manifest).is_file() and not here.is_dir():
            continue                     # both absent: pending, not unclosed
        names = expected.get(where)
        if names is None:
            problems.append(
                "payload manifest is absent or unreadable: " + manifest)
            continue
        on_disk = sorted(path.name for path in here.glob(pattern)) \
            if here.is_dir() else []
        for name in names:
            if name not in on_disk:
                problems.append("%s names %s and %s/%s does not exist"
                                % (manifest, name, where, name))
        for name in on_disk:
            if name not in names:
                problems.append("%s/%s is not named by %s"
                                % (where, name, manifest))
        if study is None or Path(study) == STUDY:
            if covered is None:
                covered = manifest_entries()
            mine = sorted(entry.split("/")[-1] for entry in covered
                          if entry.startswith(where + "/"))
            if mine != sorted(names):
                problems.append(
                    "the study manifest covers %d file(s) under %s and the "
                    "payload set is %d" % (len(mine), where, len(names)))
    return problems


def pending_documents(study=None):
    """Registered documents that do not exist yet, in registered order, and the
    registered payload SETS that nothing answers to (round-5 finding R5-6).

    One list, because `--freeze`'s gate is one question: is every registered
    thing here? A set named `mutants/jps/*.json` is registered as exactly as
    `gold/GOLD.json` is, and an absent one used to pass.
    """
    root = Path(study) if study is not None else STUDY
    pending = [name for name in REGISTERED_DOCUMENTS if not (root / name).is_file()]
    pending.extend("%s (%s)" % (glob, why)
                   for glob, why in pending_payload_sets(study))
    return pending


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
    # ROUND-5 FINDING R5-1. Not a digest mismatch — a covered-set one, in the
    # only direction an exact-set manifest cannot see: a file that is committed
    # and executable and matches no glob the manifest walks.
    for name in tracked_bytecode():
        problems.append("compiled bytecode is tracked in the study: " + name)
    # ROUND-6 FINDING R6-5. Also not a digest mismatch: a payload set that does
    # not close against the manifest naming it. Reported here so `--check` says
    # it, and refused below so `--freeze` cannot anchor it.
    problems.extend(payload_closure_problems())
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--freeze", action="store_true",
                        help="write the manifest, refusing while any registered "
                             "document is still pending")
    arguments = parser.parse_args(argv)
    pending = pending_documents()
    bytecode = tracked_bytecode()
    if arguments.check:
        problems = manifest_problems()
        for problem in problems:
            print(problem)
        for name in pending:
            print("pending registered document (not covered yet): " + name)
        return 1 if problems else 0
    if arguments.freeze and bytecode:
        # ROUND-5 FINDING R5-1: the freeze must not anchor a tree that carries
        # bytecode the reviewed sources did not produce.
        for name in bytecode:
            print("refused: compiled bytecode is tracked in the study: " + name)
        return 1
    if arguments.freeze and pending:
        for name in pending:
            print("refused: registered document is absent: " + name)
        return 1
    if arguments.freeze:
        # ROUND-6 FINDING R6-5: the payload sets must CLOSE against the manifests
        # that name them before anything is anchored. R5-6's gate asked only
        # whether the glob matched a file, so one sentinel per directory froze.
        closure = payload_closure_problems()
        if closure:
            for problem in closure:
                print("refused: " + problem)
            return 1
    MANIFEST_PATH.write_text(manifest_text(), encoding="utf-8")
    print("wrote %s (%d entries, %d registered documents pending)"
          % (MANIFEST_PATH.name, len(manifest_entries()), len(pending)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
