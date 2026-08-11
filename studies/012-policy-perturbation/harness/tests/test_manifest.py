#!/usr/bin/env python3
"""§2.10 [D-20]'s tree manifest, and the rule it matches its exclusions by
(round 9, finding 5).

The manifest is the single mechanism the review-to-freeze binding rests on, and
until this file nothing in the suite exercised it: `tree_manifest()` was run
only by each round's reviewer, recomputing it by hand. What the round-9 finding
caught is that the matching rule lived only in the code, and the code read the
registered list as a set of PREFIXES — so a file-shaped entry silently swallowed
anything tracked beneath its name, and the trailing slashes that distinguish the
seven tree entries from the eight file entries in `harness/PINS.json` were
decorative. Registered bytes could then sit inside the reviewed tree and outside
the manifest, which is the one class of gap §2.10 exists to close.

`integrity.manifest_excluded()` is now the rule, and §2.10 item 2 states it: an
entry ending in `/` names a tree and takes everything beneath it; every other
entry names exactly one path. The asymmetry is deliberate in both directions —
a tracked file sitting at a tree entry's BARE name (no slash) is reviewed bytes
and stays in the manifest, and so does a tracked file under a file entry's name.

Nine assertions:

1. a file-shaped entry excludes that path and no descendant of it — including
   the two `MANIFEST_CARRIERS`, which the same widening covered;
2. a tree-shaped entry excludes its subtree, does NOT excuse its own bare name,
   and does not reach a sibling whose name it merely prefixes (`arms/AA/`);
3. the registered list keeps its registered SHAPE — nine files and eight
   trees — so a later edit that drops a slash, silently widening the exclusion
   again, fails here rather than in a reviewer's recomputation;
4. `tree_manifest()` itself honours the distinction, end to end over a throwaway
   git repo, because a rule asserted only against its own helper is the callee
   vouching for itself. This is the regression the fix pins: under the old
   prefix reading the `RESULTS.json/nested.txt` assertion fails;
5. the invariant that makes the change provably digest-neutral for THIS tree:
   no tracked path in the committed study hides under a file-shaped entry;
6. and the property the exclusions exist to buy — the manifest is IDENTICAL
   after every registered act of the study's lifecycle, from recording a review
   round through the freeze, the golden recapture, §6 C7, the batch, the
   scoring and the publication. The scoring act's DESTINATION is the one
   README step 7 names, read out of the README rather than chosen here; the
   layout beneath it is this file's model of what `_emit_records()` writes;
   the publication act includes `CORRECTION.md`, which §8 requires written in
   every outcome. That is what makes §2.10 rule 3 terminate, and it is asserted
   here by applying each act to a copy of the tree rather than argued in prose;
7. the destination README step 7 emits the compiled records into is a
   registered exclusion tree, read out of the README's own command literal
   rather than restated here (round 14, finding 1);
8. every destination the study's writers NAME is an excluded path — read out of
   their own source rather than modelled here, so an output a writer grows
   without an entry in `freeze.excluded` fails whatever it is called, which is
   what assertion 6 models and cannot check (round 15, finding 2);
9. and that scan's own scope is total: a harness module that creates a file
   and is not in its list fails there rather than going unscanned.

Tests 4 and 6 are the only tests in the suite that run `git`. They are offline,
they run inside `fixtures.throwaway_root()` and write nothing into the
committed tree, and they need no git identity because only the index is ever
read — `git add` without a commit is enough for `git ls-files`. Tests 5 and 6
read the committed tree through `git ls-files`; test 6 copies it and writes
only inside its own throwaway root. Tests 8 and 9 read the harness sources
themselves, through `ast`, and run no git and no subprocess at all.
"""
from __future__ import annotations
import ast
import importlib
import json
import os
import re
import shutil
import subprocess
import symtable
import types

import arm_assembly
import batch
import fixtures
import flagtaint
import gatescan
import integrity
import records_compile
import redness
import score_rates


def _tracked(root: str) -> list:
    listing = subprocess.run(["git", "ls-files", "-z", "--", "."],
                             cwd=root, capture_output=True, check=True)
    return [name for name in listing.stdout.decode("utf-8").split("\0") if name]


def _write(root: str, relative: str, text: str) -> str:
    path = os.path.join(root, relative)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


def test_a_file_entry_excludes_exactly_that_path():
    for entry in ("RESULTS.json", "arms/BATCH.json") + integrity.MANIFEST_CARRIERS:
        assert integrity.manifest_excluded(entry, (entry,)) is True, entry
        under = entry + "/nested.txt"
        assert integrity.manifest_excluded(under, (entry,)) is False, under


def test_a_tree_entry_excludes_the_subtree(pins):
    registered = tuple(pins["freeze"]["excluded"])
    for name in ("arms/A/authoring/run-001/CALL.json",
                 "controls/recapture/attempt-1/x.json",
                 "controls/isolation-negative/attempt-1/x.json"):
        assert integrity.manifest_excluded(name, registered) is True, name
    # A tracked file AT the bare name is reviewed bytes: the entry names a
    # tree, and this path is not one. The asymmetry is the point.
    for name in ("arms/A/authoring", "controls/recapture",
                 "controls/isolation-negative"):
        assert integrity.manifest_excluded(name, registered) is False, name
    # And a tree entry does not reach a sibling it merely prefixes.
    assert integrity.manifest_excluded("arms/AA/authoring/x", registered) is False


def test_the_registered_exclusions_keep_their_registered_shape(pins):
    registered = tuple(pins["freeze"]["excluded"])
    files = {name for name in registered if not name.endswith("/")}
    trees = {name for name in registered if name.endswith("/")}
    assert files == {
        "RESULTS.json", "RATES.md", "CENSUS.md", "ANALYSIS.md",
        "DEVIATIONS.md", "CORRECTION.md", "arms/BATCH.json",
        # The ledger's atomic-write temporary, at `batch.LEDGER_TEMP_NAME` — a
        # FILE entry beside the ledger, so it adds no tree and the round-9
        # widening class is untouched (round 16, finding 3).
        "arms/BATCH.json.partial",
        "arms/SHORTFALL.json", "transcription/GOLDEN-CONTEXT.json"}
    assert trees == {
        "records/",
        "controls/recapture/", "controls/isolation-negative/",
        "arms/A/authoring/", "arms/B/authoring/", "arms/C/authoring/",
        "arms/D/authoring/", "arms/E/authoring/"}
    assert len(registered) == len(files) + len(trees)


def test_tree_manifest_honours_the_distinction(pins):
    registered = tuple(pins["freeze"]["excluded"])
    root = fixtures.throwaway_root()
    try:
        subprocess.run(["git", "init", "-q"], cwd=root, check=True,
                       capture_output=True)
        _write(root, "keep.txt", "reviewed\n")
        _write(root, "arms/BATCH.json", '{"registered": "exclusion"}\n')
        _write(root, "controls/recapture/attempt-1/x.txt", "a control run\n")
        nested = _write(root, "RESULTS.json/nested.txt", "tracked, unlisted\n")
        subprocess.run(["git", "add", "-A", "-f"], cwd=root, check=True,
                       capture_output=True)
        assert sorted(_tracked(root)) == [
            "RESULTS.json/nested.txt", "arms/BATCH.json",
            "controls/recapture/attempt-1/x.txt", "keep.txt"]

        base = integrity.tree_manifest(root, registered)

        # The registered exclusions still bite: an output file and a control
        # tree can move without moving the manifest.
        _write(root, "arms/BATCH.json", '{"registered": "and rewritten"}\n')
        _write(root, "controls/recapture/attempt-1/x.txt", "rewritten\n")
        assert integrity.tree_manifest(root, registered) == base

        # The descendant of a FILE-shaped entry is reviewed bytes, so it is
        # inside the manifest and its bytes move the digest. Under the round-9
        # prefix reading this assertion fails.
        _write(root, "RESULTS.json/nested.txt", "rewritten\n")
        assert integrity.tree_manifest(root, registered) != base
        _write(root, "RESULTS.json/nested.txt", "tracked, unlisted\n")
        assert integrity.tree_manifest(root, registered) == base

        # Removing it from the index moves the digest for the same reason.
        os.unlink(nested)
        subprocess.run(["git", "add", "-A", "-f"], cwd=root, check=True,
                       capture_output=True)
        assert "RESULTS.json/nested.txt" not in _tracked(root)
        assert integrity.tree_manifest(root, registered) != base

        # And the fixture is live: an ordinary tracked file moves it too.
        _write(root, "keep.txt", "reviewed, and edited\n")
        assert integrity.tree_manifest(root, registered) != base
    finally:
        shutil.rmtree(root, True)


def _stage(root: str) -> None:
    """The index is what `tree_manifest()` reads, and the real ceremony commits
    every file it writes, so each act is staged before the digest is taken."""
    subprocess.run(["git", "add", "-A", "-f"], cwd=root, check=True,
                   capture_output=True)


def _registry_edit(root: str, section: str, member: str, value) -> None:
    with open(os.path.join(root, "harness", "PINS.json")) as handle:
        pins = json.load(handle)
    pins[section][member] = value
    with open(os.path.join(root, "harness", "PINS.json"), "w") as handle:
        json.dump(pins, handle, indent=2)


RECORDS_FLAG = re.compile(r"score_rates\.py score --emit-records (\S+)")


def registered_records_dir(study: str) -> str:
    """The emission destination README step 7 actually registers, read out of
    the README rather than restated here (round 14, finding 1). A stand-in
    would let this file assert a lifecycle the ceremony does not run."""
    with open(os.path.join(study, "README.md"), encoding="utf-8") as handle:
        found = RECORDS_FLAG.findall(handle.read())
    assert len(found) == 1, ("README registers %d emission destinations"
                             % len(found))
    return found[0].rstrip("/")


def test_the_registered_record_destination_is_an_excluded_tree(study, pins):
    """§8 requires the compiled record trees published, and README step 7 emits
    them INSIDE the study tree, where `git ls-files` sees them. The destination
    therefore has to be a registered exclusion, or the publication act moves the
    digest the final round attested (round 14, finding 1). Read from the
    README, so changing the flag's value without changing `freeze.excluded`
    fails here."""
    destination = registered_records_dir(study)
    registered = tuple(pins["freeze"]["excluded"])
    assert destination + "/" in registered, (
        "README emits records into %r, which harness/PINS.json does not exclude"
        % destination)
    for name in ("%s/A/run-001/RECORDS.md" % destination,
                 "%s/A/run-001/records/CASE-001.json" % destination):
        assert integrity.manifest_excluded(name, registered) is True, name


def test_the_manifest_is_identical_after_every_registered_lifecycle_act(study,
                                                                        pins):
    """§2.10 rule 3 terminates only if no registered act moves a covered byte,
    and that is a property of the tree rather than a sentence about it.

    Rule 3 answers any covered-byte change with another review round. So if any
    act between the final round and publication — recording a round, the freeze
    itself, the golden recapture, §6 C7, the batch, the scoring, the
    publication — moved one covered byte, the study could never be frozen: the
    round that attested the tree would be invalidated by the next registered
    step, and the round attesting THAT step would be invalidated in turn. Round
    13 found one instance of this livelock (a review-round count copied into
    `README.md`) and closed it by hand.

    This is the same property asserted mechanically, over the committed file
    list rather than over a phrase list: every registered act is applied to a
    throwaway copy of the tree and the manifest is required to be identical
    after each. It is the positive half of the remedy — the lint in
    `test_review_status.py` is the negative half, and a phrase list cannot be
    complete. What this case adds is that the acts as MODELLED here move no
    covered byte. It models them; it does not run them, so an output a writer
    grows without an entry in `freeze.excluded` is caught by
    `test_every_study_destination_a_writer_names_is_an_excluded_path` below,
    which reads the destinations out of the writers, and not by this case
    (round 15, finding 2).

    It is necessary and not sufficient. A covered file that asserts a lifecycle
    status stays false-after-the-act without moving any digest here, because
    the digest is over bytes and the defect is in what the bytes say.
    """
    registered = tuple(pins["freeze"]["excluded"])
    root = fixtures.throwaway_root()
    try:
        for name in _tracked(study):
            source = os.path.join(study, name)
            if not os.path.isfile(source) or os.path.islink(source):
                continue
            target = os.path.join(root, name)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copyfile(source, target)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True,
                       capture_output=True)
        _stage(root)
        base = integrity.tree_manifest(root, registered)

        def record_a_review_round():
            with open(os.path.join(root, "PREREG-REVIEW.md"), "a",
                      encoding="utf-8") as handle:
                handle.write("\n## Round 99 — a stand-in heading\n")

        def freeze():
            # Both pins together or integrity refuses (§2.10, round 4 finding
            # 1). Both are nulled by the normalized projection.
            _registry_edit(root, "freeze", "preregistrationSha256",
                           "sha256:" + "1" * 64)
            _registry_edit(root, "freeze", "treeManifestSha256", base)

        def recapture_the_golden():
            _write(root, "transcription/GOLDEN-CONTEXT.json",
                   '{"a": "recaptured context"}\n')
            _write(root, "controls/recapture/attempt-1/CALL.json", "{}\n")
            _registry_edit(root, "golden", "sha256", "sha256:" + "2" * 64)

        def run_the_isolation_negative():
            _write(root, "controls/isolation-negative/VERDICT.json",
                   '{"outcome": "refused"}\n')
            _registry_edit(root, "isolationNegative", "assent", "granted")

        def run_the_batch():
            for arm in ("A", "B", "C", "D", "E"):
                slot = "arms/%s/authoring/run-001" % arm
                _write(root, slot + "/CALL.json", "{}\n")
                _write(root, slot + "/records.json", "[]\n")
            _write(root, "arms/BATCH.json", "[]\n")
            _write(root, "arms/SHORTFALL.json", "{}\n")

        def score_and_publish():
            for name in ("RESULTS.json", "RATES.md", "CENSUS.md",
                         "ANALYSIS.md", "DEVIATIONS.md", "CORRECTION.md"):
                _write(root, name, "the run's output\n")
            # `score --emit-records <dest>`, at the destination README step 7
            # registers and in the layout `_emit_records()` writes:
            # <dest>/<arm>/<slot>/ with the compiler's own RECORDS.md and
            # records/<case>.json beneath it. §8 requires these published, so
            # they are committed with everything else (round 14, finding 1).
            destination = registered_records_dir(study)
            for arm in ("A", "B", "C", "D", "E"):
                slot = "%s/%s/run-001" % (destination, arm)
                _write(root, slot + "/RECORDS.md", "| case | outcome |\n")
                _write(root, slot + "/records/CASE-001.json", "{}\n")

        for act in (record_a_review_round, freeze, recapture_the_golden,
                    run_the_isolation_negative, run_the_batch,
                    score_and_publish):
            act()
            _stage(root)
            assert integrity.tree_manifest(root, registered) == base, (
                "%s moved the tree manifest: §2.10 rule 3 answers a "
                "covered-byte change with another review round, whose own "
                "subject this act would break again" % act.__name__)

        # And the fixture is live: an output this study has NOT registered as
        # an exclusion is reviewed bytes, and moves the digest.
        _write(root, "SUMMARY.md", "an output with no exclusion entry\n")
        _stage(root)
        assert integrity.tree_manifest(root, registered) != base
    finally:
        shutil.rmtree(root, True)


