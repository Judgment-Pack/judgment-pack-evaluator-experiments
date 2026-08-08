#!/usr/bin/env python3
"""§6 C3 clause 2 — the census port, replication-controlled against Study 011's
published numbers.

C3 registers the census as a REPLICATION control rather than a reviewed one:
"the ported `harness/census.py` is run over Study 011's retained valid slots
and must reproduce that study's published headline exactly: 49 runs × 16
accepted records = 784, 0 dropped, distinct probes per class (2, 6, 2, 24, 26,
2), 410 of 784 records on or within 0.01 of a named threshold, and an empty
[23.75, 39) approach band. The census is a registered secondary in this study,
so its port is replication-controlled against the numbers `DIVERSITY.md`
published rather than reviewed by eye."

That is what this file does, and it is the only test in the suite that reads
another study's tree. It reads and never writes. The numbers below are
transcribed from Study 011's `DIVERSITY.md` and `RESULTS.json`, which were
published before this port existed; a port that agreed with itself and not with
them would pass nothing here.

The census is run at (40, 70) — Study 011's pair, which is arms A, B, C and E's
— over the six predicates of the family this study's arm A carries, after
checking that those bytes ARE Study 011's family bytes. §6 C1 binds that
equality already; it is re-derived here because a census over a different
family would be a census of something else.
"""
from __future__ import annotations
import hashlib
import json
import os
from decimal import Decimal

import pytest

import census

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(os.path.dirname(HERE))
ELEVEN = os.path.normpath(os.path.join(STUDY, "..", "011-authorship-coverage-rates"))

# Study 011's published headline (DIVERSITY.md and RESULTS.json), transcribed.
PUBLISHED = {
    "runs": 49,
    "recordsPerRun": 16,
    "records": 784,
    "h": 784,
    "q": 0,
    "probesPerClass": [2, 6, 2, 24, 26, 2],
    "onOrWithin001": 410,
    "humanGap": 4,
    "buckets": {"exactly on an edge": 181, "0 < d <= 0.001": 84,
                "0.001 < d <= 0.01": 145, "0.01 < d <= 0.1": 1,
                "0.1 < d <= 1": 3, "d > 1": 370},
    # DIVERSITY.md §B, per edge: (records strictly below within 1.0, exactly
    # at, strictly above within 1.0).
    "nearEdge": {"39": (0, 0, 192), "40": (89, 103, 3), "70": (100, 78, 41)},
    # The nearest approach from below anywhere in the corpus, which is what
    # leaves [23.75, 39) empty.
    "nearestBelow39": Decimal("23.75"),
}


