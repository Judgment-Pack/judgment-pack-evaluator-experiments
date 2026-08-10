#!/usr/bin/env python3
"""Round 13, finding 1, and round 12's finding 9 kept in a home that can hold
it. The count of review rounds is a value that moves once per round, and round
12 put a copy of it in `README.md` — which `integrity.tree_manifest()` covers.
Recording round N then changed a covered byte, §2.10 rule 3 answered that with
round N+1, and recording THAT round was the same change again: a tree with this
binding in it can never be frozen, because the act of writing down the round
that would freeze it moves the digest that round attested.

So the count is not checked in a covered file — it is not written in one. The
round headings in `PREREG-REVIEW.md` are the fact; `PREREG-REVIEW.md` is one of
the two carriers `integrity.tree_manifest()` excludes; and every sentence that
copies the count lives inside it, where appending a round moves no digest
anywhere. `README.md` points at the record instead of copying it, and a lint
here keeps the copy from coming back.

What round 12 wanted is kept and costs nothing: the record's own status line is
still diffed against the record's own round headings, both sides carrier bytes.
Its status WORD is a registered set rather than a constant, because pinning it
to `OPEN` put the only sayable status inside the manifest too — the record could
not say it had closed without a covered edit, hence another round.

The count was one instance of a wider class. A covered sentence about where the
study STANDS is unfreezable for exactly the same reason: the act that falsifies
it — the freeze, the golden recapture, the batch, the scoring — is a registered
act, and rule 3 forbids the repair afterwards. The second lint below
generalizes the first from the count to the status, and registers its own
weakness where it stands.
"""
from __future__ import annotations
import os
import re
import subprocess

import integrity

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
STUDY = os.path.dirname(HARNESS)
# This file's own path inside the study, because the list below is written out
# here and a lint that reads its own vocabulary reports itself.
SELF = "harness/tests/test_review_status.py"

# The record's own heading convention: `# Round N — ...` at any depth (rounds
# 1-2 are `#`, rounds 3 on are `##`).
ROUND_HEADING = re.compile(r"^#{1,6} Round (\d+)\b", re.M)
COUNT_WORDS = (
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen", "twenty",
)
# The record's status is the record's to set: OPEN while further rounds may be
# commissioned, CLOSED once the final round has ended clean and the freeze binds
# to its manifest. Registered as a set, checked as exactly one.
STATUS_WORDS = ("OPEN", "CLOSED")
# The idioms that carry a review-round count. README.md may contain none of
# them; they are the four phrasings the covered copy has actually taken.
REVIEW_COUNT_IDIOMS = (
    r"rounds?\s+recorded",
    r"rounds?\s+complete\b",
    r"rounds\s+2\s*(?:-|–|through)\s*\d",
    r"rounds\s+3\s*(?:-|–|through)\s*\d",
)
# The pointer that replaces the copy. Static: it names no round and no count, so
# no review round can make it stale.
README_POINTER = ("**Review status: [`PREREG-REVIEW.md`](PREREG-REVIEW.md) is "
                  "the count.**")
# The generalization of the same defect, from the count to the STATUS. Each of
# these is a sentence about where the study stands that a registered act of the
# ceremony falsifies; each was found in a covered file by the pre-freeze sweep,
# and the act that falsifies it is named beside it.
COVERED_LIFECYCLE_IDIOMS = (
    "nothing has run",          # the golden recapture, then the batch
    "freeze pending",           # the freeze
    "none of it is frozen",     # the freeze
    "none exists yet",          # the scoring and the publication
    "has not yet ended clean",  # the final round ending clean
    "this tree has not had",    # the freeze
    "is not a file yet",        # the golden recapture
)


def _read(name):
    with open(os.path.join(STUDY, name), encoding="utf-8") as handle:
        return handle.read()


def _flowed(text):
    """Markdown prose is hard-wrapped, so a sentence is a run of words rather
    than a run of bytes: a longer count word reflows the paragraph, and that
    must not be what fails."""
    return " ".join(text.split())


def rounds_recorded():
    numbers = [int(match.group(1))
               for match in ROUND_HEADING.finditer(_read("PREREG-REVIEW.md"))]
    assert numbers == list(range(1, len(numbers) + 1)), (
        "PREREG-REVIEW.md's round headings are not 1..N contiguous — a round "
        "heading must read `# Round N — ...`: %r" % (numbers,))
    assert len(numbers) >= 11, numbers
    return len(numbers)