def test_no_tracked_path_hides_under_a_file_entry(study, pins):
    """Why the corrected rule cannot move THIS tree's manifest: nothing tracked
    today sits under any file-shaped exclusion, so the two readings agree on
    every one of the study's tracked paths (round 9, finding 5)."""
    members = tuple(pins["freeze"]["excluded"]) + integrity.MANIFEST_CARRIERS
    files = [name for name in members if not name.endswith("/")]
    assert len(files) == 12
    hidden = [(name, entry) for entry in files for name in _tracked(study)
              if name.startswith(entry + "/")]
    assert hidden == []


# --- the writers' own destinations (round 15, finding 2) ---------------------

# The primitives that CREATE A FILE, and the argument each names it with.
# Directory creation is deliberately absent: a directory is not a tracked file
# and never enters the manifest.
FILE_WRITERS = {
    "open": 0, "os.open": 0, "os.rename": 1, "os.replace": 1,
    "os.symlink": 1, "os.link": 1,
    "shutil.copyfile": 1, "shutil.copy": 1, "shutil.copy2": 1,
    "shutil.copytree": 1, "shutil.move": 1,
    "_write_json": 0, "_write_json_atomic": 0,
}

# Round 16, finding 3: the scan's vocabulary is FINITE, and until this round it
# skipped anything outside it in silence — so `tempfile.mkstemp()` writing a
# study path was invisible while the docstring below said the scan fails closed.
# It fails closed now: a call to `open` or into one of these namespaces must be
# a known creator or a known non-creator, and a third thing is an OFFENDER that
# says "classify this call".
FS_NAMESPACES = ("os", "shutil", "tempfile", "pathlib", "io")

# The calls in those namespaces that create no FILE. `os.path.*` is exempt by
# rule rather than by list — it computes and inspects paths and creates
# nothing — and directory creation is here for the reason above.
NON_CREATING = {
    "os.close", "os.fdopen", "os.fsync", "os.getpid", "os.listdir",
    "os.lstat", "os.makedirs", "os.stat", "os.unlink", "os.walk",
    "shutil.rmtree", "io.StringIO", "tempfile.TemporaryDirectory",
}

# Namespaces whose members must be reached through the namespace, so that
# `_dotted()`'s spelling match cannot be defeated by a rebinding. `import
# subprocess as _subprocess` at batch.py:224 shows aliasing is house style, so
# the assumption is enforced rather than assumed.
IMPORT_DISCIPLINE = FS_NAMESPACES

# Every executable that writes anything, and nothing else is scanned — a module
# added here is scanned, and a module that starts writing and is not here is
# caught by `test_every_writing_module_is_scanned` below.
WRITING_MODULES = (score_rates, batch, records_compile, arm_assembly)

# Why a parameter root is not covered bytes — a CLASSIFICATION and not only a
# sentence (round 17, finding 1). The old table held prose, and prose is where
# the defect hid: `("score_rates", "_emit_records", "out_dir")`'s reason was
# three true clauses that did not compose into their conclusion. It said
# `_check_records_target()` required the target outside the population, that
# README step 7 names `records`, and that a test binds THAT NAME to an excluded
# tree — all true, and all about one VALUE of a flag registered with a free
# parameter. `--emit-records analysis/records` was accepted.
#
#   "runtime-gated"        the destination is the OPERATOR's to choose, and the
#                          harness refuses an unlawful one at run time. Such a
#                          root must carry a behavioural pair in
#                          `LAWFUL_DESTINATION_PROBES` below — the canonical
#                          value admitted, an in-study sibling the exclusion
#                          list does not cover refused BY NAME. A sentence is
#                          not enough for this class, because a sentence is
#                          exactly what was here before.
#   "constant-derived"     the caller's value is resolved to a module constant
#                          at every call site, and checked there like any other
#                          destination.
#   "not-a-registered-act" the writer is reachable, but not as a step of the
#                          registered ceremony.
#   "lawfully-covered"     it writes covered bytes, and is registered to.
#
# A classification outside this tuple fails, and so does a bare reason with no
# classification, so a new parameter root cannot arrive with only a sentence.
ROOT_CLASSIFICATIONS = ("runtime-gated", "constant-derived",
                        "not-a-registered-act", "lawfully-covered")

# A destination root that is a PARAMETER is the caller's value, and this scan
# does not follow it there. Each one is classified here, once, with the reason
# it is not covered bytes; a parameter root that is not in this table FAILS, so
# a new writer cannot be added without an entry.
PARAMETER_ROOTS = {
    ("batch", "_write_json", "path"): (
        "constant-derived",
        "the atomic-write primitives are themselves in FILE_WRITERS, so every "
        "CALL SITE's destination is resolved and checked above and their own "
        "bodies name no destination a caller does not. Round 16, finding 3: "
        "this replaces a blanket skip of both bodies, whose stated reason — "
        "\"their bodies are that primitive's implementation, not destinations "
        "of their own\" — was FALSE of `_write_json_atomic`, which used to "
        "name a `mkstemp` sibling no caller named."),
    ("batch", "_write_json_atomic", "path"): (
        "constant-derived", "the same primitive, resolved at its call sites."),
    ("batch", "_write_json_atomic", "temp_path"): (
        "constant-derived",
        "the ledger's atomic-write temporary, passed in as "
        "`batch.LEDGER_TEMP_NAME` from `write_ledger()`, where this scan "
        "resolves and checks it like any other destination."),
    ("score_rates", "_emit_records", "out_dir"): (
        "runtime-gated",
        "the `--emit-records DIR` target, and the operator's to name. "
        "`_check_records_target()` requires it outside the POPULATION and — "
        "round 17, finding 1 — `require_lawful_destination()` requires it "
        "outside the STUDY or wholly inside a registered `freeze.excluded` "
        "tree, which is the other half of the same §2.10 rule. Driven both "
        "ways by `test_every_runtime_gated_destination_refuses_an_unlawful_"
        "one`, THROUGH `score_registered()` — the function `main()` dispatches "
        "to — since round 18, finding 2: the pair used to call "
        "`_check_records_target()` itself, so the one line that wires the "
        "whole rule into the registered command could be deleted with the "
        "pinned suite at 315 passed. README step 7's literal is no longer what "
        "carries this row."),
    ("batch", "stamp_slot", "slot"): (
        "constant-derived",
        "a slot of the registered order, always `arms/<ARM>/authoring/run-NNN` "
        "(`slot_path()`), which is an excluded tree."),
    ("batch", "refuse_slot", "slot"): (
        "constant-derived",
        "two callers, and the reason has to answer for both — round 18, "
        "finding 1, where this entry said \"the same slot root, handed in by "
        "`run_batch()` from `slot_path()`\" and named ONE of them. "
        "`run_batch()` (batch.py:1816) hands a slot of the registered order, "
        "an excluded tree. `run_capture()` (batch.py:2069) hands a capture "
        "slot built from `--captures`, which is the OPERATOR's directory and "
        "not a constant at all; that path is why `REFUSAL.json` under an "
        "in-study `--captures` was a covered byte this table declared could "
        "not exist. It is constant-derived now because the flag itself is "
        "gated at `run_capture()`'s own entry and registered in "
        "`OPERATOR_DESTINATIONS`, which is where a caller-supplied root "
        "belongs."),
    ("batch", "seal_slot", "slot"): (
        "constant-derived",
        "the same slot root, from the same expansion of the same order."),
    ("batch", "capture_golden", "out_path"): (
        "runtime-gated",
        "the golden capture. Its default is `DEFAULT_GOLDEN` = "
        "`transcription/GOLDEN-CONTEXT.json`, an excluded file, but `--out` "
        "takes any path and README step 5's \"leave `--out` at its default\" "
        "was prose and not a check until round 17, finding 1. "
        "`require_lawful_destination()` is the check now, and the pair below "
        "drives it."),
    ("batch", "capture_isolation_negative", "out_dir"): (
        "runtime-gated",
        "§6 C7's record. Its default is `DEFAULT_NEGATIVE` = "
        "`controls/isolation-negative/`, an excluded tree, and `--out` took "
        "any path on the same prose alone. Gated and driven the same way."),
    ("records_compile", "cmd_compile", "out_root"): (
        "not-a-registered-act",
        "the compiler's CLI output root. It is not a step of the registered "
        "ceremony — the scoring uses this module as a LIBRARY "
        "(`compiled_files()`) and writes through `_emit_records()` above — and "
        "the file is a byte-identical port (`PORTS.md`: \"none — taken "
        "unchanged\"), so gating it would break that row for a CLI the "
        "ceremony never runs."),
    ("arm_assembly", "build", "root"): (
        "lawfully-covered",
        "the arms root. This writer is the only one that writes COVERED bytes, "
        "lawfully: assembling `arms/<X>/{POLICY.md,PROMPT.txt,FAMILY.json,"
        "ARM.json}` is a pre-registration act, and it refuses to overwrite "
        "bytes that differ, so it is byte-idempotent after the freeze."),
}

# The fragment of `score_rates.require_lawful_destination()`'s refusal that
# identifies it, and no other refusal in either module.
LAWFUL_DESTINATION_NEEDLE = "which harness/PINS.json does not exclude"


def _dotted(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted(node.value)
        return None if base is None else base + "." + node.attr
    return None


class Unclassified(Exception):
    """A call this scan cannot decide about. Raised, never swallowed: the
    docstring below claims the scan fails CLOSED, and round 16 found three
    independent ways it failed OPEN."""


def _flag_names(node) -> list:
    """Every `os.O_*` constant in a flags expression (`os.O_WRONLY |
    os.O_CREAT`), or `Unclassified` if the expression holds ANYTHING else —
    including a name whose value this scan cannot see.

    Round 17, finding 4: the old form asked only whether the expression was a
    dotted name, so `os.open(path, flags)` with a parameter and `os.open(path,
    _CREATE)` with a module constant both resolved — to `["flags"]` and
    `["_CREATE"]` — tested false for `O_CREAT`, and were dropped as
    non-creating. That is the same fail-open dressed as a limitation that round
    16 removed from `open()`'s mode, left in place one function away, and the
    docstring below claimed the opposite in terms. The `os.O_` prefix is the
    whole repair: it turns "is this a name?" into "is this a flag constant
    whose value I can read?"."""
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.BitOr, ast.Add)):
        return _flag_names(node.left) + _flag_names(node.right)
    name = _dotted(node)
    if name is None or not name.startswith("os.O_"):
        raise Unclassified(
            "os.open() flags are not a readable set of `os.O_*` constants, so "
            "whether this call creates a file cannot be read from the source")
    return [name.rsplit(".", 1)[-1]]


def _creates(call) -> bool:
    """Whether a known primitive creates a file at this call site.

    `open()` creates in a writing mode; `os.open()` creates with `O_CREAT`;
    every other member of `FILE_WRITERS` always does. Round 16, finding 3: a
    mode or a flag set the scan cannot READ raises rather than returning False.
    The old form classified `open(path, mode)` with a variable mode as
    NON-creating, which is a fail-open dressed as a limitation."""
    name = _dotted(call.func)
    if name == "os.open":
        if len(call.args) < 2:
            raise Unclassified("os.open() without flags")
        return "O_CREAT" in _flag_names(call.args[1])
    if name != "open":
        return True
    mode = None
    if len(call.args) > 1:
        mode = call.args[1]
    for keyword in call.keywords:
        if keyword.arg == "mode":
            mode = keyword.value
    if mode is None:
        return False                       # the default is "r"
    if not isinstance(mode, ast.Constant) or not isinstance(mode.value, str):
        raise Unclassified("open() mode is not a literal, so whether this call "
                           "creates a file cannot be read from the source")
    return any(letter in mode.value for letter in "wax+")


