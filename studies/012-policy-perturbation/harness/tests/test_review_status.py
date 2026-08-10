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
"""
from __future__ import annotations
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
STUDY = os.path.dirname(HARNESS)

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


def test_round_one_is_internal_and_round_two_is_the_first_cross_vendor():
    """The literal 2 in the status sentence is a fact about the record, not a
    constant: round 1 is internal, round 2 is the first cross-vendor round."""
    headings = re.findall(r"^#{1,6} Round \d+ — .*$",
                          _read("PREREG-REVIEW.md"), re.M)
    assert "internal" in headings[0], headings[0]
    assert "cross-vendor" in headings[1], headings[1]
