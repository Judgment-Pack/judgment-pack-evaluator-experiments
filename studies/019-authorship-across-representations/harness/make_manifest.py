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

**Five exclusions, each by construction and each asserted by a harness test.**
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
3. `harness/ADVISORIES.md` — **ADR 0004 again, and the RATIFIED SCOPE RULING of
   round 9.** The advisory register is the same shape of file as the two above:
   it grows by one entry whenever a review finding lands on the review-support
   apparatus (§4b) and is RECORDED rather than gated, and it is appended to for
   as long as that apparatus is maintained — including after the freeze, which
   is exactly when a recorded-not-gated finding is most likely to be revisited.
   Covering it would make the first such entry break the anchor. Nothing is lost:
   an advisory carries no claim any published number rests on, and §4b registers
   which surface it may and may not concern.
4. `harness/PINS.json` — Study 014's round-3 lesson, carried unchanged. The
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

**ROUND-8 FINDINGS R8-2 AND R8-8: two registered validators sat BESIDE the
gate.** R7-8 brought the sealed reviewer set inside the freeze as a set of
FILENAMES — closure, and a pin with a named source — and the component that
actually validates it, `e4lib/reviewer.py`'s `load()`, was never called from
here. The reviewer's construction: with the manifest digest re-pinned, one
reviewer payload replaced by `{}` left `pending=[]`, closure clean and `--freeze`
successful, while `load()` refused the same tree with `REVIEWER-SET-DIGEST`. A
filename check beside a schema/digest validator is not the validator, so
`reviewer_load_problems()` calls it — the non-executing path, exactly as §1a
registers — and both `--check` and `--freeze` read the answer.

R8-8 is the same shape at the other artifact: `design/BRIEF.md` §2.3 registers a
freeze-time full-grid `project -> re-serialize -> byte-equal` assertion and
`design/POLICY-DRAFT.md` registers range/form validation of the canonical grid
at freeze, and no step ran either. `harness/grid_gate.py` is that assertion and
`freeze_gate_problems()` runs it here.

Both are reachable on their own as `--freeze-gates`, so the ceremony's step F5c
is a command rather than a memory.

**ROUND-9 FINDING R9-2: the preregistration's own freeze condition was checked
only AFTER the freeze.** "At the freeze, every pin in `harness/PINS.json` is
filled; `results/primary-attempt-001` must not exist, and the scorer refuses if
it does" (`PREREGISTRATION.md`, "The freeze and the primary attempt") — and the
scorer's refusal comes at ATTEMPT time, which is after the anchor. A tree
carrying a prior attempt root could therefore be frozen, and the condition the
freeze registers would be enforced by nothing at the moment it names.
`prior_attempt_problems()` is that condition, at that moment: the registered
root is looked up with `lexists` (a dangling symlink is a name that exists), any
OTHER entry under `results/` is an attempt root under another name, and the
INDEX is read as well as the disk, because a working tree can be clean of a
directory HEAD still carries. It joins `freeze_gate_problems()`, so `--check`
reports it, `--freeze-gates` runs it and `--freeze` refuses on it.

Run: <the pinned interpreter> harness/make_manifest.py
                                      [--check | --freeze | --freeze-gates]