def _classify(call) -> str:
    """A call is a creator, is non-creating, or is `Unclassified` — the
    fail-closed half.

    Anything named `open` or reached through one of `FS_NAMESPACES` has to be
    one of the two. A new filesystem API therefore arrives as a failure that
    says which call to classify, instead of as a destination nobody sees.

    Round 17, finding 4: a COMPUTED callee is the third spelling of the same
    fail-open. `_dotted()` returns None for `getattr(os, 'replace')(…)`, for
    `(os.replace if flag else os.rename)(…)` and for `os.__dict__['replace'](…)`,
    and the tail of this function then classified all three as non-creating.
    The guard on the callee's own SHAPE is load-bearing: raising on every
    callee `_dotted()` cannot read false-positives on ordinary method chaining
    off a call result (`open(p).read()`, `os.path.normpath(x).startswith(…)`),
    which is six real sites across three harness modules. A callee that is
    itself a call, a conditional or a subscript is the actual attack shape."""
    if isinstance(call.func, (ast.Call, ast.IfExp, ast.Subscript)):
        touched = sorted({name for item in ast.walk(call.func)
                          for name in [_dotted(item)]
                          if name is not None
                          and (name in FILE_WRITERS
                               or name.split(".")[0] in FS_NAMESPACES)})
        if touched:
            raise Unclassified(
                "the callee is COMPUTED and mentions %r: a filesystem "
                "primitive reached other than by its dotted name cannot be "
                "classified" % (touched,))
    name = _dotted(call.func)
    if name in FILE_WRITERS:
        return "creator"
    if name in NON_CREATING:
        return "non-creating"
    if name is not None and name.startswith("os.path."):
        # `os.path` computes and inspects paths; it creates no entry.
        return "non-creating"
    if name == "open" or (name is not None
                          and name.split(".")[0] in FS_NAMESPACES):
        raise Unclassified(
            "%s is a filesystem call this scan does not classify: put it in "
            "FILE_WRITERS with the argument that names its destination, or in "
            "NON_CREATING" % name)
    return "non-creating"


def _vocabulary() -> set:
    """Every name this scan reads as a filesystem name, derived from the
    scan's own tables — so a new entry in `FILE_WRITERS` extends the discipline
    below with no second edit."""
    return ({"open"} | set(FS_NAMESPACES) | set(IMPORT_DISCIPLINE)
            | {key.split(".")[0] for key in FILE_WRITERS}
            | {key.split(".")[0] for key in NON_CREATING})


def _binding_lines(tree: ast.Module, name: str) -> list:
    """The lines at which a name appears in a BINDING position, for reporting.

    `symtable` decides what a binding IS; it has no line numbers, so the line
    is located here. The rule is the AST's own shape and not a list of
    statements: an identifier field holding this name, on a node that either
    has no `ctx` at all (`alias.asname`, `arg.arg`, a `def`'s or an `except
    … as`'s or a `match` capture's `name`) or whose `ctx` is not `Load`. String
    CONSTANTS are excluded, because a message mentioning `open` is not a
    binding of it."""
    lines = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant):
            continue
        context = getattr(node, "ctx", None)
        if context is not None and isinstance(context, ast.Load):
            continue
        for _field, value in ast.iter_fields(node):
            if value == name and getattr(node, "lineno", None) is not None:
                lines.append(node.lineno)
                break
    return sorted(lines)


def binding_offenders(module_name: str, source: str, tree: ast.Module) -> list:
    """RULE 1: no name in the scan's vocabulary may be BOUND, except by
    `import <module>` at module level and by the module-level `def` of a
    writer this scan knows.

    WHICH NAMES A MODULE BINDS IS CPYTHON'S QUESTION, NOT THIS FILE'S.
    `symtable` is the compiler's own front end, so the set is exhaustive by
    construction in the way a list of statement types is not.

    Round 18, finding 4 is why it is written this way. The function that used
    to stand here said it read "every statement that BINDS a name" and then
    glossed the universal with a seven-item list, and the docstring below said
    a primitive could not be reached under a second name "not by any other
    binding form". Measured false in twelve spellings: tuple, list and starred
    `for` targets; tuple `with` targets; `except … as`; comprehension targets;
    the three `match` capture forms; every parameter form; a NON-filesystem
    `import json as open`; and a PEP 695 `type` alias. The reviewer's own
    proposed repair — walking `ast.Name` in `Store` context — finds 15 of 35
    declared names on a probe source and would have re-recorded the same
    universal, so it is not what is here.

    Confining the sanctioned set to the MODULE scope is load-bearing: it is
    what makes `def f(os)` in an os-importing module an offender."""
    vocabulary = _vocabulary()
    sanctioned = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname is None and "." not in alias.name \
                        and alias.name in vocabulary:
                    sanctioned.add(alias.name)
        if isinstance(node, ast.FunctionDef) and node.name in FILE_WRITERS:
            sanctioned.add(node.name)      # `_write_json`, `_write_json_atomic`
    offenders = []

    def visit(table, path):
        for symbol in table.get_symbols():
            name = symbol.get_name()
            if name not in vocabulary:
                continue
            # THREE PREDICATES, and all three are load-bearing. `is_assigned()`
            # alone is what a reader assumes and it is FALSE of an import —
            # measured: `import os` reports assigned False and imported True,
            # so a rule written on assignment alone would have let `import json
            # as open` past while looking exhaustive.
            if not (symbol.is_assigned() or symbol.is_parameter()
                    or symbol.is_imported()):
                continue
            if path == "<module>" and name in sanctioned:
                continue
            floor = 0 if path == "<module>" else table.get_lineno()
            found = [line for line in _binding_lines(tree, name)
                     if line >= floor]
            offenders.append(
                "%s.py:%d binds the filesystem name `%s` in scope %s. The "
                "writer scan matches filesystem calls by their dotted "
                "spelling, so a second name for one defeats it: the only "
                "bindings this discipline allows are `import %s` at module "
                "level and this module's own definition of a writer the scan "
                "knows"
                % (module_name, found[0] if found else table.get_lineno(),
                   name, path, name))
        for child in table.get_children():
            visit(child, "%s.%s" % (path, child.get_name()))

    visit(symtable.symtable(source, module_name + ".py", "exec"), "<module>")
    return offenders


def escape_offenders(module_name: str, tree: ast.Module) -> list:
    """RULE 2: a filesystem primitive may be CALLED, and not otherwise used.

    Every mention of a vocabulary name that is not a callee and not a link in a
    longer dotted chain is a VALUE use — the primitive escaping as an object,
    which is how it acquires a second name without a binding statement anywhere
    in this module: `functools.partial(os.replace, …)`, a dispatch dict, a
    parameter default, a `return os.replace`.

    The classifier is `callable()` against the resolved object, not a list.
    That is what separates `os.sep`, `os.O_CREAT` and `os.environ` — which are
    data and pass — from `os.replace`, `shutil.copy` and `os` itself. A name
    outside `FS_NAMESPACES` that is in the vocabulary at all is a writer by
    construction (`open`, `_write_json`, `_write_json_atomic`), and a chain
    that will not resolve is an offender, because a fail-closed scan may not
    treat "I could not look this up" as "it is fine".

    Rule 2 subsumes the alias half of the old import discipline: it does not
    matter which statement form bound the second name, because the primitive
    has to LEAVE the callee position to be bound at all."""
    vocabulary = _vocabulary()
    called, chained = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            called.add(id(node.func))
        if isinstance(node, ast.Attribute):
            chained.add(id(node.value))
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if not isinstance(node.ctx, ast.Load):
                continue
        elif not isinstance(node, ast.Attribute):
            continue
        name = _dotted(node)
        if name is None or name.split(".")[0] not in vocabulary:
            continue
        if id(node) in called or id(node) in chained:
            continue
        why = None
        root = name.split(".")[0]
        if root not in FS_NAMESPACES:
            why = "a writer of this scan's own vocabulary"
        else:
            try:
                value = importlib.import_module(root)
                for part in name.split(".")[1:]:
                    value = getattr(value, part)
            except (ImportError, AttributeError):
                why = "a filesystem name this scan cannot resolve"
            else:
                if callable(value) or isinstance(value, types.ModuleType):
                    why = ("a filesystem module" if isinstance(
                        value, types.ModuleType) else "a filesystem primitive")
        if why is None:
            continue                       # data: `os.sep`, `os.O_*`, `os.environ`
        offenders.append(
            "%s.py:%d uses `%s` as a VALUE and not as a callee, and it is %s. "
            "The writer scan matches filesystem calls by their dotted "
            "spelling, so a primitive that escapes as an object is reachable "
            "under a name this scan cannot see: call it through its module"
            % (module_name, node.lineno, name, why))
    return offenders


def import_offenders(module_name: str, tree: ast.Module) -> list:
    """RULE 3: the two spellings in which a primitive never appears dotted at
    all, and which rules 1 and 2 therefore structurally cannot see.

    `from tempfile import mkstemp` binds `mkstemp`, which is not in the
    vocabulary and never will be — the vocabulary is roots. `import tempfile as
    t` binds `t`, likewise. Both defeat `_dotted()`'s spelling match, and both
    are caught here by the IMPORT rather than by the name it produces."""
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) \
                and (node.module or "").split(".")[0] in IMPORT_DISCIPLINE:
            offenders.append(
                "%s.py:%d imports names out of %r. The writer scan matches "
                "filesystem calls by their dotted spelling, so a bare name "
                "defeats it: reach them through the module"
                % (module_name, node.lineno, node.module))
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in IMPORT_DISCIPLINE and alias.asname:
                    offenders.append(
                        "%s.py:%d imports %s as %s. The writer scan matches "
                        "filesystem calls by their dotted spelling, so an "
                        "alias defeats it"
                        % (module_name, node.lineno, alias.name, alias.asname))
    return offenders


def _scope_calls(tree: ast.Module) -> list:
    """[(scope name, scope node, call)] for EVERY call in a module, each in the
    nearest function that encloses it.

    Round 16, finding 3: the old collection walked `ast.FunctionDef` only, so a
    write at module level, in a class body, in a lambda or in an async function
    was never visited — and, because `ast.walk()` yields nested definitions
    too, a write inside a nested function was visited twice. This is a
    partition: every call is attributed once, and `"<module>"` is a scope like
    any other."""
    found = []

    def descend(node, scope_name, scope_node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef,
                                  ast.Lambda)):
                descend(child, getattr(child, "name", "<lambda>"), child)
                continue
            if isinstance(child, ast.Call):
                found.append((scope_name, scope_node, child))
            descend(child, scope_name, scope_node)

    descend(tree, "<module>", tree)
    return found


def _resolve(node, assignments, depth=0, seen=frozenset()):
    """(root symbol, [tail parts]) for a destination expression.

    Resolved through the writer's own module only: `os.path.join`, string
    literals, and a local name's single in-function assignment. A name already
    being expanded is not expanded again (`root = root or <default>` rebinds a
    parameter to itself), and anything else returns a root the caller cannot
    classify — which is a failure and never a skip."""
    if depth > 8:
        return ("<too-deep>", [])
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return ("<literal>", [node.value])
    if isinstance(node, ast.Name):
        if node.id in assignments and node.id not in seen:
            return _resolve(assignments[node.id], assignments, depth + 1,
                            seen | {node.id})
        return (node.id, [])
    if isinstance(node, ast.BoolOp):
        # `root or <default>`: the caller's value wins, so the parameter is the
        # root and the default is not a second destination.
        return _resolve(node.values[0], assignments, depth + 1, seen)
    if isinstance(node, ast.Call):
        name = _dotted(node.func)
        if name in ("os.path.realpath", "os.path.abspath", "os.path.normpath"):
            return _resolve(node.args[0], assignments, depth + 1, seen)
        if name == "os.path.join":
            root, tail = _resolve(node.args[0], assignments, depth + 1, seen)
            for extra in node.args[1:]:
                part_root, part_tail = _resolve(extra, assignments, depth + 1,
                                                seen)
                tail = tail + (part_tail if part_root == "<literal>"
                               else ["<%s>" % part_root])
            return (root, tail)
        return ("<call:%s>" % name, [])
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        # `"run-%03d" % index`: the literal's fixed head is all a reader of the
        # source knows, and the substituted tail is marked as unresolved.
        root, tail = _resolve(node.left, assignments, depth + 1, seen)
        if root == "<literal>":
            return ("<literal>", [tail[0].split("%")[0] + "<format>"])
        return (root, tail + ["<format>"])
    return ("<%s>" % type(node).__name__, [])


