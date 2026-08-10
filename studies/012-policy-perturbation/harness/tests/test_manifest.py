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

Six assertions:

1. a file-shaped entry excludes that path and no descendant of it — including
   the two `MANIFEST_CARRIERS`, which the same widening covered;
2. a tree-shaped entry excludes its subtree, does NOT excuse its own bare name,
   and does not reach a sibling whose name it merely prefixes (`arms/AA/`);
3. the registered list keeps its registered SHAPE — eight files and seven
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
   scoring and the publication. That is what makes §2.10 rule 3 terminate, and
   it is asserted here by applying each act to a copy of the tree rather than
   argued in prose.

Tests 4 and 6 are the only tests in the suite that run `git`. They are offline,
they run inside `fixtures.throwaway_root()` and write nothing into the
committed tree, and they need no git identity because only the index is ever
read — `git add` without a commit is enough for `git ls-files`. Tests 5 and 6
read the committed tree through `git ls-files`; test 6 copies it and writes
only inside its own throwaway root.
"""
from __future__ import annotations
import json
import os
import shutil
import subprocess

import fixtures
import integrity


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
        "DEVIATIONS.md", "arms/BATCH.json", "arms/SHORTFALL.json",
        "transcription/GOLDEN-CONTEXT.json"}
    assert trees == {
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
    complete. What this case adds is that a future output added without an
    entry in `freeze.excluded` fails here, whatever it is called.

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
                         "ANALYSIS.md", "DEVIATIONS.md"):
                _write(root, name, "the run's output\n")

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
    assert len(files) == 10
    hidden = [(name, entry) for entry in files for name in _tracked(study)
              if name.startswith(entry + "/")]
    assert hidden == []