"""

import argparse
import hashlib
import json
import re
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
    # ROUND-7 FINDING R7-9: declared pre-freeze obligations that sat OUTSIDE the
    # freeze gate. Each of the three is required before the freeze by a document
    # in this tree, none of them was pinned, manifest-covered or named by the
    # runbook, and the ceremony could therefore complete without any of them.
    #
    #   CORRECTION-TARGETS.md            §10 pins the CORRECTION.md targets —
    #                                    verbatim wording, venue, URL and
    #                                    retrieval date — before the freeze
    #   verification/V7-COMPLETENESS.md  design/POLICY-DRAFT.md's V7: one
    #                                    governing clause per gold-grid cell,
    #                                    re-derived mechanically, with the
    #                                    former X1 region asserted COVERED
    #   verification/V8-ASYMMETRY-LEDGER.md
    #                                    the same document's V8: the asymmetry
    #                                    ledger re-derived from the two
    #                                    references, with its final balance
    #
    # Registering them here is what makes the freeze refuse while any is absent.
    # Withdrawing one is a decision that must delete its obligation from the
    # document that declares it, in the same commit — not a quiet omission here.
    "CORRECTION-TARGETS.md",
    "verification/V7-COMPLETENESS.md",
    "verification/V8-ASYMMETRY-LEDGER.md",
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
    "harness/ADVISORIES.md":
        "ADR 0004, round-9 ratified scope ruling: appendable by design. The "
        "advisory register grows by one entry per recorded-not-gated finding "
        "against the review-support apparatus (PREREGISTRATION.md §4b), for as "
        "long as that apparatus is maintained; covering it means the first "
        "advisory breaks the anchor, exactly as PREREG-REVIEW.md did three "
        "rounds running. No advisory carries a claim a published number rests "
        "on.",
    "harness/PINS.json":
        "Study 014's round-3 linear-anchor rule: the manifest must not cover "
        "the registry that pins the manifest, or the anchor cannot be "
        "initialized without finding a SHA-256 fixed point.",
}

# ROUND-9 FINDING R9-2. The preregistration's freeze condition, as a path this
# module can look up. `harness/batch.py` owns the absolute constant
# (`batch.ATTEMPT_ROOT`) and the scorer takes it as `--attempt-root`; this is the
# same path study-relative, and `tests/test_manifest.py` asserts the two agree
# rather than trusting a second spelling of one registered name.
RESULTS_DIR = "results"
PRIMARY_ATTEMPT_ROOT = RESULTS_DIR + "/primary-attempt-001"


def authoring_state_paths():
    """ROUND-10 FINDING R10-1. `(slot directories, ledger files)` — the places
    an AUTHORING RUN leaves bytes, study-relative posix.

    DERIVED from `harness/batch.py`'s own constants and its own `slot_path()`,
    never spelled again here. `arms/<ARM>/authoring` and `arms/BATCH.json` are
    the driver's spellings; a second copy of them in this file is a second thing
    to keep in step with the module that writes them, and this gate exists
    precisely because a gate can be true of a path nobody writes any more.

    The ledger names are the three files the driver owns under `arms/`: the
    ledger itself, its registered atomic-write temporary, and the shortfall
    declaration. `arms/<ARM>/PROMPT.txt` is deliberately NOT reachable from
    here — an arm prompt is a registered input that must exist before the
    freeze, and the authoring TREE beneath it is what must not.
    """
    import batch                          # local: batch imports this module
    study = Path(batch.STUDY)
    directories, files = [], []
    for arm in batch.ARMS:
        slot = Path(batch.slot_path({"arm": arm, "slotIndex": 1}))
        directories.append(slot.parent)
    for name in (batch.LEDGER_NAME, batch.LEDGER_TEMP_NAME,
                 batch.SHORTFALL_NAME):
        files.append(Path(batch.ARMS_ROOT) / name)
    def relative(path):
        try:
            return path.relative_to(study).as_posix()
        except ValueError:
            raise ValueError(
                "harness/batch.py places %s outside %s: this gate reads the "
                "driver's own constants, and a driver whose roots have left the "
                "study is not a tree this module can make a claim about"
                % (path, study))
    return (tuple(relative(path) for path in directories),
            tuple(relative(path) for path in files))

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


class IndexUnreadable(Exception):
    """ROUND-10 FINDING R10-2. The index could not be OBSERVED — git missing
    from PATH, git exiting nonzero, or its output not decodable as UTF-8.

    A named exception rather than a `None` return, because `None` was read by
    both callers as "nothing is indexed", and a gate that cannot read the index
    concluding emptiness is the failure mode R9-2's check existed to prevent: in
    a scratch repository the reviewer staged
    `results/primary-attempt-001/RESULTS.json`, deleted it from disk, made git
    unavailable, and `--freeze` returned success over a tree whose index carried
    a prior attempt. Every consumer turns this into a named problem instead.
    """


def tracked_paths(study=None):
    """Every path git has in the INDEX under the study, study-relative posix.

    Raises `IndexUnreadable` when the index cannot be observed (R10-2). It does
    NOT return an empty list for that state: "git said nothing is indexed" and
    "git could not be asked" are different facts and only one of them is a clean
    bill.
    """
    root = Path(study) if study is not None else STUDY
    try:
        completed = subprocess.run(["git", "ls-files", "-z", "--", "."],
                                   cwd=str(root), capture_output=True)
    except OSError as error:
        raise IndexUnreadable("`git ls-files` could not be run in %s (%s: %s)"
                              % (root, type(error).__name__, error))
    if completed.returncode != 0:
        raise IndexUnreadable(
            "`git ls-files` exited %d in %s (%s)"
            % (completed.returncode, root,
               completed.stderr.decode("utf-8", "replace").strip()
               or "no stderr"))
    try:
        listing = completed.stdout.decode("utf-8")
    except UnicodeDecodeError as error:
        raise IndexUnreadable("`git ls-files` output is not UTF-8 in %s (%s)"
                              % (root, error))
    return [name for name in listing.split("\0") if name]


def tracked_bytecode(study=None):
    """ROUND-5 FINDING R5-1. Tracked compiled bytecode, sorted.

    Read from the index and not from the working tree: `git rm --cached`
    without the disk delete, and a disk delete without the `git rm`, are both
    states where one of the two lies about the other. The manifest's job is to
    describe what is COMMITTED.

    ROUND-10 FINDING R10-2: `IndexUnreadable` propagates. This function used to
    swallow it into `[]`, which is the same fail-open the finding is about, one
    check over.
    """
    tracked = tracked_paths(study)
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


# ROUND-7 FINDING R7-6: EXACTLY the scorer's shape, per arm, or a refusal that
# names itself.
#
# `_manifest_records()` accepted a bare LIST or `{"mutants": [...]}` for EITHER
# arm and then derived the filename from whichever member the arm's tuple named.
# `e4lib/e4.py`'s `load_mutants()` does neither of those things: it iterates the
# JPS manifest DIRECTLY, which makes a top-level JSON list the only shape it can
# read, and it reads the Rego manifest's `["mutants"]`, which makes a top-level
# object the only shape it can read. So two manifests with their shapes SWAPPED
# and payload filenames that happen to match closed the freeze here and raised
# `E4-MISSING-MUTANT` at the attempt — after the anchor this gate exists to
# hold. A numeric JPS id was the same defect one level down: `1` renders a
# plausible `1.json` in closure and fails `mutant["id"] + ".json"` in the
# scorer, which concatenates a string.
#
# The shape is therefore arm-specific and strict, the id/file member must be a
# plain filename component, and the alternative shape is a named refusal rather
# than an accepted variant.
_PAYLOAD_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _manifest_records(data, key):
    """`(records, refusal)` for one arm, in exactly the shape the scorer reads."""
    if key == "id":
        if not isinstance(data, list):
            return None, ("arm A's manifest is a JSON %s and e4lib/e4.py "
                          "iterates a top-level LIST"
                          % type(data).__name__)
        return data, None
    if not isinstance(data, dict):
        return None, ("arm B's manifest is a JSON %s and e4lib/e4.py reads a "
                      "top-level OBJECT's `mutants`" % type(data).__name__)
    records = data.get("mutants")
    if not isinstance(records, list):
        return None, "arm B's manifest carries no top-level `mutants` list"
    return records, None


def _payload_names(records, key):
    """`(sorted filenames, refusal)` by the same rule `load_mutants()` uses:
    `<id>.json` for arm A, the record's own `file` for arm B. EVERY record
    counts, not only the valid ones — arm B's dropped mutant has a payload on
    disk, and a file the manifest does not name is as loud as one it names and
    cannot find."""
    names = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            return None, "record %d is a JSON %s and a record is an object" \
                % (index, type(record).__name__)
        value = record.get(key)
        if not isinstance(value, str) or not _PAYLOAD_NAME.match(value):
            return None, (
                "record %d's `%s` is %r; the scorer builds the payload path "
                "from it, so it must be a plain filename component"
                % (index, key, value))
        names.append("%s.json" % value if key == "id" else value)
    return sorted(names), None


def expected_payloads(study=None, directory=None):
    """`{directory: (sorted expected filenames, refusal)}` derived from the
    frozen mutant manifests. Exactly one of the pair is None."""
    root = Path(study) if study is not None else STUDY
    out = {}
    for where, _pattern, manifest, key in PAYLOAD_MANIFESTS:
        if directory is not None and where != directory:
            continue
        path = root / manifest
        if not path.is_file():
            out[where] = (None, "the payload manifest %s does not exist" % manifest)
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeDecodeError) as error:
            out[where] = (None, "%s is not readable JSON (%s)"
                          % (manifest, type(error).__name__))
            continue
        records, refusal = _manifest_records(data, key)
        if refusal is not None:
            out[where] = (None, "%s: %s" % (manifest, refusal))
            continue
        names, refusal = _payload_names(records, key)
        out[where] = ((None, "%s: %s" % (manifest, refusal))
                      if refusal is not None else (names, None))
    return out


# ROUND-7 FINDING R7-8: the sealed reviewer set is a REGISTERED set and its
# closure was never checked.
#
# `controls/reviewer-mutants` is one of the registered payload sets and its
# bytes are what a REGISTERED attempt executes (§1a/§4, round-1 R1-10), yet
# exact manifest ↔ payload closure was implemented only for the two primary
# mutant manifests. The set's manifest is the shape `e4lib/reviewer.py` loads —
# a top-level object with a `mutants` list whose records carry `file` — and its
# own bytes are what `reviewerMutantSet.sha256` pins, so the manifest is part of
# the covered set alongside the payloads it names.
REVIEWER_SET_DIR = "controls/reviewer-mutants"
REVIEWER_SET_MANIFEST = "MANIFEST.json"


def reviewer_set_expected(study=None):
    """`(sorted expected filenames, refusal)` for the sealed set — its manifest
    plus every payload the manifest names."""
    root = Path(study) if study is not None else STUDY
    path = root / REVIEWER_SET_DIR / REVIEWER_SET_MANIFEST
    if not path.is_file():
        return None, ("%s/%s does not exist; the sealed set is a registered set "
                      "and its manifest is what `reviewerMutantSet.sha256` pins"
                      % (REVIEWER_SET_DIR, REVIEWER_SET_MANIFEST))
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as error:
        return None, "%s/%s is not readable JSON (%s)" \
            % (REVIEWER_SET_DIR, REVIEWER_SET_MANIFEST, type(error).__name__)
    records, refusal = _manifest_records(data, "file")
    if refusal is not None:
        return None, "%s/%s: %s" % (REVIEWER_SET_DIR, REVIEWER_SET_MANIFEST,
                                    refusal.replace("arm B's manifest",
                                                    "the sealed manifest"))
    names, refusal = _payload_names(records, "file")
    if refusal is not None:
        return None, "%s/%s: %s" % (REVIEWER_SET_DIR, REVIEWER_SET_MANIFEST,
                                    refusal)
    return sorted(names + [REVIEWER_SET_MANIFEST]), None


def reviewer_set_digest(study=None):
    """The digest `reviewerMutantSet.sha256` is filled from, or None while the
    manifest is absent. Named here so the freeze runbook has one place to point
    at and `harness/integrity.py`'s pin-source table can name it."""
    root = Path(study) if study is not None else STUDY
    path = root / REVIEWER_SET_DIR / REVIEWER_SET_MANIFEST
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reviewer_set_closure_problems(study=None):
    """R7-8. The same exact closure the two mutant corpora get: every payload
    the sealed manifest names exists, no other file sits beside it, and the
    study manifest covers exactly that set plus the manifest itself."""
    root = Path(study) if study is not None else STUDY
    here = root / REVIEWER_SET_DIR
    if not here.is_dir():
        return []                        # pending, not unclosed
    names, refusal = reviewer_set_expected(study)
    if refusal is not None:
        return [refusal]
    on_disk = sorted(path.name for path in here.iterdir()
                     if path.is_file() and path.name.endswith((".json", ".rego")))
    problems = []
    for name in names:
        if name not in on_disk:
            problems.append("%s/%s names %s and it does not exist"
                            % (REVIEWER_SET_DIR, REVIEWER_SET_MANIFEST, name))
    for name in on_disk:
        if name not in names:
            problems.append("%s/%s is not named by %s"
                            % (REVIEWER_SET_DIR, name, REVIEWER_SET_MANIFEST))
    if study is None or Path(study) == STUDY:
        covered = sorted(entry.split("/")[-1] for entry in manifest_entries()
                         if entry.startswith(REVIEWER_SET_DIR + "/"))
        if covered != sorted(names):
            problems.append(
                "the study manifest covers %d file(s) under %s and the sealed "
                "set is %d" % (len(covered), REVIEWER_SET_DIR, len(names)))
    return problems