def test_the_records_own_status_line_equals_its_own_headings():
    """Carrier against carrier: PREREG-REVIEW.md's status sentence against
    PREREG-REVIEW.md's own round headings. Both sides are outside the manifest,
    so this check is free — recording a round updates both and moves no
    covered byte."""
    total = rounds_recorded()
    flowed = _flowed(_read("PREREG-REVIEW.md"))
    wanted = ["**Status: %s. %s rounds complete, rounds 2 through %d "
              "cross-vendor." % (word, COUNT_WORDS[total].capitalize(), total)
              for word in STATUS_WORDS]
    matched = [sentence for sentence in wanted if sentence in flowed]
    assert len(matched) == 1, (
        "PREREG-REVIEW.md's own status line is out of step with its own %d "
        "round headings, or names an unregistered status. It must read exactly "
        "one of:\n%s" % (total, "\n".join(wanted)))


def test_the_readme_copies_no_review_count():
    """README.md is inside the tree manifest. A review-round count in it makes
    recording a round a covered-byte change, and §2.10 rule 3 answers a
    covered-byte change with another review round — whose recording is the same
    change again. The count may not live here at all."""
    flowed = _flowed(_read("README.md"))
    for pattern in REVIEW_COUNT_IDIOMS:
        found = re.search(pattern, flowed, re.I)
        assert found is None, (
            "README.md is covered by the tree manifest and PREREG-REVIEW.md is "
            "not, so the review-round count lives in the record and is pointed "
            "at from here, never copied: %r (§2.10 rule 3, round 13 finding 1)"
            % (found.group(0),))


def test_the_readme_points_at_the_record():
    assert README_POINTER in _flowed(_read("README.md")), (
        "README.md must point at the review record where the count lives. It "
        "must read: %s" % README_POINTER)


def _covered(pins) -> list:
    """§2.10's covered set, from the same three inputs the manifest uses: the
    tracked list, the registry's `freeze.excluded`, and the two carriers."""
    listing = subprocess.run(["git", "ls-files", "-z", "--", "."], cwd=STUDY,
                             capture_output=True, check=True)
    excluded = tuple(pins["freeze"]["excluded"]) + integrity.MANIFEST_CARRIERS
    return [name for name in listing.stdout.decode("utf-8").split("\0")
            if name and not integrity.manifest_excluded(name, excluded)]


def test_no_covered_file_states_where_the_study_stands(pins):
    """The count was one instance; the class is STATUS. §2.10 rule 3 forbids
    correcting a covered byte after the final round, and every registered act
    from the freeze to publication moves carrier or excluded bytes only — so a
    covered sentence asserting where the study stands is false from the act
    that falsifies it onward, with no lawful repair. The freeze falsifies
    "freeze pending"; the golden recapture falsifies "nothing has run" one step
    AFTER the freeze, when rule 3 already binds.

    The register, honestly: **this is a blacklist and a blacklist cannot be
    complete.** These are the seven idioms the pre-freeze sweep actually found
    in covered files, and a replacement can be written past every one of them.
    What closes the class is §2.10's own registered sentence, plus
    `test_manifest.py`'s positive property that no registered act moves a
    covered byte, plus the reviewer; this case is the cheap guard that stops
    these seven from coming back, in the same file and for the same reason as
    the review-count lint above.

    Two exclusions, both stated rather than silent. `arms/` is locked bytes
    whose inherited prose §2.6 and §9 register, and this file is skipped
    because the vocabulary is written out here.
    """
    offenders = []
    for name in _covered(pins):
        if name.startswith("arms/") or name == SELF:
            continue
        path = os.path.join(STUDY, name)
        if not os.path.isfile(path) or os.path.islink(path):
            continue
        with open(path, "rb") as handle:
            body = _flowed(handle.read().decode("utf-8", "replace")).lower()
        offenders += [(name, idiom) for idiom in COVERED_LIFECYCLE_IDIOMS
                      if idiom in body]
    assert offenders == [], (
        "a manifest-covered file says where the study stands, and §2.10 rule "
        "3 forbids correcting it once the final round has read it — point at "
        "`harness/PINS.json`'s lifecycle members or at `PREREG-REVIEW.md`'s "
        "status line instead: %r" % (offenders,))


def test_round_one_is_internal_and_round_two_is_the_first_cross_vendor():
    """The literal 2 in the status sentence is a fact about the record, not a
    constant: round 1 is internal, round 2 is the first cross-vendor round."""
    headings = re.findall(r"^#{1,6} Round \d+ — .*$",
                          _read("PREREG-REVIEW.md"), re.M)
    assert "internal" in headings[0], headings[0]
    assert "cross-vendor" in headings[1], headings[1]