def scan_source(module_name: str, source: str) -> tuple:
    """(write sites, offenders) for one module's source text.

    Sites are `(line, scope, root symbol, [tail parts])` for every
    file-creating write. Offenders are the calls this scan cannot classify,
    the modes and flag sets it cannot read, and the import spellings that would
    defeat it — everything that used to be a silent skip.

    Takes SOURCE rather than a module so that
    `test_the_writer_scan_fails_closed_on_what_it_cannot_read` can splice a
    write into a copy and require it to be caught."""
    tree = ast.parse(source)
    offenders = (import_offenders(module_name, tree)
                 + binding_offenders(module_name, source, tree)
                 + escape_offenders(module_name, tree))
    sites = []
    for scope_name, scope_node, node in _scope_calls(tree):
        try:
            kind = _classify(node)
            if kind != "creator" or not _creates(node):
                continue
        except Unclassified as why:
            offenders.append("%s.py:%d %s(): %s"
                             % (module_name, node.lineno, scope_name, why))
            continue
        assignments = {}
        for inner in ast.walk(scope_node):
            if isinstance(inner, ast.Assign) and len(inner.targets) == 1 \
                    and isinstance(inner.targets[0], ast.Name):
                assignments.setdefault(inner.targets[0].id, inner.value)
        index = FILE_WRITERS[_dotted(node.func)]
        if len(node.args) <= index:
            sites.append((node.lineno, scope_name, "<no-argument>", []))
            continue
        root, tail = _resolve(node.args[index], assignments)
        sites.append((node.lineno, scope_name, root, tail))
    return sorted(sites), offenders


def write_sites(module) -> list:
    """[(line, scope, root symbol, [tail parts])] for every file-creating write
    in a writing module, read out of its own source."""
    with open(module.__file__, encoding="utf-8") as handle:
        return scan_source(module.__name__, handle.read())[0]


def _module_string(module, name):
    value = getattr(module, name, None)
    return value if isinstance(value, str) else None


def test_every_study_destination_a_writer_names_is_an_excluded_path(study, pins):
    """The writers' own destinations, derived from their source rather than
    restated here (round 15, finding 2).

    The lifecycle case above applies each registered act by HAND — it writes
    the names the ceremony's writers write. That is an assertion about a list
    THIS file keeps, so a writer that grew a fourth study-root output would
    leave it green while the publication moved the attested manifest. This case
    is the coupling the other one cannot be: every file-creating write in the
    writing modules is read out of their AST, its destination is resolved as
    far as the writer's own module resolves it, and every destination that
    lands inside the study tree must be `manifest_excluded()`.

    What it does not do, said rather than implied.

      * It READS; it does not RUN. It binds the destinations the writers NAME,
        not the files they produce — `_write_outputs()` publishes only for a
        scoring that computed the committed registry's digest itself and
        re-derives the whole result from the committed arms tree, so no fixture
        can reach it and none should be able to (§2.10, §7).
      * IT DOES NOT FOLLOW A PARAMETER TO ITS CALLERS, and that IS the
        permanent residual here. This bullet said "it is not any more" for one
        round and was wrong: what the round-17 repair added was a
        classification per root in `PARAMETER_ROOTS` and a run-time gate at
        three call sites chosen by hand, and neither is this scan following a
        parameter anywhere. `--captures` proved the difference — a fourth
        operator-named destination, classified by nothing, gated by nothing,
        and invisible here because the only file written under it is written by
        `refuse_slot()`, whose root this same table had already declared
        "constant-derived" on the strength of ONE of its two callers (round 18,
        finding 1).
        What follows the parameter is a different derivation, and it is named
        rather than implied: `test_every_operator_named_destination_is_
        registered_and_gated` propagates each command-line flag's value forward
        through the writers' own source to every write, so the roots the
        OPERATOR supplies are computed instead of listed, and each is gated at
        run time by `score_rates.require_lawful_destination()` — outside the
        study, or wholly inside a registered exclusion tree — with a
        behavioural pair per destination in
        `test_every_runtime_gated_destination_refuses_an_unlawful_one`. What is
        still true of THIS scan is that it reads a writer's own module and
        stops there.
      * It is Python-only. `transcription/authoring_call.sh` writes into
        `$SLOT`, an excluded tree, and into the scratch parent outside the
        study; that is named here rather than parsed.
      * It fails CLOSED on anything it cannot resolve OR cannot classify: an
        unresolvable destination, an `open()` whose mode is not a literal, an
        `os.open()` whose flag set is not a readable expression of `os.O_*`
        constants, a COMPUTED callee that mentions a filesystem name, and a
        filesystem call outside `FILE_WRITERS` and `NON_CREATING` are each an
        offender that names the line — and so are the two rules the alias half
        is written as: a name in the scan's vocabulary BOUND anywhere except by
        `import <module>` at module level, and a filesystem primitive USED as
        anything but a callee. Round 16, finding 3 is why that sentence is
        worded this way: it used to say the scan failed closed on anything it
        could not resolve and it failed OPEN in three independent ways — an
        unknown API was skipped, a variable `open()` mode was read as
        non-creating, and the whole bodies of
        `_write_json`/`_write_json_atomic` were skipped, which hid the one real
        unexcluded destination the study had. Round 17, finding 4 is why the
        sentence is worded this way TWICE: the round-16 form said "an
        `os.open()` whose flags are not readable" four lines below a function
        that read `os.open(path, flags)` as non-creating. Round 18, finding 4
        is why it no longer says "by any binding form": that was a universal
        over a seven-item list of statement types, measured false in twelve
        spellings, and the repair was to stop enumerating and ask CPython's own
        binder instead. THIRTEEN spellings are driven by `FAIL_CLOSED_SPLICES`,
        one per mechanism these rules turn on, and the case pins that count —
        so the list above is a set of driven properties and not one adjective.
      * The residual it does NOT close, stated rather than implied: the
        vocabulary is finite. A creator that is neither `open` nor a member of
        `FS_NAMESPACES` — a C extension, a vendored helper, a `subprocess` that
        shells out — is classified as non-creating and is invisible here. What
        bounds that is TWO RULES, and they are rules rather than a list of
        forms: a filesystem primitive may be CALLED and not otherwise used, and
        no name in the scan's vocabulary may be BOUND except by `import
        <module>` at module level. The first is `callable()` against the
        resolved object; the second is `symtable`, CPython's own binder, so
        what counts as a binding is not this file's to enumerate. Round 17,
        finding 4 bounded this residual by "the import discipline", which was
        false as written; round 18, finding 4 found the replacement false too —
        "not by any other binding form" was a universal glossing a seven-item
        list, and twelve spellings escaped it, four of them (parameters, a
        non-filesystem `import … as open`, starred `for` targets, PEP 695 type
        aliases) also missed by the finding that reported it. What the two
        rules still cannot see: a binding made at RUN time (`globals()["w"] =
        os.replace`, `setattr`, a module reached by a string through
        `importlib`), a callable handed in from OUTSIDE the module (`def
        f(writer, p): writer(p)` — the same parameter-to-callers residual named
        above), a creator that never enters the source as a name at all, and a
        filesystem OBJECT as distinct from a primitive: `p =
        pathlib.Path(root); p.write_text(x)` passes both rules, because the
        `Path` call is in callee position and the root `p` is not in
        `FS_NAMESPACES`. No harness module imports `pathlib` today, verified by
        the same `symtable` walk, and closing it means extending the
        fail-closed table to METHOD calls on filesystem-derived objects, which
        collides with the deliberate allowance for `open(p).read()` above. It
        is a discipline, not a proof; `WRITING_MODULES` is itself checked by
        `test_every_writing_module_is_scanned`, whose scope this widening
        extends: `census.py`, `integrity.py`, `policy_mirror.py` and
        `transcript_check.py` are bound by both rules there too, and all four
        are clean.

    What it does buy is that the classification is CHECKED against the code: an
    unresolvable destination, an unclassified root and an unclassified call all
    fail here, so a writer cannot quietly acquire a covered destination.
    """
    registered = tuple(pins["freeze"]["excluded"])
    study_root = os.path.realpath(study)
    offenders = []
    for module in WRITING_MODULES:
        name = module.__name__
        with open(module.__file__, encoding="utf-8") as handle:
            sites, unreadable = scan_source(name, handle.read())
        offenders.extend(unreadable)
        for line, function, root, tail in sites:
            anchor = _module_string(module, root)
            if anchor is None:
                key = (name, function, root)
                if key not in PARAMETER_ROOTS:
                    offenders.append(
                        "%s.py:%d %s() writes under %r, which is neither a "
                        "module path constant nor a classified parameter root: "
                        "add it to PARAMETER_ROOTS with the reason it is not "
                        "covered bytes, or give the writer a constant"
                        % (name, line, function, root))
                continue
            parts = [_module_string(module, part.strip("<>")) or part
                     for part in tail]
            if any(part.startswith("<") for part in parts):
                offenders.append(
                    "%s.py:%d %s() builds its destination from %r, which this "
                    "scan cannot resolve; a destination that is not statically "
                    "readable cannot be checked against freeze.excluded"
                    % (name, line, function, parts))
                continue
            destination = os.path.realpath(os.path.join(anchor, *parts))
            if destination != study_root \
                    and not destination.startswith(study_root + os.sep):
                continue                      # not a path inside the study tree
            relative = os.path.relpath(destination, study_root)
            if not integrity.manifest_excluded(relative, registered):
                offenders.append(
                    "%s.py:%d %s() writes %s, which harness/PINS.json does not "
                    "exclude: the act that writes it would move the manifest "
                    "the final round attested, and §2.10 rule 3 answers that "
                    "with another round (round 15, finding 2)"
                    % (name, line, function, relative))
    assert offenders == [], "\n".join(offenders)


def _refusal_of(call, module=None) -> str:
    """The refusal one drive produced, or "" — either exception type, because
    the destination rule lives in `score_rates` and three of its four call
    sites are in `batch`, so the operator meets it as a `ScoreError` once and
    as a `BatchError`-caught `ScoreError` three times. `main()` prints them the
    same way.

    A drive against a MUTANT module (round 18, finding 2) meets that module's
    OWN copies of those classes, which are different objects from the imported
    ones however identical their source. They are added by NAME against the
    types already caught, rather than by catching whatever the mutant raises:
    a redness case asserts a refusal is ABSENT, so a catch-all here would make
    it pass for the wrong reason."""
    kinds = (score_rates.ScoreError, batch.BatchError)
    if module is not None:
        named = {kind.__name__ for kind in kinds}
        kinds = kinds + tuple(
            value for value in vars(module).values()
            if isinstance(value, type) and issubclass(value, Exception)
            and value.__name__ in named)
    try:
        call()
    except kinds as refusal:
        return str(refusal)
    return ""


def _drive_emit_records(study: str, target: str, module=None) -> str:
    """`score --emit-records DIR`, through the REGISTERED INTERFACE.

    `score_registered()` is the function `main()` dispatches to, and it
    validates the destination before anything is scored or written, so the gate
    is met with nothing spent. `score()` is replaced for the length of the
    drive so that the lawful half cannot become a function of the study's stage
    (§2.10): pre-freeze it would stop at the golden pin, post-freeze it would
    score the real population and publish.

    Round 18, finding 2 is why it is written this way. It used to call
    `score_rates._check_records_target()` — an INTERMEDIATE — while its own
    docstring said "this drives the real entry point and not the predicate
    underneath it". Measured: deleting `score_registered()`'s call to that
    helper (score_rates.py:4711-4712) left `harness/integrity.py` at exit 0 and
    the whole pinned suite at 315 passed with 177 subtests, taking the
    lawful-destination rule AND the round-14 population rule out together. A
    probe bound below its entry is the round-16 shape one level up, and the
    entry a probe may bind to is derived rather than asserted — see
    `test_every_parameter_root_carries_a_classification_not_only_a_reason`."""
    module = module or score_rates

    def past_the_gate(*arguments, **keywords):
        raise module.ScoreError(
            "the drive reached score(): past the destination gate")

    spent, module.score = module.score, past_the_gate
    try:
        return _refusal_of(lambda: module.score_registered(target), module)
    finally:
        module.score = spent


def _drive_run_capture(study: str, target: str, module=None) -> str:
    """`capture --captures DIR`, through the entry `main()` dispatches to.

    `run_capture()` is the FOURTH operator-named destination (round 18,
    finding 1): its default is the excluded `controls/recapture/`, so the
    registered ceremony was lawful and the flag itself was checked by nothing.
    `preflight()` is replaced for the length of the drive, one statement below
    the gate and above `os.makedirs()`, so the ADMITTING half stops before the
    lawful destination is created and the case is the same at every stage of
    the study."""
    module = module or batch

    def past_the_gate(*arguments, **keywords):
        raise module.BatchError("the drive reached preflight(): past the "
                                "destination gate")

    spent, module.preflight = module.preflight, past_the_gate
    try:
        return _refusal_of(lambda: module.run_capture(
            module.MIN_CAPTURE_SLOTS, target,
            os.path.join(study, "no-such-golden-capture.json"),
            os.path.join(study, "no-such-scratch"),
            score_rates.REGISTRY_OF_RECORD, None), module)
    finally:
        module.preflight = spent


def _drive_capture_golden(study: str, target: str, module=None) -> str:
    """`capture-golden --out PATH`, as far as its destination gate. Nothing is
    spent and nothing is written: the gate sits third in `capture_golden()`,
    above `verify_ported_bytes()` and far above any call, so the drive either
    refuses there or falls through to a later gate whose message this test
    reads as "not refused by THIS rule"."""
    module = module or batch
    return _refusal_of(lambda: module.capture_golden(
        os.path.join(study, "no-such-capture-attempt"), target,
        module.MIN_CAPTURE_SLOTS), module)