def reviewer_load_problems(study=None):
    """ROUND-8 FINDING R8-2. The sealed set's OWN loader, run at the gate.

    `reviewer_set_closure_problems()` above compares filenames; `load()` is the
    component that validates `reviewerSetVersion`, the registered manifest
    members, the 6-10 cardinality, both languages, every record's members, the
    registered `rm-<language>-NN.<ext>` filename, containment on real paths, and
    every payload's digest — and the freeze never called it. The reviewer's
    construction was one payload replaced by `{}`: closure clean, `pending=[]`,
    `--freeze` successful, and `load()` refusing the same tree.

    It is called with the registry's pin when the registry has one, so the
    digest that binds the executed bytes to the freeze is checked here too; a
    null pin (pre-freeze) still gets the whole schema and every payload digest.
    `load()` runs no engine, which is what keeps "first executed at the primary
    attempt" true of the pre-attempt path.
    """
    root = Path(study) if study is not None else STUDY
    here = root / REVIEWER_SET_DIR
    if not here.is_dir():
        return []                        # pending, not invalid
    try:
        from e4lib import reviewer as reviewer_module
    except ImportError as error:
        return ["the sealed reviewer set's loader could not be imported (%s); "
                "the freeze may not anchor a set nothing validated" % error]
    pinned = None
    registry = root / "harness" / "PINS.json"
    if registry.is_file():
        try:
            pins = json.loads(registry.read_text(encoding="utf-8"))
        except (ValueError, UnicodeDecodeError):
            pins = {}
        pinned = (pins.get("reviewerMutantSet") or {}).get("sha256") \
            if isinstance(pins.get("reviewerMutantSet"), dict) else None
    try:
        reviewer_module.load(str(here), pinned)
    except reviewer_module.ReviewerSetError as error:
        return ["the sealed reviewer set does not load: %s" % error]
    except (OSError, ValueError) as error:
        return ["the sealed reviewer set could not be read (%s: %s)"
                % (type(error).__name__, error)]
    return []


