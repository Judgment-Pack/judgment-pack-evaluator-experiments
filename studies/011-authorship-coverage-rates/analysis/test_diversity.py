#!/usr/bin/env python3
"""DIVERSITY.md and analysis/diversity.py cannot silently disagree.

The addendum is a document of numbers, and both of the things it depends on
can drift out from under it: the retained tree it is computed from, and the
prose someone edits afterwards. These tests pin both ends.

  - the script's headline numbers are asserted outright, so a drifted or
    partially restored retained tree fails here instead of quietly producing a
    different census;
  - every markdown table the script prints must appear VERBATIM in
    DIVERSITY.md, so an edited table in the document fails too;
  - the script is re-run and must print identical bytes, and the study tree
    must be unchanged afterwards.

Run with the rest of the study's suite: `python -m pytest harness/tests
analysis -q` from the study root.
"""
from __future__ import annotations

import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
SCRIPT = os.path.join(HERE, "diversity.py")
DOC = os.path.join(STUDY, "DIVERSITY.md")


def run_script() -> str:
    finished = subprocess.run([sys.executable, SCRIPT], cwd=STUDY,
                              capture_output=True, text=True, check=False)
    assert finished.returncode == 0, finished.stderr
    return finished.stdout


@pytest.fixture(scope="module")
def printed() -> str:
    return run_script()


@pytest.fixture(scope="module")
def document() -> str:
    with open(DOC, encoding="utf-8") as handle:
        return handle.read()


def tables(text: str) -> list:
    """Every maximal run of consecutive markdown table lines."""
    found, current = [], []
    for line in text.splitlines():
        if line.startswith("|"):
            current.append(line)
        elif current:
            found.append("\n".join(current))
            current = []
    if current:
        found.append("\n".join(current))
    return found


def row_cells(text: str, prefix: str) -> list:
    """The cells of the single table row starting with `prefix`."""
    matches = [line for line in text.splitlines()
               if line.startswith(prefix)]
    assert len(matches) == 1, "expected one row starting %r, got %d" % (
        prefix, len(matches))
    return [cell.strip() for cell in matches[0].strip("|").split("|")]


# ----------------------------------------------------------- the numbers

def test_record_set_is_the_scored_set(printed: str) -> None:
    """784 accepted, 0 dropped, H 784, Q 0 — RATES.md's own splits."""
    assert ("Record set: 49 valid runs x 16 accepted records = 784, "
            "0 dropped; H = 784, Q = 0.") in printed


def test_the_excluded_slot_is_named_with_its_refusal(printed: str) -> None:
    assert ("Excluded by RESULTS.json, not by this script: 1 of 50 slots — "
            "`run-026` (transcript-refused).") in printed


def test_distance_bucket_table(printed: str) -> None:
    expected = [
        "| exactly on a threshold | 181 |",
        "| 0 < d <= 0.001 | 84 |",
        "| 0.001 < d <= 0.01 | 145 |",
        "| 0.01 < d <= 0.1 | 1 |",
        "| 0.1 < d <= 1 | 3 |",
        "| d > 1 | 370 |",
    ]
    for row in expected:
        assert row in printed, row
    assert ("410 of 784 (52.3%) sit on a threshold or within 0.01 of one. "
            "Exactly 4 land in the human-sized gap (0.01, 1.0].") in printed


def test_nothing_below_the_unstated_edge_and_both_far_sides_of_the_stated_ones(
        printed: str) -> None:
    assert ("| 39 (unstated) | none | 0 | 0 | 39.5 x2, 39.9 x1, 39.99 x58, "
            "39.999 x28, 40 x103 | 192 |") in printed
    assert ("| 40 (stated) | 39.5 x2, 39.9 x1, 39.99 x58, 39.999 x28 | 89 "
            "| 103 | 40.01 x3 | 3 |") in printed
    assert ("| 70 (stated) | 69 x1, 69.99 x51, 69.999 x48 | 100 | 78 | "
            "70.001 x8, 70.01 x33 | 41 |") in printed


def test_distinct_probe_vector(printed: str) -> None:
    """The headline of the whole addendum: 2, 6, 2, 24, 26, 2."""
    vector = [row_cells(printed, "| %d | no sanctions hit," % index)[5]
              for index in range(6)]
    assert vector == ["**2**", "**6**", "**2**", "**24**", "**26**", "**2**"]


def test_class_5_is_two_probes_partitioning_the_runs_28_21(
        printed: str, document: str) -> None:
    cells = row_cells(printed, "| 5 | no sanctions hit,")
    assert cells[5] == "**2**"
    assert cells[8] == "28/49", "the modal probe's run share"
    assert cells[9] == "21", "runs still covered without it"
    assert "39.99 (28 runs) or 39.999 (21 runs)" in document