def _digest(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


@pytest.fixture(scope="module")
def eleven():
    """Study 011's retained records — one directory per valid slot, holding
    that run's accepted records as the compiler wrote them — with the corpus
    bound to 011's own published population before anything is counted.

    Skipped, with the reason stated, when the sibling study is not checked out
    beside this one: C3 is a control on the port, and a port cannot be
    replication-controlled against a corpus that is not there.
    """
    records_root = os.path.join(ELEVEN, "records")
    results_path = os.path.join(ELEVEN, "RESULTS.json")
    if not os.path.isdir(records_root) or not os.path.isfile(results_path):
        pytest.skip("Study 011's retained records are not present at %s: C3 "
                    "clause 2 needs that study's own corpus and this checkout "
                    "does not carry it" % records_root)
    with open(results_path) as handle:
        results = json.load(handle)
    runs = {}
    for slot in sorted(os.listdir(records_root)):
        directory = os.path.join(records_root, slot, "records")
        runs[slot] = [json.load(open(os.path.join(directory, name)))
                      for name in sorted(os.listdir(directory))]
    published_accepted = {row["slot"]: row["accepted"] for row in results["runs"]
                          if row["valid"]}
    assert {slot: len(records) for slot, records in runs.items()} \
        == published_accepted, (
        "the retained records are not the population Study 011 published")
    family_path = os.path.join(ELEVEN, "FAMILY.json")
    assert _digest(family_path) == _digest(os.path.join(STUDY, "arms", "A",
                                                        "FAMILY.json")), (
        "this study's arm A family is not Study 011's family bytes, so a "
        "census over it would not be a replication of 011's")
    with open(family_path) as handle:
        family = json.load(handle)
    classes = [{"index": mutation["index"], "title": mutation["title"],
                "predicate": mutation["predicate"],
                "predicateProse": mutation["predicateProse"]}
               for mutation in family["mutations"]]
    return {"runs": runs, "classes": classes,
            "embargo": tuple(family["embargoList"]), "results": results}


@pytest.fixture(scope="module")
def replicated(eleven):
    return census.census("A", eleven["runs"], eleven["classes"],
                         eleven["embargo"], "40", "70")


def test_the_population_is_the_one_study_011_published(replicated, eleven):
    """49 runs × 16 accepted records = 784, 0 dropped."""
    population = replicated["population"]
    assert population["runs"] == PUBLISHED["runs"]
    assert population["records"] == PUBLISHED["records"]
    assert population["recordsPerRun"] == {"min": PUBLISHED["recordsPerRun"],
                                           "max": PUBLISHED["recordsPerRun"]}
    assert PUBLISHED["runs"] * PUBLISHED["recordsPerRun"] == PUBLISHED["records"]
    # "0 dropped": every record 011 retained was an accepted one, and its own
    # published rows say so run by run.
    assert sum(row["dropped"] for row in eleven["results"]["runs"]
               if row["valid"]) == 0


def test_the_ported_mirror_labels_the_corpus_as_study_011_published_it(replicated,
                                                                       eleven):
    """The H/Q split at (40, 70) — the parameterized mirror against a number a
    predecessor already published, which is the point of running the port over
    someone else's corpus."""
    assert replicated["population"]["h"] == PUBLISHED["h"]
    assert replicated["population"]["q"] == PUBLISHED["q"]
    assert eleven["results"]["labelAccuracy"]["h"] == PUBLISHED["h"]
    assert eleven["results"]["labelAccuracy"]["q"] == PUBLISHED["q"]


def test_the_distinct_probes_per_class_are_the_published_two_six_two(replicated):
    """X1's headline, and the number this study's arm A will be read against:
    (2, 6, 2, 24, 26, 2)."""
    assert [row["probes"] for row in replicated["x1"]["classes"]] \
        == PUBLISHED["probesPerClass"]
    assert replicated["x1"]["runs"] == PUBLISHED["runs"]


def test_the_hugging_count_is_410_of_784(replicated):
    """X2: 410 of 784 records sit on a named threshold or within 0.01 of one,
    and exactly 4 land in the human-sized gap."""
    assert replicated["x2"]["records"] == PUBLISHED["records"]
    assert replicated["x2"]["onOrWithin001"] == PUBLISHED["onOrWithin001"]
    assert replicated["x2"]["humanGap"] == PUBLISHED["humanGap"]
    assert replicated["x2"]["buckets"] == PUBLISHED["buckets"]


def test_the_approach_band_below_39_is_empty(replicated, eleven):
    """X3's finding, and the one C3 names: nothing lies within 1.0 below the
    UNSTATED 39 edge, and the nearest approach from below anywhere in the
    corpus is 23.75 — so the whole band [23.75, 39) is empty."""
    rows = {row["edge"]: row for row in replicated["x3"]["edges"]}
    assert sorted(rows) == ["39", "40", "70"]
    for edge, (below, at, above) in PUBLISHED["nearEdge"].items():
        assert (rows[edge]["belowCount"], rows[edge]["at"],
                rows[edge]["aboveCount"]) == (below, at, above), edge
    assert rows["39"]["below"] == [], "a record inside [38, 39) would refute it"
    assert rows["39"]["stated"] == "unstated"
    scores = sorted({Decimal(record["vendor"]["riskScore"])
                     for records in eleven["runs"].values()
                     for record in records})
    below = [value for value in scores if value < Decimal("39")]
    assert max(below) == PUBLISHED["nearestBelow39"]
    assert not [value for value in scores
                if PUBLISHED["nearestBelow39"] < value < Decimal("39")]