def grid_assertion_problems(study=None):
    """ROUND-8 FINDING R8-8. The registered freeze-time grid assertion, run.

    `design/BRIEF.md` §2.3 registers `project -> re-serialize -> byte-equal` over
    the FULL grid with a nonzero exit, and `design/POLICY-DRAFT.md` registers
    that the canonical grid carries no malformed or out-of-range values,
    "asserted at freeze". `harness/grid_gate.py` is both assertions; this is the
    line that makes the ceremony run them."""
    try:
        import grid_gate
    except ImportError as error:
        return ["the canonical-grid assertion could not be imported (%s)" % error]
    root = Path(study) if study is not None else STUDY
    return ["canonical grid: " + problem
            for problem in grid_gate.grid_problems(str(root))]


def prior_attempt_problems(study=None):
    """ROUND-9 FINDING R9-2. The freeze condition the preregistration states and
    only the SCORER enforced.

    `PREREGISTRATION.md` ("The freeze and the primary attempt"): at the freeze
    `results/primary-attempt-001` must not exist. The scorer refuses an existing
    attempt root at ATTEMPT time — after the anchor — so a tree carrying a prior
    attempt was freezable, and the sentence was enforced by nothing at the moment
    it names.

    Three ways a prior attempt is present, and each of them refuses:

    * the registered root exists as a NAME — `lexists`, not `isdir`, because a
      dangling symlink named `results/primary-attempt-001` is a root that exists
      and that `isdir`/`exists` both call absent;
    * some OTHER entry sits under `results/` — an attempt root under a second
      name is the same fact, and the freeze may not anchor a tree in which a rate
      may already have been computed;
    * the INDEX carries a descendant of `results/` — read exactly as
      `tracked_bytecode()` reads it (R5-1's lesson), because a working tree can
      be clean of a directory HEAD still carries, and the freeze anchors a
      COMMIT.
    """
    root = Path(study) if study is not None else STUDY
    problems = []
    registered = root / PRIMARY_ATTEMPT_ROOT
    if registered.is_symlink() or registered.exists():
        problems.append(
            "%s exists and the preregistration registers its ABSENCE at the "
            "freeze: the primary attempt is the first invocation from the "
            "freeze commit, and a root that is already there means a rate may "
            "already have been computed" % PRIMARY_ATTEMPT_ROOT)
    here = root / RESULTS_DIR
    if here.is_dir():
        for entry in sorted(here.iterdir(), key=lambda path: path.name):
            relative = "%s/%s" % (RESULTS_DIR, entry.name)
            if relative == PRIMARY_ATTEMPT_ROOT:
                continue                 # already named above
            problems.append(
                "%s exists: an attempt root under a second name is the same "
                "fact the freeze forbids, and `results/` holds attempt roots "
                "and nothing else" % relative)
    # ROUND-10 FINDING R10-2. The index check FAILS CLOSED. It used to read a
    # `None` from `tracked_paths()` — git absent, or git nonzero — as "no
    # indexed paths", so the one state in which the check cannot see anything
    # was the state in which it passed. A gate that cannot read the index
    # refuses with a named problem; it does not conclude emptiness.
    try:
        tracked = tracked_paths(study)
    except IndexUnreadable as error:
        problems.append(
            "the index under %s could not be read (%s): the freeze anchors a "
            "commit, so the absence of a prior attempt is a claim about the "
            "INDEX, and a check that cannot observe the index refuses rather "
            "than reporting a tree it never saw" % (root, error))
        tracked = []
    if tracked:
        indexed = sorted(name for name in tracked
                         if name.split("/")[0] == RESULTS_DIR)
        if indexed:
            problems.append(
                "the index carries %d path(s) under %s/ (%s): the freeze "
                "anchors a commit, and a working tree clean of an attempt root "
                "the index still has is not a tree without one"
                % (len(indexed), RESULTS_DIR, ", ".join(indexed[:3])))
    return problems