def _drive_capture_isolation_negative(study: str, target: str,
                                      module=None) -> str:
    """`capture-isolation-negative --out DIR`, as far as its destination gate.

    This one is staged, because its gate sits below §6 C7's own preconditions —
    the ported bytes, the freeze, the recorded assent and the golden capture —
    and "this gate alone unmet" means meeting those first. The registry is a
    stand-in built through `fixtures.stand_in_registry()`, which writes every
    lifecycle member, so nothing here is a function of the study's stage
    (§2.10). `invoke()` is replaced for the length of the drive: the ACCEPTING
    half passes the gate and would otherwise spend a real call, and this test
    is about the destination and not about C7."""
    root = fixtures.throwaway_root()
    try:
        golden = os.path.join(root, "GOLDEN.json")
        with open(golden, "w") as handle:
            json.dump({"contextVersion": "1", "entries": [],
                       "capturedFrom": ["a stand-in for the §3.2 capture"]},
                      handle)
        scratch = os.path.join(root, "scratch")
        os.makedirs(scratch)
        with open(score_rates.REGISTRY_OF_RECORD) as handle:
            committed = json.load(handle)
        pins = fixtures.stand_in_registry(committed, {
            ("freeze", "preregistrationSha256"):
                batch._digest(os.path.join(score_rates.STUDY,
                                           "PREREGISTRATION.md")),
            ("freeze", "treeManifestSha256"): fixtures.STAND_IN_TREE_MANIFEST,
            ("golden", "sha256"): "sha256:" + fixtures.file_digest(golden),
            ("isolationNegative", "assent"): "granted"})
        pins_path = os.path.join(root, "PINS.json")
        with open(pins_path, "w") as handle:
            json.dump(pins, handle)

        driven = module or batch

        def no_call(*arguments, **keywords):
            raise driven.BatchError("the drive reached invoke(): past the gate")

        spent, driven.invoke = driven.invoke, no_call
        try:
            return _refusal_of(lambda: driven.capture_isolation_negative(
                target, scratch, pins_path, None, golden), driven)
        finally:
            driven.invoke = spent
    finally:
        shutil.rmtree(root, True)


# One behavioural pair per operator-named destination: the ENTRY it is driven
# through, the drive, the canonical destination, and an in-study sibling
# `freeze.excluded` does not cover. Both paths are relative to the study root.
#
# The entry is written here and CHECKED against the module's own `main()`
# dispatch (round 18, finding 2), because "driven through the command's own
# entry point rather than through the shared predicate" is what this comment
# used to claim while one of the three drove an intermediate — and the wiring
# above that intermediate was then deletable with the whole suite green. A
# probe naming a function `main()` does not dispatch to fails by name at
# collection now, rather than being read as an entry because it says so.
LAWFUL_DESTINATION_PROBES = {
    ("score_rates", "_emit_records", "out_dir"): (
        "score_registered", _drive_emit_records, "records", "analysis/records"),
    ("batch", "capture_golden", "out_path"): (
        "capture_golden", _drive_capture_golden,
        "transcription/GOLDEN-CONTEXT.json", "transcription/GOLDEN-2.json"),
    ("batch", "capture_isolation_negative", "out_dir"): (
        "capture_isolation_negative", _drive_capture_isolation_negative,
        "controls/isolation-negative", "controls/isolation-negative-2"),
    ("batch", "run_capture", "captures_dir"): (
        "run_capture", _drive_run_capture,
        "controls/recapture", "controls/recapture-2"),
}


# --- the operator's own destinations, DERIVED (round 18, finding 1) ---------

# Calls that compute a path and create nothing, so a tainted argument makes a
# tainted result. `os.path.*` is exempt from the writer scan by rule for the
# same reason; this is that rule in the form the taint walk needs.
PATH_ARITHMETIC = frozenset({
    "os.path.join", "os.path.realpath", "os.path.abspath", "os.path.normpath",
    "os.path.dirname", "os.path.basename", "os.path.relpath",
    "os.path.expanduser",
})

# Arguments that are written to by something outside this AST. `invoke()`'s
# first argument is the wrapper's `$SLOT`, and `transcription/authoring_call.sh`
# creates it and fills it with `stdout.raw`, `stderr.raw`, `session.jsonl`,
# `CALL.json` and `context.json`. It is DECLARED rather than derived, and it is
# the reason `--captures` is a destination at all even before `refuse_slot()`
# writes a `REFUSAL.json` under it.
DECLARED_SINKS = {"invoke": 0}

# The rule the taint walk asks about by name.
DESTINATION_GATE = "require_lawful_destination"

# Why an operator-named destination is not a way to move covered bytes. The
# same shape as `ROOT_CLASSIFICATIONS`, plus the one class a destination can be
# in that a writer's parameter root cannot: held by the WRAPPER, which is bash
# and outside every Python check.
DESTINATION_CLASSIFICATIONS = ROOT_CLASSIFICATIONS + ("held-by-the-wrapper",)

# Every command-line flag whose value reaches a write, keyed (flag, the entry
# `main()` hands it to, that entry's formal) — and NOT by the flag alone,
# because `--out` names three destinations through three commands and keyed by
# the flag they would be one row whose gate could be deleted at two of the
# three sites invisibly.
#
# The KEYS are derived by `flagtaint.roster()` from the two modules' own source
# and asserted equal to this table in both directions, so a FIFTH destination
# flag fails here by name. That is the whole difference from round 17, which
# wrote one general predicate, applied it at three call sites chosen by hand,
# and recorded the result as "applied to every operator-supplied destination at
# once" — while `batch.py capture --captures DIR` was a fourth, was ungated,
# and moved the staged tree manifest.
#
# The value is (classification, the behavioural pair that drives it, reason).
OPERATOR_DESTINATIONS = {
    ("--captures", "run_capture", "captures_dir"): (
        "runtime-gated", ("batch", "run_capture", "captures_dir"),
        "the §3.2 recapture's attempt root. Its default `DEFAULT_CAPTURES` = "
        "`controls/recapture/` is an excluded TREE, which is why nothing "
        "noticed: the registered ceremony was lawful and the flag took any "
        "directory. `--captures controls/recapture-2` was accepted, the "
        "wrapper created and filled a slot beneath it, `refuse_slot()` wrote a "
        "`REFUSAL.json` there, and staging what §8 retains moved the §2.10 "
        "tree manifest — measured, cf9c5738 to 2bce35f1, against the default's "
        "unchanged cf9c5738 (round 18, finding 1)."),
    ("--out", "run_capture", "out_path"): (
        "runtime-gated", ("batch", "capture_golden", "out_path"),
        "the same golden capture `capture-golden --out` names, reached through "
        "the `capture` command: `run_capture()` hands its `out_path` to "
        "`capture_golden()`, which is where the rule is called and where the "
        "pair drives it. The derivation reports this row gated THROUGH that "
        "call, so deleting the gate at batch.py:1946 fails this row and "
        "`capture_golden`'s together."),
    ("--out", "capture_golden", "out_path"): (
        "runtime-gated", ("batch", "capture_golden", "out_path"),
        "the golden capture, named directly. README step 5's \"leave `--out` "
        "at its default\" was prose and not a check until round 17, finding "
        "1."),
    ("--out", "capture_isolation_negative", "out_dir"): (
        "runtime-gated", ("batch", "capture_isolation_negative", "out_dir"),
        "§6 C7's record. A TREE here rather than a file, so every path beneath "
        "it has to be covered by a registered exclusion tree."),
    ("--emit-records", "score_registered", "records_dir"): (
        "runtime-gated", ("score_rates", "_emit_records", "out_dir"),
        "the compiled record trees. Gated against the POPULATION by "
        "`_check_records_target()` and against the MANIFEST by the rule this "
        "table is about — the two halves of §2.10 rule 3, both reached through "
        "the registered entry `score_registered()`."),
    ("--scratch-parent", "capture_isolation_negative", "scratch_parent"): (
        "held-by-the-wrapper", None,
        "§6 C7's raw slot: `capture_isolation_negative()` builds "
        "`os.path.join(scratch_parent, 's012-c7-raw-<pid>')` and hands it to "
        "`invoke()`, where the wrapper creates it and writes five files into "
        "it. It is NOT gated by `require_lawful_destination()` and must not "
        "be: the registered value is a directory OUTSIDE the study, which the "
        "rule would accept, but the rule cannot be what holds it because the "
        "operator's legitimate parent is outside the study by design. What "
        "holds it is `transcription/authoring_call.sh:216-219` — \"the scratch "
        "dir resolves inside the repository\" and \"the scratch dir is inside "
        "some git worktree\" — which fires BEFORE the slot is created. This "
        "row is why the roster is a table and not a list of gated flags: the "
        "derivation found this destination, and the honest answer to it is a "
        "classification rather than a fifth call to the rule."),
}


def _taint_creates(call) -> bool:
    """Whether a call creates a file AT THIS SITE, by the writer scan's own
    two rules — the same `_classify()` and `_creates()` the destination case
    uses, so there is one vocabulary and not a second copy. It fails CLOSED:
    a mode or flag set that cannot be read counts as creating."""
    try:
        return _classify(call) == "creator" and _creates(call)
    except Unclassified:
        return True


def _entry_modules() -> tuple:
    """The writing modules that have a command line — derived, by asking each
    one's source whether it defines `main()`, rather than naming the two that
    do today."""
    found = []
    for module in WRITING_MODULES:
        with open(module.__file__, encoding="utf-8") as handle:
            source = handle.read()
        if "main" in {node.name for node in ast.parse(source).body
                      if isinstance(node, ast.FunctionDef)}:
            found.append((module, source))
    return tuple(found)


def operator_destinations() -> dict:
    """{(flag, entry, formal): (gated, sinks)} over every module with a command
    line, read out of their own sources."""
    rows = {}
    for module, source in _entry_modules():
        rows.update(flagtaint.roster(
            source, "main", FILE_WRITERS, _taint_creates, PATH_ARITHMETIC,
            DESTINATION_GATE, DECLARED_SINKS))
    return rows


def test_every_operator_named_destination_is_registered_and_gated(study):
    """The class, closed by DERIVATION rather than by a fourth list.

    Rounds 14, 16 and 17 each repaired one member of one class — `records/`
    absent from the exclusion list, `CORRECTION.md`, `arms/BATCH.json.partial`,
    the two `--out` flags — and each repair was scoped to the instance in front
    of it. Round 17 went furthest: it wrote ONE general predicate. It then
    called that predicate at three call sites chosen by hand and recorded the
    result as "applied to every operator-supplied destination at once". Round
    18 found the fourth, `--captures`, and measured the manifest moving.

    So the members are computed. `flagtaint.roster()` walks the source of every
    writing module that has a `main()` — all four of them, which is the scope
    and not the two that carry destinations today — seeds every `--flag`
    literal each `main()` reads, propagates the value forward through
    assignment, `for` targets, path arithmetic and the module's own calls, and
    reports every flag whose value reaches a file-creating write or the
    wrapper's slot, together with whether the lawful-destination rule was
    called on that same value on the way.

    THREE THINGS ARE ASSERTED, and each fails BY NAME.
      * The roster IS this table: a fifth destination flag, or a flag that
        stops being one, is a named failure here rather than a member nobody
        listed.
      * A row is gated exactly when it is classified `runtime-gated`. Deleting
        a call to the rule flips its row to UNGATED and fails; adding one to a
        row held another way fails too, because a destination that has acquired
        a gate has changed class.
      * Every `runtime-gated` row names a behavioural PAIR, so the derivation's
        "the gate is called on this value somewhere" is backed by a run in
        which the unlawful destination is actually refused.

    WHAT THE DERIVATION CANNOT SEE — in its own docstring, because a residual
    stated in a summary is what rounds 15, 16 and 17 each recorded and each had
    to widen. A destination escapes it by being: not named by a flag at all
    (`os.environ`, a config file, a positional argument, a mutated module
    constant); reached through a call the walk cannot follow (an
    attribute-spelled or computed callee on the PROPAGATION path — the gate is
    matched by its dotted name, the propagation is not — a callable passed as a
    parameter, or a value stored in and read back out of a container or an
    attribute); written only by the wrapper along a path the driver never names
    (`invoke()`'s slot is a DECLARED sink; `$SCRATCH`, `$RUN_TMP` and
    `$ISOLATED_HOME` are outside the AST entirely); named POSITIONALLY rather
    than by a flag — all four writing modules define `main()` and all four are
    walked, but `records_compile` and `arm_assembly` take their destination as
    `argv[n]`, so this seeding finds nothing in them and their roots are
    classified in `PARAMETER_ROOTS` instead; written by a module with no
    `main()` at all, which `census.py` is; or gated on one branch only, or
    below the write, because the taint is path-INSENSITIVE: "the value reaches
    the gate somewhere" is not "the gate dominates every write", and what
    covers that is the behavioural pair.
    """
    derived = operator_destinations()
    assert set(derived) == set(OPERATOR_DESTINATIONS), (
        "the flags whose values reach a write are not the flags this table "
        "registers. Derived and unregistered: %r. Registered and no longer "
        "derived: %r. A destination flag arrives with a classification and, if "
        "it is gated, a behavioural pair — it does not arrive as a member "
        "nobody listed (round 18, finding 1)."
        % (sorted(set(derived) - set(OPERATOR_DESTINATIONS)),
           sorted(set(OPERATOR_DESTINATIONS) - set(derived))))
    # …and the walk is LIVE rather than an empty roster agreeing with an empty
    # table. Its SCOPE is every writing module that has a `main()` — all four
    # of them, not the two that carry destinations — so a module that starts
    # naming a destination by flag is inside this case from the moment it does,
    # and both modules that do today contribute rows.
    assert len(_entry_modules()) == len(WRITING_MODULES)
    assert {key[1] for key in derived} & {"score_registered"}
    assert {key[1] for key in derived} - {"score_registered"}
    for key, value in sorted(OPERATOR_DESTINATIONS.items()):
        assert isinstance(value, tuple) and len(value) == 3, key
        kind, pair, why = value
        assert kind in DESTINATION_CLASSIFICATIONS, (
            "%r is classified %r, which is not one of %r"
            % (key, kind, DESTINATION_CLASSIFICATIONS))
        assert why and len(why) > 40, key
        gated = derived[key][0]
        assert gated == (kind == "runtime-gated"), (
            "%r is classified %r and the derivation reports it %s: a "
            "destination is gated exactly when it is classified runtime-gated, "
            "so this is either a deleted call to %s() or a row whose class has "
            "changed" % (key, kind, "gated" if gated else "UNGATED",
                         DESTINATION_GATE))
        if kind == "runtime-gated":
            assert pair in LAWFUL_DESTINATION_PROBES, (
                "%r is gated and names the behavioural pair %r, which "
                "`LAWFUL_DESTINATION_PROBES` does not carry: the derivation "
                "says the rule is CALLED on this value, and only a pair says "
                "it refuses" % (key, pair))
        else:
            assert pair is None, key
    # No pair is orphaned: every behavioural pair is claimed either by a
    # destination row here or by a runtime-gated parameter root above.
    claimed = {pair for _kind, pair, _why in OPERATOR_DESTINATIONS.values()
               if pair is not None}
    claimed |= {key for key, (kind, _why) in PARAMETER_ROOTS.items()
                if kind == "runtime-gated"}
    assert set(LAWFUL_DESTINATION_PROBES) == claimed, (
        "these behavioural pairs are claimed by no destination row and no "
        "runtime-gated parameter root, or are claimed and missing: %r"
        % (sorted(set(LAWFUL_DESTINATION_PROBES) ^ claimed),))


