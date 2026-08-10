#!/usr/bin/env python3
"""Round 12, finding 9. `README.md`'s review-status block copies a count that
another file holds, and a hand-copied count of a growing number goes stale:
this block was flagged in rounds 5, 6, 8, 10 and 12, and `PREREG-REVIEW.md`'s
own status line sat at "two rounds" through round 9 — it says so itself.

Nothing could ever catch it. `PREREG-REVIEW.md` is one of the two manifest
carriers excluded inside `integrity.tree_manifest()`, so appending a round
record moves no digest anywhere; the README's copy is inside the manifest but
the fact that it copies is not. Only a test can see the two drift apart.

So the count stops being maintained and starts being derived. The round
headings in `PREREG-REVIEW.md` are the fact, and every status sentence is
checked against them. This does more than detect staleness: it names the value
the editing commit must write, which is the value AT THAT COMMIT — the commit
that appends round N's record is the commit that must say N.
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
# The full-tree binding applies from round 3 on (§2.10 [D-20]).
FIRST_POST_PORT_ROUND = 3


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


def test_the_readme_review_status_equals_the_rounds_on_record():
    total = rounds_recorded()
    sentence = ("**Review status: %s rounds recorded, rounds 2-%d "
                "cross-vendor.**" % (COUNT_WORDS[total], total))
    assert sentence in _flowed(_read("README.md")), (
        "README.md's review-status line is out of step with PREREG-REVIEW.md's "
        "%d round headings. It must read exactly:\n%s" % (total, sentence))


def test_the_readme_post_port_span_ends_at_the_last_round():
    total = rounds_recorded()
    span = ("rounds %d-%d over the complete post-port candidate tree"
            % (FIRST_POST_PORT_ROUND, total))
    assert span in _flowed(_read("README.md")), (
        "README.md's post-port span is out of step; it must read: %s" % span)


def test_the_records_own_status_line_equals_its_own_headings():
    total = rounds_recorded()
    sentence = ("**Status: OPEN. %s rounds complete, rounds 2 through %d "
                "cross-vendor." % (COUNT_WORDS[total].capitalize(), total))
    assert sentence in _flowed(_read("PREREG-REVIEW.md")), (
        "PREREG-REVIEW.md's own status line is out of step with its own round "
        "headings. It must read: %s" % sentence)


def test_round_one_is_internal_and_round_two_is_the_first_cross_vendor():
    """The literal 2 in both status sentences is a fact about the record, not a
    constant: round 1 is internal, round 2 is the first cross-vendor round."""
    headings = re.findall(r"^#{1,6} Round \d+ — .*$",
                          _read("PREREG-REVIEW.md"), re.M)
    assert "internal" in headings[0], headings[0]
    assert "cross-vendor" in headings[1], headings[1]