def prior_authoring_problems(study=None):
    """ROUND-10 FINDING R10-1. The freeze condition one step EARLIER than R9-2's:
    at the freeze no authoring run exists at all, not merely no rate.

    `PREREGISTRATION.md` §1a registers the study's prospective content as "the
    150 post-freeze runs — no authoring run exists at freeze time", and the
    registry's own rule keeps every freeze pin null until the freeze so that no
    run CAN be made before it. `prior_attempt_problems()` above enforces the
    later half of the same sentence — no attempt ROOT — and enforcing only that
    half leaves the state the round-10 reviewer actually constructed freezable:
    slots authored under a substitute complete registry, sitting in
    `arms/<ARM>/authoring/` with their ledger beside them, and no rate computed
    over them yet. That tree would have been anchored by the freeze commit and
    the runs inside it scored afterwards as the study's prospective content.

    Three ways authoring state is present, and each of them refuses:

    * an authoring slot ROOT exists as a NAME — `lexists`, not `isdir`, for
      R9-2's reason: a dangling symlink named `arms/A/authoring` is a tree that
      exists and that `isdir`/`exists` both call absent. The DIRECTORY is the
      condition and not its contents, because an empty `arms/A/authoring` is a
      batch that started;
    * a ledger FILE exists — `arms/BATCH.json`, its atomic-write temporary or a
      shortfall declaration. A ledger without slots is a batch whose slots were
      deleted, which is a stronger reason to refuse and not a weaker one;
    * the INDEX carries either — read exactly as `prior_attempt_problems()`
      reads it, and FAIL-CLOSED on an index that cannot be observed (R10-2),
      because the freeze anchors a COMMIT and a working tree can be clean of an
      authoring tree HEAD still carries.

    None of this reaches `arms/<ARM>/PROMPT.txt`: the arm prompts are registered
    inputs that must EXIST before the freeze. `authoring_state_paths()` is where
    that boundary is drawn, from the driver's own constants.
    """
    root = Path(study) if study is not None else STUDY
    directories, files = authoring_state_paths()
    problems = []
    for relative in directories:
        here = root / relative
        if here.is_symlink() or here.exists():
            problems.append(
                "%s exists and the preregistration registers that NO authoring "
                "run exists at the freeze: the study's prospective content is "
                "the 150 post-freeze runs, and a slot tree that is already "
                "there is a run the freeze did not anchor" % relative)
    for relative in files:
        here = root / relative
        if here.is_symlink() or here.exists():
            problems.append(
                "%s exists and the preregistration registers that NO authoring "
                "run exists at the freeze: a ledger is the record of calls "
                "already made" % relative)
    try:
        tracked = tracked_paths(study)
    except IndexUnreadable as error:
        problems.append(
            "the index under %s could not be read (%s): the freeze anchors a "
            "commit, so the absence of pre-freeze authoring is a claim about "
            "the INDEX, and a check that cannot observe the index refuses "
            "rather than reporting a tree it never saw" % (root, error))
        tracked = []
    indexed = sorted(
        name for name in tracked
        if name in files
        or any(name == where or name.startswith(where + "/")
               for where in directories))
    if indexed:
        problems.append(
            "the index carries %d authoring path(s) (%s): the freeze anchors a "
            "commit, and a working tree clean of an authoring run the index "
            "still has is not a tree without one"
            % (len(indexed), ", ".join(indexed[:3])))
    return problems