def test_every_parameter_root_carries_a_classification_not_only_a_reason(study):
    """`PARAMETER_ROOTS` says why each operator-supplied destination is not
    covered bytes, and the WHY is now a member of a fixed vocabulary.

    Round 17, finding 1. The old table held prose, and one entry's prose was
    three true clauses that did not compose: `--emit-records` was gated against
    the population, README step 7 names `records`, and a test bound that NAME
    to an excluded tree — none of which says anything about the interface the
    flag actually registers, which takes any directory. The classification is
    what makes the difference checkable: a root claimed to be held at run time
    has to produce a refusal, and one claimed to be held by construction has to
    say by which construction."""
    for key, value in sorted(PARAMETER_ROOTS.items()):
        assert isinstance(value, tuple) and len(value) == 2, (
            "%r carries %r: a parameter root is (classification, reason), and "
            "a bare sentence is what round 17 finding 1 found wrong"
            % (key, value))
        kind, why = value
        assert kind in ROOT_CLASSIFICATIONS, (
            "%r is classified %r, which is not one of %r: a new class of "
            "reason is a change to what this table means and arrives here "
            "rather than in one entry" % (key, kind, ROOT_CLASSIFICATIONS))
        assert why and len(why) > 40, key
    gated = {key for key, (kind, _why) in PARAMETER_ROOTS.items()
             if kind == "runtime-gated"}
    assert gated <= set(LAWFUL_DESTINATION_PROBES), (
        "every runtime-gated root needs a behavioural pair: %r"
        % (sorted(gated - set(LAWFUL_DESTINATION_PROBES)),))
    # …and no pair may exist without a claimant, which the destination case
    # above asserts over both tables at once — a parameter root here, or a
    # derived operator destination there.

    # THE ENTRY EACH PAIR DRIVES IS DERIVED (round 18, finding 2). A probe that
    # names a function `main()` does not dispatch to is a probe bound BELOW its
    # own entry, and the wiring above it is then deletable with the suite
    # green: measured, deleting `score_registered()`'s call to
    # `_check_records_target()` left integrity at exit 0 and the pinned suite
    # at 315 passed while removing both halves of §2.10 rule 3's destination
    # rule. The legal set of drive targets is read out of each module's own
    # dispatch here, so the next probe cannot bind to a helper and say in a
    # docstring that it did not.
    for key, (entry, _drive, _lawful, _unlawful) in sorted(
            LAWFUL_DESTINATION_PROBES.items()):
        module = {"batch": batch, "score_rates": score_rates}[key[0]]
        tree = gatescan.parse(module.__file__)
        functions = gatescan.module_functions(tree)
        assert entry in gatescan.entry_points(functions["main"], functions), (
            "%r drives %r, which is not a function %s.main() dispatches to: a "
            "probe bound below the entry stays green with the wiring above it "
            "deleted (round 18, finding 2). The entries are %r."
            % (key, entry, key[0],
               gatescan.entry_points(functions["main"], functions)))


def test_every_runtime_gated_destination_refuses_an_unlawful_one(study, pins):
    """The gate, driven — because a gate with no case is a gate that can be
    deleted with the suite green, and that is the defect round 16's own repair
    reproduced.

    §2.10 rule 3 registers that every act from the freeze to publication moves
    carrier or excluded bytes only. FOUR operator-named destinations can break
    it — `score --emit-records DIR`, `capture --captures DIR`, `capture-golden
    --out PATH` and `capture-isolation-negative --out DIR` — and each is driven
    here twice: the registered destination must not be refused by this rule,
    and an in-study sibling the exclusion list does not cover must be, naming
    the path.

    WHAT STOPS A FIFTH, said accurately this time. Round 13 asserted the
    manifest invariant "under every registered lifecycle act" and modelled five
    documents; round 14 modelled the emit act at ONE literal value; round 16
    made the writer scan's vocabulary total and left the parameter door it had
    itself documented; round 17 wrote one general predicate and called it at
    three call sites CHOSEN BY HAND. This docstring then said "what stops a
    fifth is that the rule is general and that its generality is exercised",
    which was false in the way that mattered: what was general was
    `require_lawful_destination()`, and what stopped at three was the list of
    places it is called. A fourth had already arrived — `--captures` — and it
    was ungated.

    What stops a fifth is
    `test_every_operator_named_destination_is_registered_and_gated` above,
    which DERIVES the destinations from the two modules' own source and fails
    by name on a flag whose value reaches a write and is not registered. These
    pairs are what turn that derivation's "the rule is called on this value"
    into "and it refuses"; neither is the other's substitute."""
    registered = tuple(pins["freeze"]["excluded"])
    for key, (_entry, drive, lawful, unlawful) in sorted(
            LAWFUL_DESTINATION_PROBES.items()):
        # The fixture is live at both ends: the pair really is one excluded
        # destination and one the registry does not cover, read out of
        # `freeze.excluded` rather than asserted here.
        assert (integrity.excluded_tree_covers(lawful, registered)
                or integrity.manifest_excluded(lawful, registered)), (key, lawful)
        assert not integrity.excluded_tree_covers(unlawful, registered), (
            key, unlawful)
        assert not integrity.manifest_excluded(unlawful, registered), (
            key, unlawful)

        admitted = drive(study, os.path.join(study, lawful))
        assert LAWFUL_DESTINATION_NEEDLE not in admitted, (
            "%r refuses its own registered destination %r: %s"
            % (key, lawful, admitted))
        refused = drive(study, os.path.join(study, unlawful))
        assert LAWFUL_DESTINATION_NEEDLE in refused, (
            "%r accepted %r, which harness/PINS.json does not exclude, so the "
            "act that writes there moves the §2.10 tree manifest: %s"
            % (key, unlawful, refused or "(no refusal at all)"))
        assert unlawful in refused, (key, refused)


def test_deleting_any_link_of_a_destination_gate_turns_its_case_red(study):
    """"Deleting the call turns this red" — RUN, for every link of the chain.

    Round 18, finding 2. The pair above is what makes the destination rule a
    behaviour rather than a predicate, and until this case the claim that it
    would catch a deleted call was a sentence in a docstring. It was false:
    `_drive_emit_records()` called `_check_records_target()` itself, so the one
    line in `score_registered()` that wires the rule into the registered
    command could be deleted with `harness/integrity.py` at exit 0 and the
    whole pinned suite at 315 passed — and that deletion removes the round-14
    POPULATION check with it, not only the destination check.

    So the chain is derived and each of its links is cut. `redness.chain_to()`
    reads the path from the module's own `main()` down to
    `require_lawful_destination()` out of the source; `redness.mutant()`
    compiles the module with ONE of those calls removed, into a throwaway
    module object that is never written and never imported by name; the probe's
    own drive is re-run against it; and the UNLAWFUL destination must stop
    being refused. A link this case cannot cover is reported by name rather
    than passed over: today those are exactly the four `main()` -> entry edges,
    which are VALUE edges (`return run_capture(…)`) that cannot be deleted and
    still compile — which is why a drive starts at an entry, and which is the
    round-18 finding stated as a property of the chain rather than as an
    apology.

    This case is the reason the pair may claim redness at all. It is not a
    substitute for the ledgers in `test_batch.py` and `test_admission.py`:
    those protect gates no probe drives, and this protects only chains a probe
    does. `redness.py`'s own docstring carries what the mutation operator
    cannot reach."""
    with open(score_rates.REGISTRY_OF_RECORD) as handle:
        registered = tuple(json.load(handle)["freeze"]["excluded"])
    modules = {"batch": batch, "score_rates": score_rates}
    uncoverable = []
    cut = 0
    for key, (entry, drive, _lawful, unlawful) in sorted(
            LAWFUL_DESTINATION_PROBES.items()):
        module = modules[key[0]]
        universe = gatescan.Universe(module.__file__)
        # What the command line runs ABOVE the drive point, derived the same
        # way: the case cannot cut those and says so by name.
        for _home, host, callee, _line, _deletable in redness.chain_to(
                universe, "main", entry):
            uncoverable.append((key, "%s() -> %s (above the drive point)"
                                % (host, callee)))
        chain = redness.chain_to(universe, entry, DESTINATION_GATE)
        assert chain, (
            "%s.%s() reaches no %s(): the chain this case cuts is derived from "
            "the source, so an empty one is a rule that is no longer wired in "
            "at all" % (key[0], entry, DESTINATION_GATE))
        assert not integrity.manifest_excluded(unlawful, registered), key
        for home, host, callee, line, deletable in chain:
            if not deletable:
                uncoverable.append((key, "%s() -> %s (not a deletable "
                                         "statement)" % (host, callee)))
                continue
            broken = redness.mutant(modules[home], host, callee, line)
            refused = drive(study, os.path.join(study, unlawful),
                            module=broken)
            assert LAWFUL_DESTINATION_NEEDLE not in refused, (
                "%r still refuses %r with %s.py:%d %s() -> %s deleted, so this "
                "pair is not what holds that call: %s"
                % (key, unlawful, home, line, host, callee, refused))
            cut += 1
    # …and the harness is live: it cut something, and what it could not cut it
    # named. Today every link below each drive point is deletable and every
    # deletion is caught, so the only uncoverable links are the value edges
    # `main()` dispatches through — which no case can delete and keep the
    # module compiling, and which is why a drive starts at an entry.
    assert cut == 5, cut
    assert all("above the drive point" in why or "not a deletable" in why
               for _key, why in uncoverable), uncoverable


def test_every_writing_module_is_scanned(study):
    """`WRITING_MODULES` is the scan's own scope, so a module that starts
    writing outside it would be invisible. Every harness module is parsed here
    and one that holds a file-creating write must be in the list.

    Round 16, finding 3: through the SAME scanner as the destination case
    above, not a second copy of its vocabulary. It used to re-implement the
    `FILE_WRITERS`/`_creates()` pair inline, so a new module writing only
    through `tempfile.mkstemp` passed here as "not a writing module" — the
    identical fail-open one level up, which is the level that decides what gets
    scanned at all.

    Its directory scope is `harness/` top level and is stated rather than
    widened: `analysis/` and `transcription/` hold no Python that writes today
    (`transcription/authoring_call.sh` is bash and is named in the case above),
    and a Python writer appearing there is outside this case."""
    harness = os.path.join(study, "harness")
    missing = []
    scanned = {os.path.realpath(module.__file__) for module in WRITING_MODULES}
    for name in sorted(os.listdir(harness)):
        if not name.endswith(".py"):
            continue
        path = os.path.join(harness, name)
        if os.path.realpath(path) in scanned:
            continue
        with open(path, encoding="utf-8") as handle:
            sites, offenders = scan_source(name[:-3], handle.read())
        missing.extend("%s:%d creates a file" % (name, line)
                       for line, _scope, _root, _tail in sites)
        missing.extend(offenders)
    assert missing == [], (
        "these harness modules create files, or make a filesystem call this "
        "scan cannot classify, and are outside WRITING_MODULES — so their "
        "destinations are checked against freeze.excluded by nothing: %r"
        % (missing,))