def test_the_all_49_probes_and_the_coverage_collapse(printed: str) -> None:
    assert '| 0 | ("70", false, non-emb, false) | 49 | 4 |' in printed
    assert '| 1 | ("70", false, non-emb, false) | 49 | 45 |' in printed
    assert '| 2 | ("40", false, non-emb, true) | 49 | 3 |' in printed
    assert '| 3 | ("40", false, non-emb, false) | 49 | 49 |' in printed
    assert '| 3 | ("40", false, non-emb, true) | 49 | 49 |' in printed
    assert "| 4 | none — the widest reaches 11/49 runs | — | — |" in printed
    assert "| 5 | none — the widest reaches 28/49 runs | — | — |" in printed


def test_run_skeletons_repeat(printed: str) -> None:
    assert ("| profile multiset, def (i) | 21 | 38 (77.6%) | 10, 8, 5, 3, 2, "
            "2, 2, 2, 2, 2, then 11 singletons |") in printed
    assert ("| probe multiset (exact value + tuple) | 49 | 0 (0.0%) | all "
            "singletons |") in printed
    assert "Mean redundant records per run: 5.143 of 16 (32.1%)." in printed


def test_vendor_tuple_duplicates(printed: str) -> None:
    assert ("| exact vendor tuple (all five members) | 725 | 32 | 91 | 59 | "
            "0 |") in printed
    assert ("| semantic profile (i) | 17 | 15 | 782 | 767 | 252 |") in printed


def test_per_clause_deciding_counts(printed: str) -> None:
    expected = {"P1": ("106", "13.52%"), "P2": ("147", "18.75%"),
                "P3": ("148", "18.88%"), "P4": ("145", "18.49%"),
                "P5": ("238", "30.36%")}
    for clause, (records, share) in expected.items():
        cells = row_cells(printed, "| %s | " % clause)
        assert (cells[2], cells[3]) == (records, share), clause
        assert cells[4] == "49/49", clause
    assert "Outcome distribution: clear 238, manual-review 293, reject 253." \
        in printed


def test_the_single_probe_pinned_boundary_encodings(printed: str) -> None:
    """P3's inclusivity rests on one distinct probe; P4's lower bound and
    P5's inner edge on two each."""
    assert ("| P3 `>=` becomes `>` (70 excluded) | P3 | 49 | 49 | **1** | "
            "49 |") in printed
    assert "| P4 lower bound 40 -> 41 | P4 | 52 | 49 | **2** | 46 |" in printed
    assert ("| P5 inner clearance bound 40 -> 39 | P5 | 49 | 49 | **2** | "
            "49 |") in printed
    assert ("| P4 personal-data condition inverted | P4 | 251 | 49 | 24 | "
            "0 |") in printed


# ------------------------------------------------------ document and tree

def test_every_printed_table_appears_verbatim_in_the_document(
        printed: str, document: str) -> None:
    printed_tables = tables(printed)
    assert len(printed_tables) >= 9, "the script prints fewer tables than the "\
        "addendum's sections"
    for table in printed_tables:
        assert table in document, (
            "this table is not in DIVERSITY.md verbatim:\n%s" % table)


def test_the_document_is_labelled_post_hoc(document: str) -> None:
    for claim in ("**POST-HOC DESCRIPTIVE ANALYSIS.**",
                  "Computed 2026-08-07 from the retained\nbytes",
                  "Nothing here was preregistered",
                  "It changes no\nregistered claim",
                  "regenerated by\n`analysis/diversity.py`",
                  "internally consistent and\nboundary-dense, but probe-poor",
                  "byte-lineage, not truth."):
        assert claim in document, claim


def test_the_script_is_deterministic_and_read_only() -> None:
    def snapshot() -> dict:
        state = {}
        for root, directories, names in os.walk(STUDY):
            directories[:] = [name for name in sorted(directories)
                              if name != "__pycache__"]
            for name in sorted(names):
                path = os.path.join(root, name)
                info = os.stat(path)
                state[path] = (info.st_size, info.st_mtime_ns)
        return state

    before = snapshot()
    first = run_script()
    second = run_script()
    assert first == second, "the script is not deterministic"
    assert snapshot() == before, "the script wrote to the study tree"


def test_the_below_39_band_claim_is_computed_not_asserted(document: str) -> None:
    """The check round found the draft claiming 'nothing anywhere below 39',
    which the clear-region records refute. The corrected claim is scoped and
    stronger — the band [23.75, 39) is empty — and this test recomputes it
    from the corpus so the prose cannot drift from the bytes again."""
    sys.path.insert(0, os.path.join(STUDY, "harness"))
    sys.path.insert(0, HERE)
    import diversity

    runs, _mutations, population, _family = diversity.load()
    records = [record for slot in population["valid"] for record in runs[slot]]
    from decimal import Decimal
    below = sorted(Decimal(r["vendor"]["riskScore"]) for r in records
                   if Decimal(r["vendor"]["riskScore"]) < Decimal("39"))
    assert below, "the clear region is populated below 39"
    assert below[-1] == Decimal("23.75"), below[-5:]
    assert not [v for v in below if v >= Decimal("38")]
    assert "nothing in [38, 39)" in document
    assert "nearest approach from below anywhere\nin the corpus is 23.75" \
        in document or "nearest approach from below anywhere in the corpus " \
        "is 23.75" in document
    assert "nothing anywhere below it" not in document