def freeze_gate_problems(study=None):
    """The registered validators that are not filename comparisons, in one
    list: the sealed set's loader (R8-2), the canonical grid's freeze-time
    assertion (R8-8), the absence of a prior attempt root (R9-2) and the absence
    of any pre-existing authoring state (R10-1). `--check` reports them,
    `--freeze` refuses on them, and `--freeze-gates` runs exactly these."""
    return (reviewer_load_problems(study) + grid_assertion_problems(study)
            + prior_attempt_problems(study) + prior_authoring_problems(study))


def payload_closure_problems(study=None):
    """R6-5. Exact closure: manifest ↔ directory ↔ covered set.

    Every payload the manifest names must exist, no other file may sit in the
    directory, and the study manifest must cover exactly that set. A manifest
    that cannot be read is a problem in itself — the whole point is that the
    freeze may not anchor a payload tree nobody has counted.

    ROUND-7 FINDING R7-6: the refusal now NAMES itself, because "absent or
    unreadable" was true of a manifest in the other arm's shape and told the
    operator nothing about which of the two mistakes they had made. ROUND-7
    FINDING R7-8 adds the sealed reviewer set, which was a registered set with
    no closure at all.
    """
    root = Path(study) if study is not None else STUDY
    problems = []
    expected = expected_payloads(study)
    covered = None
    for where, pattern, manifest, _key in PAYLOAD_MANIFESTS:
        here = root / where
        if not (root / manifest).is_file() and not here.is_dir():
            continue                     # both absent: pending, not unclosed
        names, refusal = expected.get(where, (None, "unregistered payload set"))
        if names is None:
            problems.append("payload closure refused: " + refusal)
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
    problems.extend(reviewer_set_closure_problems(study))
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
    pending.extend(pending_pins(study))
    return pending


