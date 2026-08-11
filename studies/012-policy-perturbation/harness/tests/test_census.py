#!/usr/bin/env python3
"""§6 C3 clause 2 — the census port, replication-controlled against Study 011's
published numbers.

C3 registers the census as a REPLICATION control rather than a reviewed one:
"the ported `harness/census.py` is run over Study 011's retained valid slots
and must reproduce that study's published headline exactly: 49 runs × 16
accepted records = 784, 0 dropped, distinct probes per class (2, 6, 2, 24, 26,
2), 410 of 784 records on or within 0.01 of a named threshold, and an empty
(23.75, 39) approach band. The census is a registered secondary in this study,
so its port is replication-controlled against the numbers `DIVERSITY.md`
published rather than reviewed by eye."

That is what this file does, and it is the only test in the suite that reads
another study's tree. It reads and never writes. The numbers below are
transcribed from Study 011's `DIVERSITY.md` and `RESULTS.json`, which were
published before this port existed; a port that agreed with itself and not with
them would pass nothing here.

Round 5, finding 9 adds a second section at the foot of the file, over records
this file builds rather than over 011's: §4.5 registers three census surfaces
011 never published — X3's full value distribution, X4's distribution over
whole-run multisets, and arm D's old-edge tables at 40 and 70 — so a replication
control against 011's numbers cannot pin them and something has to. The
replication above is untouched: every number C3 clause 2 names is an aggregate
count, and the new members sit beside them rather than in them.

The census is run at (40, 70) — Study 011's pair, which is arms A, B, C and E's
— over the six predicates of the family this study's arm A carries, after
checking that those bytes ARE Study 011's family bytes. §6 C1 binds that
equality already; it is re-derived here because a census over a different
family would be a census of something else.
"""
from __future__ import annotations
import collections
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
    # leaves (23.75, 39) empty.
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
    corpus is 23.75 — so the whole open band (23.75, 39) is empty."""
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


def test_the_full_value_distribution_covers_the_whole_corpus(replicated, eleven):
    """X3's full distribution over 011's own records (round 5, finding 9).

    The near-edge tables are the anticipated neighbourhood; the distribution is
    every value, and 23.75 — the nearest approach from below, which is 15.25
    away from the 39 edge and in no near-edge table — is the corpus's own proof
    that the two are not the same publication.
    """
    x3 = replicated["x3"]
    assert sum(count for _value, count in x3["values"]) == PUBLISHED["records"]
    assert x3["records"] == PUBLISHED["records"]
    assert x3["distinctValues"] == len(x3["values"])
    published = {value: count for value, count in x3["values"]}
    # Counted again here, off 011's retained records and not off the census.
    independent = collections.Counter(
        str(Decimal(record["vendor"]["riskScore"]))
        for records in eleven["runs"].values() for record in records)
    assert published == dict(independent)
    # 23.75 is in the distribution and in NO near-edge table: 15.25 from the
    # nearest edge is exactly the distance the near-edge tables cannot see, and
    # it is the value C3's own clause is about.
    assert str(PUBLISHED["nearestBelow39"]) in published
    near_edge_values = {value for row in x3["edges"]
                        for value, _count in row["below"] + row["above"]}
    assert str(PUBLISHED["nearestBelow39"]) not in near_edge_values
    assert near_edge_values < set(published)
    # Ascending, by value and not by string: "9.5" sorts after "40" as text.
    assert [Decimal(value) for value, _count in x3["values"]] \
        == sorted(Decimal(value) for value, _count in x3["values"])
    # Every near-edge value is in the distribution, at the same count: the two
    # tables are one population read two ways.
    for row in x3["edges"]:
        for value, count in row["below"] + row["above"]:
            assert published[value] == count, (row["edge"], value)


def test_study_011_is_not_an_arm_d_and_publishes_no_old_edge_table(replicated):
    """The old-edge table is arm D's alone: 40 and 70 are this census's own
    edges here, and a second copy of them under another name would be the same
    table published twice."""
    assert "oldEdges" not in replicated["x3"]


def test_the_run_multiset_distribution_accounts_for_every_run(replicated):
    """X4's `groups` over 011's corpus: the distribution, not its shape. Every
    run is in exactly one group, the group sizes agree with the aggregates that
    were published before them, and the order is deterministic."""
    for key in ("profile", "probe"):
        signature = replicated["x4"]["signatures"][key]
        counts = [group["runs"] for group in signature["groups"]]
        assert sum(counts) == PUBLISHED["runs"], key
        assert len(counts) == signature["distinct"], key
        assert sorted((count for count in counts if count > 1), reverse=True) \
            == signature["groupSizes"], key
        assert sum(count for count in counts if count > 1) \
            == signature["runsSharing"], key
        assert sum(1 for count in counts if count == 1) \
            == signature["singletons"], key
        assert counts == sorted(counts, reverse=True), key
        assert len({group["signature"] for group in signature["groups"]}) \
            == signature["distinct"], key


# --- the surfaces §4.5 registers that C3's numbers cannot pin ---------------
#
# Round 5, finding 9. Study 011 published no full value distribution, no
# distribution over whole-run multisets and no old-edge table, so the
# replication above says nothing about any of the three. These records are
# built here, at the two registered pairs, and every expected count is stated
# beside the fixture rather than derived from the census under test.

EMBARGO = ("KP", "IR", "SY")


def _vendor(value: str, *, country: str = "NL", personal: bool = False,
            sanctions: bool = False) -> dict:
    return {"legalName": "Vendor " + value, "sanctionsHit": sanctions,
            "registeredCountry": country, "handlesPersonalData": personal,
            "riskScore": value}


def _record(value: str, outcome: str, **vendor) -> dict:
    return {"caseId": "case-" + value, "vendor": _vendor(value, **vendor),
            "decision": {"outcome": outcome, "decidedBy": "reviewer-1",
                         "decidedAt": "2026-06-02T09:00:00Z"}}


def _census(runs: dict, arm: str = "E", pair: tuple = ("40", "70")) -> dict:
    """One arm's census over records this file builds. No class predicates are
    needed for X3 or X4 — X1 is the only endpoint that reads them, and it is
    what C3's replication above already pins."""
    return census.census(arm, runs, [], EMBARGO, *pair)


