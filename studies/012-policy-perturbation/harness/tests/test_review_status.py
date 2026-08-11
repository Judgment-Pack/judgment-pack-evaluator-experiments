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
import json
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
# The one manifest entry that is not a tracked file: `tree_manifest()`
# appends the registry's normalized projection under this name.
NORMALIZED = "harness/PINS.json#normalized"

# The record's own heading convention: `# Round N — ...` at any depth (rounds
# 1-2 are `#`, rounds 3 on are `##`).
ROUND_HEADING = re.compile(r"^#{1,6} Round (\d+)\b", re.M)
# A convenience the record MAY use, never the vocabulary it must use: a word
# table has a last entry, and an expectation whose domain ends inside a covered
# file is the round-13 livelock one act later. `_count_renderings()` below is
# what makes the expectation total in the count (round 15, finding 3).
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
# §8's falsification commitment has four venues, and one of them is a covered
# file. The README carries a POINTER written before the data instead of the
# sentence written after it — same defect, same remedy, one act later (round
# 14, finding 2). `CORRECTION.md` is a `freeze.excluded` output, written in
# every outcome, so this link is frozen and can never come loose lawfully.
CORRECTION_POINTER = ("at the head of [`CORRECTION.md`](CORRECTION.md), "
                      "linked from this block")
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


def _count_renderings(total):
    """Every rendering of the count the record's status line may use. A word
    table has a last entry, and a covered file the record can outgrow puts the
    round-13 livelock back one act later: past the table, recording a round
    needs an edit HERE, and rule 3 answers that with another round. The numeral
    is defined for every N, so the table is a convenience the record may use and
    never a ceiling (round 15, finding 3)."""
    renderings = [str(total)]
    if total < len(COUNT_WORDS):
        renderings.append(COUNT_WORDS[total].capitalize())
    return renderings


def _read(name):
    with open(os.path.join(STUDY, name), encoding="utf-8") as handle:
        return handle.read()


def _flowed(text):
    """Markdown prose is hard-wrapped, so a sentence is a run of words rather
    than a run of bytes: a longer count word reflows the paragraph, and that
    must not be what fails."""
    return " ".join(text.split())


def _strings(node):
    """Every string in a JSON structure, keys included."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _strings(value)
    elif isinstance(node, str):
        yield node


def _lifecycle_hits(name, text) -> list:
    body = _flowed(text).lower()
    return [(name, idiom) for idiom in COVERED_LIFECYCLE_IDIOMS
            if idiom in body]


def _projection_hits(pins) -> list:
    """The registry as the MANIFEST binds it, not as the file holds it.
    Round-tripped through `integrity.normalized_pins()` so the scanned object
    IS the projected one by construction; read as values rather than as bytes
    because the projection is serialized with `ensure_ascii=True`, and a
    `\\u00a0` inside a phrase would survive a byte scan."""
    projected = json.loads(integrity.normalized_pins(pins))
    return _lifecycle_hits(NORMALIZED, " ".join(_strings(projected)))


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
              "cross-vendor." % (word, count, total)
              for word in STATUS_WORDS
              for count in _count_renderings(total)]
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


def test_the_readme_points_at_the_correction():
    """The same shape as the pointer above, at the publishing act. §8 registers
    a README venue for an R1-UNSUPPORTED correction, and README.md is covered
    by the manifest — so writing the correction there after the data is both
    the covered-byte change rule 3 forbids and the status assertion rule 3's
    second clause forbids. The venue is a pre-data link to `CORRECTION.md`,
    which is a `freeze.excluded` output; this lint is what makes the link
    permanent, because dropping it fails here before it moves the digest."""
    assert CORRECTION_POINTER in _flowed(_read("README.md")), (
        "README.md must link the correction venue §8 registers, in the block "
        "that states the commitment. It must read: %s" % CORRECTION_POINTER)


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

    The register, honestly, in two parts.

    **Scope.** What is scanned is what the manifest BINDS, which is not the
    same as what git tracks: the covered files, plus `harness/PINS.json`'s
    normalized projection, which `integrity.tree_manifest()` appends as an
    entry of its own and in which everything but the four post-freeze members
    is byte-significant. A status sentence in a registry NOTE is therefore
    exactly as unrepairable as one in `README.md`, and the file is a carrier
    only in the sense that its four lifecycle VALUES may move. Two bound
    entries are skipped and both are stated rather than silent: `arms/` is
    locked bytes whose inherited prose §2.6 and §9 register, and this file is
    skipped because the vocabulary is written out here. `PREREG-REVIEW.md` is
    not scanned and must not be — it is the record, its bytes are appendable
    by rule, and it says "nothing has run" on purpose.

    **Phrases.** This is a blacklist and a blacklist cannot be complete. These
    are the seven idioms the pre-freeze sweep actually found in covered files,
    and a replacement can be written past every one of them. What closes the
    class is §2.10's own registered sentence, plus `test_manifest.py`'s
    positive property that no registered act moves a covered byte, plus the
    reviewer; this case is the cheap guard that stops these seven from coming
    back, in the same file and for the same reason as the review-count lint
    above.
    """
    offenders = []
    for name in _covered(pins):
        if name.startswith("arms/") or name == SELF:
            continue
        path = os.path.join(STUDY, name)
        if not os.path.isfile(path) or os.path.islink(path):
            continue
        with open(path, "rb") as handle:
            offenders += _lifecycle_hits(
                name, handle.read().decode("utf-8", "replace"))
    offenders += _projection_hits(pins)
    assert offenders == [], (
        "a manifest-covered file says where the study stands, and §2.10 rule "
        "3 forbids correcting it once the final round has read it — point at "
        "`harness/PINS.json`'s four post-freeze MEMBERS, whose values the "
        "projection nulls — a registry NOTE is bound like any covered byte — "
        "or at `PREREG-REVIEW.md`'s status line instead: %r" % (offenders,))


def test_the_projection_scan_catches_a_status_line_in_a_registry_note(pins):
    """Scope, asserted. The projection is in the manifest, so it is in the
    lint; the four members the projection nulls are not, because a value the
    ceremony writes after the freeze moves no digest."""
    planted = json.loads(json.dumps(pins))
    planted["freeze"]["note"] += " Freeze pending."
    assert _projection_hits(planted) == [(NORMALIZED, "freeze pending")]
    assert _projection_hits(pins) == []


def test_the_status_line_check_has_no_round_ceiling():
    """The expectation must be total in the round count. A lookup table with a
    last entry is a covered file the record outgrows, and past it the only
    repair is a covered edit — the round-13 livelock one act later. Stage-free
    by construction: the counts probed are constants about the table, not the
    live count (§2.10 rule 3, round 15 finding 3)."""
    for total in (0, len(COUNT_WORDS) - 1, len(COUNT_WORDS), 10 ** 4):
        assert str(total) in _count_renderings(total), total


def test_round_one_is_internal_and_round_two_is_the_first_cross_vendor():
    """The literal 2 in the status sentence is a fact about the record, not a
    constant: round 1 is internal, round 2 is the first cross-vendor round."""
    headings = re.findall(r"^#{1,6} Round \d+ — .*$",
                          _read("PREREG-REVIEW.md"), re.M)
    assert "internal" in headings[0], headings[0]
    assert "cross-vendor" in headings[1], headings[1]