# ROUND-7 FINDING R7-8: the registered freeze procedure had NO step that filled
# the mandatory reviewer-set pin.
#
# `reviewerMutantSet.sha256` is one of the eighteen pins `integrity.study_label()`
# requires for `REGISTERED`, it is null, and `SCAFFOLD.md`'s exhaustive
# freeze-fill filled the other pins and then claimed the label. A pin whose
# SOURCE nobody names is a pin nobody fills, so the source is named here — the
# digest of the sealed manifest — and the gate reports it beside the pending
# documents. The ceremony cannot complete without it.
PENDING_PIN_SOURCES = (
    ("reviewerMutantSet.sha256", REVIEWER_SET_DIR + "/" + REVIEWER_SET_MANIFEST,
     reviewer_set_digest),
)


def pending_pins(study=None):
    """Freeze pins this module can compute the source of and that the registry
    has not been given, each named WITH that source."""
    root = Path(study) if study is not None else STUDY
    registry = root / "harness" / "PINS.json"
    if not registry.is_file():
        return []
    try:
        pins = json.loads(registry.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError):
        return ["harness/PINS.json is not readable JSON"]
    out = []
    for dotted, source, compute in PENDING_PIN_SOURCES:
        node = pins
        for key in dotted.split(".")[:-1]:
            node = node.get(key) if isinstance(node, dict) else None
        recorded = node.get(dotted.split(".")[-1]) if isinstance(node, dict) else None
        actual = compute(study)
        if actual is None:
            continue                     # the source itself is not here yet
        if recorded is None:
            out.append("%s (fill from the sha256 of %s: %s)"
                       % (dotted, source, actual))
        elif str(recorded).split(":")[-1].strip() != actual:
            out.append("%s records %r and %s hashes to %s"
                       % (dotted, recorded, source, actual))
    return out


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
    # ROUND-10 FINDING R10-2: and an index that cannot be read is a problem
    # here too, not an empty bytecode list.
    try:
        bytecode = tracked_bytecode()
    except IndexUnreadable as error:
        bytecode = []
        problems.append("the index could not be read (%s): tracked bytecode is "
                        "a claim about the index and this check did not make it"
                        % error)
    for name in bytecode:
        problems.append("compiled bytecode is tracked in the study: " + name)
    # ROUND-6 FINDING R6-5. Also not a digest mismatch: a payload set that does
    # not close against the manifest naming it. Reported here so `--check` says
    # it, and refused below so `--freeze` cannot anchor it.
    problems.extend(payload_closure_problems())
    # ROUND-8 FINDINGS R8-2 AND R8-8, ROUND-9 FINDING R9-2 AND ROUND-10 FINDING
    # R10-1. None of the four is a digest mismatch either: a sealed set that its
    # own loader refuses, a canonical grid that fails the assertion two design
    # documents register for the freeze, a prior attempt root the preregistration
    # registers as absent at this moment, and any authoring slot tree or ledger,
    # which the same document registers as absent one step earlier. `--check`
    # says all four, and `--freeze` refuses on all four.
    problems.extend(freeze_gate_problems())
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--freeze", action="store_true",
                        help="write the manifest, refusing while any registered "
                             "document is still pending")
    parser.add_argument("--freeze-gates", dest="gates", action="store_true",
                        help="run the registered freeze-time validators alone: "
                             "the sealed reviewer set's loader (R8-2), the "
                             "canonical grid's assertion (R8-8), the absence of "
                             "a prior attempt root (R9-2) and the absence of any "
                             "pre-existing authoring state (R10-1)")
    arguments = parser.parse_args(argv)
    pending = pending_documents()
    # ROUND-10 FINDING R10-2. An unreadable index is a REFUSAL of every writing
    # path, not an empty bytecode list: the two checks that read the index —
    # R5-1's tracked bytecode and R9-2's prior attempt — both make claims about
    # a commit, and neither can be made from a tree git cannot be asked about.
    # `--check` and `--freeze-gates` report it through `manifest_problems()` and
    # `prior_attempt_problems()`; this is the same fact at the one place that
    # WRITES.
    try:
        bytecode = tracked_bytecode()
        index_unreadable = None
    except IndexUnreadable as error:
        bytecode, index_unreadable = [], str(error)
    if arguments.gates:
        # ROUND-8 FINDINGS R8-2 AND R8-8, as a step an operator can run and a
        # CI job can call. Reported before the manifest work below, and on its
        # own, because these two are about the ARTIFACTS being frozen rather
        # than about the covered set.
        gates = freeze_gate_problems()
        for problem in gates:
            print("refused: " + problem)
        if not gates:
            print("freeze gates hold: the sealed reviewer set loads, the "
                  "canonical grid assertion holds, no prior attempt root "
                  "exists, and no authoring slot tree or ledger exists")
        if not (arguments.check or arguments.freeze):
            return 1 if gates else 0
        if gates:
            return 1
    if arguments.check:
        problems = manifest_problems()
        for problem in problems:
            print(problem)
        for name in pending:
            print("pending pre-freeze obligation (not satisfied yet): " + name)
        return 1 if problems else 0
    if index_unreadable is not None:
        # ROUND-10 FINDING R10-2: nothing is WRITTEN over a tree whose index
        # could not be observed. `--check` above has already reported it as a
        # problem; every path below this line either anchors the freeze or
        # rewrites the manifest, and both of them describe a commit.
        print("refused: the index could not be read (%s): the manifest and the "
              "freeze both describe a COMMIT, and a tree git cannot be asked "
              "about is not a tree this module may write over" % index_unreadable)
        return 1
    if arguments.freeze and bytecode:
        # ROUND-5 FINDING R5-1: the freeze must not anchor a tree that carries
        # bytecode the reviewed sources did not produce.
        for name in bytecode:
            print("refused: compiled bytecode is tracked in the study: " + name)
        return 1
    if arguments.freeze and pending:
        # ROUND-7 FINDINGS R7-8 AND R7-9: `pending` is every declared pre-freeze
        # obligation this module can check, not only the documents — the
        # registered payload sets, the CORRECTION.md target register, the two
        # verification artifacts, and the reviewer-set pin with the source it is
        # filled from. A ceremony that can complete while one of them is missing
        # is a ceremony that never enforced it.
        for name in pending:
            print("refused: pre-freeze obligation not satisfied: " + name)
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
        # ROUND-8 FINDINGS R8-2 AND R8-8, ROUND-9 FINDING R9-2 AND ROUND-10
        # FINDING R10-1: and the registered VALIDATORS, which closure is not. A
        # set whose loader refuses it, a grid that fails the assertion registered
        # for this moment, a tree carrying a prior attempt root, and a tree
        # carrying authoring slots or a ledger are all four anchorable without
        # this call — the first is exactly what the round-8 reviewer
        # constructed, the third is a condition the preregistration states about
        # the freeze and the scorer checked one step too late, and the fourth is
        # the state the round-10 reviewer reached through the alternate-registry
        # seam: runs made before the freeze, which no gate looked for.
        gates = freeze_gate_problems()
        if gates:
            for problem in gates:
                print("refused: " + problem)
            return 1
    MANIFEST_PATH.write_text(manifest_text(), encoding="utf-8")
    print("wrote %s (%d entries, %d registered documents pending)"
          % (MANIFEST_PATH.name, len(manifest_entries()), len(pending)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