def test_two_corpora_differing_only_off_edge_are_two_censuses():
    """The reviewer's own case (round 5, finding 9): arm E records at 12 and at
    13 produced IDENTICAL complete census objects.

    Both values are more than 1.0 from every edge, so X2 buckets them together
    and X3's near-edge tables saw neither; X6's sentinel list anticipates
    neither; X1 counts distinct values only inside a class. A census whose
    registered job is to catch a value arrived at by an unanticipated route
    could not tell the two corpora apart. X3's full distribution can, and the
    two facts are asserted together so the fix cannot be read as an accident.
    """
    twelve = _census({"run-001": [_record("12", "clear")]})
    thirteen = _census({"run-001": [_record("13", "clear")]})
    assert twelve["x2"] == thirteen["x2"], "the buckets are why this was invisible"
    assert twelve["x3"]["edges"] == thirteen["x3"]["edges"]
    assert twelve["x6"] == thirteen["x6"]
    assert twelve["x3"]["values"] == [["12", 1]]
    assert thirteen["x3"]["values"] == [["13", 1]]
    assert twelve != thirteen
    # And the rendering carries it, so a reader of CENSUS.md sees what
    # RESULTS.json holds (§4.7).
    assert "| 12 | 1 |" in census.render_markdown([twelve])
    assert "| 13 | 1 |" in census.render_markdown([thirteen])