# --- stand-in registries and the study's stage (round 16, finding 4) ---------

# The one constructor every stand-in registry has to go through, and the
# spellings that name the COMMITTED registry. A path built from a PARAMETER is
# some throwaway copy and is not this rule's subject; a path built from a
# module constant is the registry of record.
STAND_IN_CONSTRUCTOR = "stand_in_registry"
REGISTRY_NAMES = ("REGISTRY", "REGISTRY_OF_RECORD", "score_rates.REGISTRY_OF_RECORD")

# The calls that write a registry OUT. Handing the object to any other callee
# is READING it — `batch.check_registry(committed)`,
# `integrity.verify_interpreter(pins)`, `fixtures.Population(…, pins)` are all
# legitimate and all silent — so the escape rule is deliberately narrow.
REGISTRY_WRITERS = ("json.dump", "write_pins")


def _names_the_committed_registry(node, constants: dict) -> bool:
    """Whether an `open()` argument names `harness/PINS.json` itself."""
    name = _dotted(node)
    if name in REGISTRY_NAMES:
        return True
    if isinstance(node, ast.Call) and _dotted(node.func) == "os.path.join":
        parts = node.args
        if not parts or not isinstance(parts[-1], ast.Constant) \
                or parts[-1].value != "PINS.json":
            return False
        # …rooted at a module constant. A parameter root is a copy of the tree
        # under a throwaway root (`test_manifest._registry_edit`), not the
        # registry of record.
        return _dotted(parts[0]) in constants
    return False


def _escapes(scope_node, bound: list) -> bool:
    """Whether a bound registry LEAVES this scope as a registry.

    Round 17, finding 5 replaced the write-SHAPE trigger with this one. The
    rule used to fire only on a scope that ASSIGNED into the loaded object with
    a two-level constant subscript, which is false of every one of the six real
    loader scopes in the committed tree — so the rule fired on nothing at all
    and was kept alive entirely by its own two synthetic controls. Worse, the
    shapes it carved out are not exotic: a scope that loads the committed
    registry and simply RETURNS it inherits all four lifecycle members, which
    is the worst case the rule exists to stop.

    Three ways out, and no more. `return pins`; an attribute or subscript
    assignment (`self.pins = pins`); and a call that WRITES it
    (`REGISTRY_WRITERS`). Deliberately NOT an escape: handing the object to any
    other callee, including returning that call's RESULT. That is reading, and
    counting it fires on the legitimate scopes that hand the committed registry
    to a checker — `integrity.verify_interpreter(pins)` in
    `test_batch.registered_interpreter()` is the live one, measured: the
    broader rule reported it as a builder inheriting all four members, and it
    builds nothing and returns a string. The cost of the narrower rule is
    recorded in this rule's own limits rather than paid in a false offender.

    The constructor exemption is the one exemption left, and it is not
    syntactic: `_registry_loaders()` unbinds a name REASSIGNED from the
    constructor, so `committed = fixtures.stand_in_registry(committed)` leaves
    nothing bound to escape. What used to be here instead was a suffix match on
    any call taking a bound name positionally — which a local homonym
    satisfied, and which a delegation whose result was DISCARDED also
    satisfied."""
    names = set(bound)

    def leaves(value) -> bool:
        if isinstance(value, ast.Name):
            return value.id in names
        if isinstance(value, (ast.Tuple, ast.List)):
            return any(leaves(item) for item in value.elts)
        return False

    for node in ast.walk(scope_node):
        if isinstance(node, ast.Return) and node.value is not None \
                and leaves(node.value):
            return True
        if isinstance(node, ast.Assign) and leaves(node.value) \
                and any(isinstance(target, (ast.Attribute, ast.Subscript))
                        for target in node.targets):
            return True
        if isinstance(node, ast.Call):
            name = _dotted(node.func) or ""
            if (name in REGISTRY_WRITERS
                    or name.rsplit(".", 1)[-1] in REGISTRY_WRITERS) \
                    and any(leaves(argument) for argument in node.args):
                return True
    return False


def _registry_loaders(tree: ast.Module, constants: dict) -> list:
    """[(scope name, scope node, [names bound to the committed registry or to a
    copy of it])], one entry per SCOPE.

    Round 17, finding 5: keyed on the scope NODE, not on its name. Two
    same-named builders in one module used to be one subject and definition
    order decided which — an innocent `stand_in_registry()` defined above an
    offending one made the offender invisible, and the same pair in the other
    order fired. The appends are deduped for a related reason: `_scope_calls()`
    yields once per CALL, so a scope with fourteen calls in it re-walked its
    own body fourteen times and bound every name fourteen times over."""
    loaded = {}

    def entry(scope_name, scope_node):
        return loaded.setdefault(id(scope_node), (scope_name, scope_node, []))

    for scope_name, scope_node, call in _scope_calls(tree):
        if _dotted(call.func) not in ("json.load", "json.loads"):
            continue
        argument = call.args[0] if call.args else None
        source = argument
        if isinstance(source, ast.Call) and _dotted(source.func) == "open":
            source = source.args[0] if source.args else None
        if source is None or not _names_the_committed_registry(source, constants):
            # `json.load(handle)` — follow the handle back to its `with open()`.
            if not isinstance(argument, ast.Name):
                continue
            opened = [item.context_expr for node in ast.walk(scope_node)
                      if isinstance(node, ast.With)
                      for item in node.items
                      if isinstance(item.optional_vars, ast.Name)
                      and item.optional_vars.id == argument.id
                      and isinstance(item.context_expr, ast.Call)
                      and _dotted(item.context_expr.func) == "open"]
            if not any(_names_the_committed_registry(one.args[0], constants)
                       for one in opened if one.args):
                continue
        for node in ast.walk(scope_node):
            if isinstance(node, ast.Assign) and node.value is call \
                    and len(node.targets) == 1 \
                    and isinstance(node.targets[0], ast.Name):
                bound = entry(scope_name, scope_node)[2]
                if node.targets[0].id not in bound:
                    bound.append(node.targets[0].id)
    for scope_name, scope_node, bound in loaded.values():
        # …every name that is a COPY of one of those, because a builder that
        # copies before it assigns inherits exactly as much as one that does
        # not…
        for node in ast.walk(scope_node):
            if not isinstance(node, ast.Assign) or len(node.targets) != 1 \
                    or not isinstance(node.targets[0], ast.Name):
                continue
            inner = {_dotted(item) for item in ast.walk(node.value)
                     if isinstance(item, ast.Name)}
            if inner & set(bound) and any(
                    _dotted(item.func) in ("json.loads", "copy.deepcopy", "dict")
                    or (isinstance(item.func, ast.Attribute)
                        and item.func.attr == "copy")
                    for item in ast.walk(node.value)
                    if isinstance(item, ast.Call)) \
                    and node.targets[0].id not in bound:
                bound.append(node.targets[0].id)
        # …and any name REBOUND from the shared constructor stops being one.
        # `committed = fixtures.stand_in_registry(committed)` returns a written
        # copy, so what escapes afterwards is the written object and not the
        # loaded one. Without this the delegating shape would fire the moment
        # its delegation stopped being an exemption of its own.
        for node in ast.walk(scope_node):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                    and isinstance(node.targets[0], ast.Name) \
                    and isinstance(node.value, ast.Call) \
                    and (_dotted(node.value.func) or "").endswith(
                        STAND_IN_CONSTRUCTOR) \
                    and node.targets[0].id in bound:
                bound.remove(node.targets[0].id)
    return sorted(loaded.values(),
                  key=lambda row: (row[0], getattr(row[1], "lineno", 0)))


def stand_in_offenders(name: str, source: str) -> list:
    """The rule below, over one file's source."""
    tree = ast.parse(source)
    required = set(integrity.POST_FREEZE_MEMBERS)
    constants = {node.targets[0].id for node in tree.body
                 if isinstance(node, ast.Assign) and len(node.targets) == 1
                 and isinstance(node.targets[0], ast.Name)}
    offenders = []
    for scope_name, scope_node, bound in _registry_loaders(tree, constants):
        # Round 17, finding 5: the trigger is ESCAPE, and the two syntactic
        # exemptions are gone. `delegates` fired on ANY call whose dotted name
        # ended in `stand_in_registry` that took a bound name positionally — so
        # a local homonym that did nothing but `return pins` was exempt, and so
        # was a real delegation whose result was thrown away. `looped` fired on
        # ANY `for` over `integrity.POST_FREEZE_MEMBERS` anywhere in the scope
        # subtree, with no look at the body — a loop that only asserted the
        # pairs were non-null bought a builder its exemption. Neither is
        # needed: a delegation that escapes is the CONSTRUCTOR's object, which
        # `_registry_loaders()` unbinds, and a genuine member-writing loop
        # writes the members.
        if not _escapes(scope_node, bound):
            continue
        written = set()
        for node in ast.walk(scope_node):
            if not isinstance(node, (ast.Assign, ast.AugAssign)):
                continue
            targets = (node.targets if isinstance(node, ast.Assign)
                       else [node.target])
            for target in targets:
                if not isinstance(target, ast.Subscript):
                    continue
                parent = target.value
                root = parent.value if isinstance(parent, ast.Subscript) else None
                if not isinstance(root, ast.Name) or root.id not in bound:
                    continue
                if isinstance(parent.slice, ast.Constant) \
                        and isinstance(target.slice, ast.Constant):
                    written.add((parent.slice.value, target.slice.value))
        if required - written:
            offenders.append(
                "%s %s() loads the committed registry and writes %r, "
                "inheriting %r: a stand-in registry writes every member of "
                "integrity.POST_FREEZE_MEMBERS or goes through "
                "fixtures.stand_in_registry(), or every case standing on it is "
                "a function of the study's stage (§2.10)"
                % (name, scope_name, sorted(written), sorted(required - written)))
    return offenders


# The two builders this rule replaces, as they stood before their rounds — the
# positive control, so the lint is one that has been seen to fire.
INHERITING_BUILDERS = (
    ("round 16's: three of the four members written, the tree pin inherited",
     "import json\nimport score_rates\n"
     "def _stand_in_registry(root, golden):\n"
     "    with open(score_rates.REGISTRY_OF_RECORD) as handle:\n"
     "        pins = json.load(handle)\n"
     "    pins['golden']['sha256'] = golden\n"
     "    pins['freeze']['preregistrationSha256'] = 'x'\n"
     "    pins['isolationNegative']['assent'] = 'granted'\n"
     "    return pins\n"),
    ("round 15's: the copy assigned into, two members inherited",
     "import json\nREGISTRY = '/x/harness/PINS.json'\n"
     "def stand_in_registry():\n"
     "    with open(REGISTRY) as handle:\n"
     "        committed = json.load(handle)\n"
     "    pins = json.loads(json.dumps(committed))\n"
     "    pins['freeze']['preregistrationSha256'] = 'x'\n"
     "    pins['freeze']['treeManifestSha256'] = None\n"
     "    return pins\n"),
    # Round 17, finding 5. Every one of these was SILENT under the rule as
    # round 16 recorded it, and the first is the worst case the rule exists to
    # stop: a builder that inherits all four members and hands them out.
    ("round 17's: a direct return, all four members inherited",
     "import json\nREGISTRY = '/x/harness/PINS.json'\n"
     "def stand_in_registry():\n"
     "    with open(REGISTRY) as handle:\n"
     "        pins = json.load(handle)\n"
     "    return pins\n"),
    ("round 17's: a decoy loop over the member tuple that writes nothing",
     "import json\nimport integrity\nREGISTRY = '/x/harness/PINS.json'\n"
     "def stand_in_registry():\n"
     "    with open(REGISTRY) as handle:\n"
     "        pins = json.load(handle)\n"
     "    for pair in integrity.POST_FREEZE_MEMBERS:\n"
     "        assert pair\n"
     "    return pins\n"),
    ("round 17's: a delegation whose result is discarded",
     "import json\nimport fixtures\nREGISTRY = '/x/harness/PINS.json'\n"
     "def stand_in_registry(golden):\n"
     "    with open(REGISTRY) as handle:\n"
     "        committed = json.load(handle)\n"
     "    fixtures.stand_in_registry(committed)\n"
     "    committed['golden']['sha256'] = golden\n"
     "    return committed\n"),
    ("round 17's: a local homonym that delegates to nothing",
     "import json\nREGISTRY = '/x/harness/PINS.json'\n"
     "def _my_stand_in_registry(pins):\n"
     "    return pins\n"
     "def stand_in_registry(golden):\n"
     "    with open(REGISTRY) as handle:\n"
     "        pins = json.load(handle)\n"
     "    pins['golden']['sha256'] = golden\n"
     "    _my_stand_in_registry(pins)\n"
     "    return pins\n"),
    ("round 17's: a one-level replacement of each parent object",
     "import json\nREGISTRY = '/x/harness/PINS.json'\n"
     "def stand_in_registry():\n"
     "    with open(REGISTRY) as handle:\n"
     "        pins = json.load(handle)\n"
     "    pins['freeze'] = {'preregistrationSha256': 'x'}\n"
     "    pins['golden'] = {'sha256': 'y'}\n"
     "    return pins\n"),
    ("round 17's: `.update()` instead of an assignment",
     "import json\nREGISTRY = '/x/harness/PINS.json'\n"
     "def stand_in_registry():\n"
     "    with open(REGISTRY) as handle:\n"
     "        pins = json.load(handle)\n"
     "    pins['golden'].update({'sha256': 'y'})\n"
     "    return pins\n"),
    ("round 17's: two same-named builders, the innocent one defined first",
     "import json\nREGISTRY = '/x/harness/PINS.json'\n"
     "class Good:\n"
     "    def stand_in_registry(self):\n"
     "        with open(REGISTRY) as handle:\n"
     "            pins = json.load(handle)\n"
     "        pins['freeze']['preregistrationSha256'] = 'x'\n"
     "        pins['freeze']['treeManifestSha256'] = 'y'\n"
     "        pins['golden']['sha256'] = 'z'\n"
     "        pins['isolationNegative']['assent'] = 'granted'\n"
     "        return pins\n"
     "class Bad:\n"
     "    def stand_in_registry(self):\n"
     "        with open(REGISTRY) as handle:\n"
     "            pins = json.load(handle)\n"
     "        pins['golden']['sha256'] = 'z'\n"
     "        return pins\n"),
)

# …and the other end of the strengthening: shapes that must stay SILENT, so
# the rule is shown not to over-fire. `base_offenders == []` over the real
# harness/tests/ is the same move the writer scan makes; this adds the three
# CORRECT builder shapes explicitly, because a rule that fires on everything
# would satisfy `INHERITING_BUILDERS` and prove nothing (round 17, finding 5).
CORRECT_BUILDERS = (
    ("the shared constructor, returned directly",
     "import json\nimport fixtures\nREGISTRY = '/x/harness/PINS.json'\n"
     "def stand_in_registry(golden):\n"
     "    with open(REGISTRY) as handle:\n"
     "        committed = json.load(handle)\n"
     "    return fixtures.stand_in_registry(\n"
     "        committed, {('golden', 'sha256'): golden})\n"),
    ("the shared constructor, rebinding the loaded name",
     "import json\nimport fixtures\nREGISTRY = '/x/harness/PINS.json'\n"
     "def stand_in_registry(golden):\n"
     "    with open(REGISTRY) as handle:\n"
     "        committed = json.load(handle)\n"
     "    committed = fixtures.stand_in_registry(committed)\n"
     "    committed['golden']['sha256'] = golden\n"
     "    return committed\n"),
    ("a hand-written builder that writes all four members",
     "import json\nREGISTRY = '/x/harness/PINS.json'\n"
     "def stand_in_registry():\n"
     "    with open(REGISTRY) as handle:\n"
     "        pins = json.load(handle)\n"
     "    pins['freeze']['preregistrationSha256'] = 'x'\n"
     "    pins['freeze']['treeManifestSha256'] = 'y'\n"
     "    pins['golden']['sha256'] = 'z'\n"
     "    pins['isolationNegative']['assent'] = 'granted'\n"
     "    return pins\n"),
    ("a scope that only READS the committed registry",
     "import json\nimport batch\nREGISTRY = '/x/harness/PINS.json'\n"
     "def test_the_committed_registry_passes(self):\n"
     "    with open(REGISTRY) as handle:\n"
     "        pins = json.load(handle)\n"
     "    batch.check_registry(pins)\n"),
)


def test_every_stand_in_registry_writes_every_lifecycle_member(study):
    """§2.10: a test expectation may not be a function of the study's STAGE.

    Round 15 fixed `test_batch.py`'s builder and recorded in PREREG-REVIEW.md
    that it was the only fixture inheriting a lifecycle member. That was false:
    `test_admission.py`'s near-identically named `_stand_in_registry()`
    inherited `freeze.treeManifestSha256`. Two hand-kept builders and two
    hand-kept guards is the pattern this sequence has now repeated three times,
    so the guard is a RULE over the sources instead:

      every scope under `harness/tests/` that loads the COMMITTED registry and
      then lets it ESCAPE — returns it, returns something computed from it,
      stores it on an attribute or a subscript, or writes it out — must write
      every member of `integrity.POST_FREEZE_MEMBERS`, or go through
      `fixtures.stand_in_registry()`, which writes them all by looping over
      that same tuple.

    It discovers builders rather than listing them, it is keyed off the member
    tuple so a fifth member is covered without an edit, and it does NOT fire on
    the fixtures' own ceremony acts (`register_golden()`,
    `record_negative_control()`), which advance one member over a registry that
    is already a stand-in and never load the committed one.

    ROUND 17, FINDING 5 CHANGED THE TRIGGER, and the reason is worth stating
    because the rule read exactly the same before. The trigger was that the
    scope ASSIGNED into the loaded object with a two-level constant subscript.
    That is false of all six loader scopes in the committed tree, so the rule
    fired on NOTHING and was kept alive entirely by the two positive controls
    below — a registered sentence (PREREGISTRATION.md §2.10) and a recorded one
    (PREREG-REVIEW.md) both said a source rule held any future stand-in to this
    discipline, and the rule held one shape. A builder that loaded the
    committed registry and simply RETURNED it inherited all four members and
    was silent; so were `pins['freeze'] = {…}`, `pins['golden'].update(…)`, a
    decoy `for pair in integrity.POST_FREEZE_MEMBERS: assert pair`, a
    delegation whose result was thrown away, a local homonym named
    `_my_stand_in_registry`, and — because scopes were keyed by NAME — an
    offending builder defined below an innocent one of the same name. Each of
    those is a control below now.

    What it does not cover, said rather than implied.
      * A builder that reads the committed registry through something other
        than `open`/`json.load` — for instance `integrity.normalized_pins()`,
        which nulls all four members and is therefore stage-invariant by
        construction.
      * A registry that escapes by being handed to a HELPER that stores or
        writes it. Passing the object to a callee is reading here,
        deliberately: counting it fires on the scopes that hand the committed
        registry to a checker, and it does so in this very tree —
        `registered_interpreter()` in `test_batch.py` returns
        `integrity.verify_interpreter(pins)`, which is a string, and the
        broader rule called it a builder inheriting all four members.
        `fixtures.Population(…, pins)` is the live instance of the shape this
        therefore leaves outside; it is reviewed, not asserted.
      * `CALL.json`'s `pinsSha256` (`fixtures.py`), the live digest of the
        registry FILE. That byte IS a function of all four members and does
        move by stage; it is deliberate, and invariant as an EXPECTATION
        because `admit()` recomputes the same digest on the other side.
      * A run-time binding of any kind. This is a rule over SOURCES: it is
        author-visible, not author-proof.
    """
    tests = os.path.dirname(os.path.abspath(__file__))
    offenders = []
    for name in sorted(os.listdir(tests)):
        if not name.endswith(".py"):
            continue
        with open(os.path.join(tests, name), encoding="utf-8") as handle:
            offenders.extend(stand_in_offenders(name, handle.read()))
    assert offenders == [], "\n".join(offenders)
    # …and the rule is LIVE, against the shape round 16 found and the shape
    # round 15 fixed. A source lint asserted only over sources that satisfy it
    # is a lint nobody has seen fire.
    for what, source in INHERITING_BUILDERS:
        assert stand_in_offenders("stand-in.py", source), what
    # …and it is not a rule that fires on everything, which would satisfy the
    # controls above and mean nothing. The correct shapes stay silent.
    for what, source in CORRECT_BUILDERS:
        assert stand_in_offenders("stand-in.py", source) == [], what


# Every shape the scan has been measured staying GREEN under — round 16's
# three, round 17's four, round 18's five. Each is spliced onto a copy of a
# writing module's source and must come back as a NAMED offender at a line past
# that module's own last one: a fail-closed claim that is not itself tested is
# the same sentence in a docstring the round before.
FAIL_CLOSED_SPLICES = (
    ("an API outside the vocabulary",
     "def _sneak_one(root):\n"
     "    return tempfile.mkstemp(dir=root, prefix='SNEAK', suffix='.md')\n"),
    ("an open() whose mode is not a literal",
     "def _sneak_two(root, mode):\n"
     "    return open(os.path.join(root, 'SNEAK2.md'), mode)\n"),
    ("a write at module level",
     "_SNEAK_THREE = open(os.path.join('/sneak', 'SNEAK3.md'), 'w')\n"),
    ("a writer reached under another name",
     "from tempfile import mkstemp\n"),
    # Round 17, finding 4. The four above are round 16's, and the entry
    # immediately above names a SHAPE — "a writer reached under another name" —
    # while testing one spelling of it. These are the spellings that shape has
    # that the round-16 code did not close, plus the flag-set hole one function
    # over and the computed-callee hole one function further still. A shape
    # claimed and a spelling tested is what this round is a disposition of.
    ("an os.open() whose flag set is not readable",
     "def _sneak_five(root, flags):\n"
     "    return os.open(os.path.join(root, 'SNEAK5.md'), flags, 0o600)\n"),
    ("a writer bound to another name by assignment",
     "_sneak_alias = open\n"
     "def _sneak_six(root):\n"
     "    return _sneak_alias(os.path.join(root, 'SNEAK6.md'), 'w')\n"),
    ("a filesystem module bound to another name by assignment",
     "_sneak_module = os\n"
     "def _sneak_seven(root):\n"
     "    return _sneak_module.replace('/x', os.path.join(root, 'SNEAK7.md'))\n"),
    ("a writer reached through a computed callee",
     "def _sneak_eight(root):\n"
     "    return getattr(os, 'replace')('/x', os.path.join(root, 'SNEAK8.md'))\n"),
    # Round 18, finding 4. The eight above drive four of the five clauses the
    # bullet below used to make; the fifth — "not by any other binding form" —
    # was driven by nothing and was false in twelve measured spellings. These
    # are one per MECHANISM rather than one per spelling, because the rules are
    # `symtable` and `callable()` now and a spelling is not what either of them
    # decides on: a binding target that is not a simple name, a parameter, a
    # rebinding through a NON-filesystem import (which the import limbs
    # structurally cannot see), a primitive escaping as a value with no
    # assignment statement anywhere, and the one existing clause — `import
    # tempfile as t` — that had a limb and no splice.
    ("a binding target that is not a simple name",
     "for open, _sneak_nine in ((1, 2),):\n"
     "    pass\n"),
    ("a filesystem name bound as a parameter",
     "def _sneak_ten(open):\n"
     "    return open\n"),
    ("`open` rebound through a NON-filesystem import",
     "import json as open\n"),
    ("a writer escaping as a value, with no assignment",
     "def _sneak_eleven(root, _replace=os.replace):\n"
     "    return _replace('/x', root)\n"),
    ("a filesystem module reached under an import alias",
     "import tempfile as _sneak_twelve\n"),
)


def test_the_writer_scan_fails_closed_on_what_it_cannot_read():
    """The enforcement, so "it fails CLOSED" is a property and not a sentence.

    Round 16, finding 3 spliced three covered-byte writes into a writing module
    and both scan cases stayed green: an unknown creator was skipped, a
    variable `open()` mode was classified as non-creating, and module level was
    never walked. A fourth shape — reaching a creator under a bare name —
    defeats the dotted-spelling match the whole scan rests on. Each is required
    to produce an offender naming the line it was spliced at.

    Round 17, finding 4 added three more, and the reason they are here rather
    than in a sentence is the finding itself: the fourth entry NAMES a shape,
    "a writer reached under another name", and drove one spelling of it. An
    assignment alias of a writer, an assignment alias of a filesystem module
    and a computed callee are three more spellings of that same shape, and an
    `os.open()` whose flag set is a variable was a fourth independent
    fail-open. The rule this file now works to: a disposition may not name a
    CLASS as closed unless the class's boundary is driven, and where it is not
    driven, the spellings that ARE driven are the claim.

    Round 18, finding 4 applied that rule to this file's own record and it
    failed: the alias bullet made five clauses, `FAIL_CLOSED_SPLICES` drove
    three of them, and the undriven clause — "not by any other binding form" —
    was false in twelve spellings. Five more splices, one per mechanism rather
    than one per spelling, and the count is pinned below so that a clause
    cannot be added to the claim without a splice being added to the drive."""
    assert len(FAIL_CLOSED_SPLICES) == 13, len(FAIL_CLOSED_SPLICES)
    for module in WRITING_MODULES:
        with open(module.__file__, encoding="utf-8") as handle:
            source = handle.read()
        original = len(source.splitlines())
        base_sites, base_offenders = scan_source(module.__name__, source)
        # The fixture is live: the unspliced module is classifiable throughout.
        assert base_offenders == [], module.__name__
        for what, splice in FAIL_CLOSED_SPLICES:
            sites, offenders = scan_source(module.__name__,
                                           source + "\n\n" + splice)
            # Caught either as an unclassifiable call or as a write site the
            # destination case then has to resolve — and at a line past the
            # module's own last one, so it is the SPLICE that was caught and
            # not something the module already carried.
            lines = [int(offender.split(":")[1].split(" ")[0])
                     for offender in offenders]
            lines += [line for line, _scope, _root, _tail in sites
                      if (line, _scope, _root, _tail) not in base_sites]
            assert lines and max(lines) > original, (module.__name__, what,
                                                     offenders, sites)