def test_arm_d_publishes_the_old_edge_tables_at_forty_and_seventy():
    """§4.5's registered expectation under D — "the near-edge tables at 40 and
    70 empty out" — is a statement about tables arm D did not publish (round 5,
    finding 9).

    The records below sit exactly on the OLD edges and 1.0 above the new ones,
    which is the shape the expectation is about: D's own tables say the mass
    moved, and only the old tables can say it left.
    """
    runs = {"run-001": [_record("40", "clear"), _record("70", "clear",
                                                        personal=True),
                        _record("70.5", "clear", personal=True),
                        _record("45", "clear", personal=True),
                        _record("72", "manual-review")]}
    block = _census(runs, arm="D", pair=("45", "72"))
    own = {row["edge"]: row for row in block["x3"]["edges"]}
    assert sorted(own) == ["44", "45", "72"]
    assert (own["45"]["at"], own["72"]["at"]) == (1, 1)
    old = {row["edge"]: row for row in block["x3"]["oldEdges"]}
    assert sorted(old) == ["40", "70"]
    assert (old["40"]["at"], old["70"]["at"]) == (1, 1)
    # Stated in no text arm D's author saw: the label is about this arm's own
    # policy bytes and not about the study's history.
    assert [row["stated"] for row in block["x3"]["oldEdges"]] == ["unstated"] * 2
    # The old table's own approach column, at a value 1.5 from every new edge
    # and half a point from an old one — the record only an old-edge table sees.
    assert old["70"]["above"] == [["70.5", 1]] and old["70"]["aboveCount"] == 1
    # The emptying-out case, which is the one the expectation predicts.
    empty = _census({"run-001": [_record("45", "clear", personal=True),
                                 _record("72", "manual-review")]},
                    arm="D", pair=("45", "72"))
    old_empty = {row["edge"]: row for row in empty["x3"]["oldEdges"]}
    for edge in ("40", "70"):
        assert (old_empty[edge]["belowCount"], old_empty[edge]["at"],
                old_empty[edge]["aboveCount"]) == (0, 0, 0), edge
    assert "old edge" in census.render_markdown([empty])
    # No other arm publishes it: 40 and 70 are already their own edges.
    for arm in ("A", "B", "C", "E"):
        assert "oldEdges" not in _census({"run-001": [_record("40", "clear")]},
                                         arm=arm)["x3"]


def test_x4_publishes_every_distinct_run_multiset_and_its_run_count():
    """X4's registered wording is "the number of runs sharing a whole-run
    profile multiset", and §4.5 calls the distribution full (round 5,
    finding 9).

    Two runs here ask the same questions in the same numbers and a third does
    not, so the aggregates alone — 2 distinct, 2 sharing, group sizes [2] —
    could belong to any corpus with that shape. The groups say which.
    """
    same = [_record("70", "manual-review"), _record("12", "clear")]
    runs = {"run-001": list(same), "run-002": list(same),
            "run-003": [_record("70", "manual-review"),
                        _record("12", "clear", country="SY")]}
    block = _census(runs)
    profile = block["x4"]["signatures"]["profile"]
    assert profile["distinct"] == 2
    assert profile["runsSharing"] == 2 and profile["groupSizes"] == [2]
    assert [group["runs"] for group in profile["groups"]] == [2, 1]
    # The shared multiset is two questions asked once each, and the third run's
    # differs in exactly the member that makes it a different question.
    shared, alone = profile["groups"]
    assert shared["signature"] != alone["signature"]
    assert "x1" in shared["signature"]
    assert "true" in alone["signature"], "the embargoed record is the difference"
    # The probe multiset, which carries the exact value, separates them too.
    probe = block["x4"]["signatures"]["probe"]
    assert [group["runs"] for group in probe["groups"]] == [2, 1]
    rendered = census.render_markdown([block])
    assert "whole-run profile multiset" in rendered
    for group in profile["groups"]:
        assert "| %d | %s |" % (group["runs"], group["signature"]) in rendered
