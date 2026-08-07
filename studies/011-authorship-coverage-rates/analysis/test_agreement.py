#!/usr/bin/env python3
"""MIRROR-AGREEMENT.md, `analysis/agreement.py` and `analysis/mirror2.py`
cannot silently disagree.

The agreement document rests on three things that can each drift out from
under it: the retained tree it recomputes from, the clean-room mirror it
compares against, and the prose someone edits afterwards. These tests pin all
three.

  - the headline counts (784/784 and 120/120) and the per-clause deciding
    vector are asserted outright, so a drifted or partially restored retained
    tree fails here instead of quietly producing a different agreement;
  - `mirror2.py`'s bytes must hash to the digest the document publishes, so
    "the clean-room mirror" cannot be edited into agreement after the fact —
    an edit that fixed a divergence would be indistinguishable from
    independence otherwise;
  - every markdown table the script prints must appear VERBATIM in
    MIRROR-AGREEMENT.md, and the document must keep its post-hoc label;
  - the script is re-run and must print identical bytes, and the study tree
    must be unchanged afterwards.

Run with the rest of the study's suite: `python -m pytest harness/tests
analysis -q` from the study root — the command the `study-011-harness` CI job
already runs, which needs no extension for this file.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
SCRIPT = os.path.join(HERE, "agreement.py")
MIRROR2 = os.path.join(HERE, "mirror2.py")
NOTES = os.path.join(HERE, "MIRROR2-NOTES.md")
DOC = os.path.join(STUDY, "MIRROR-AGREEMENT.md")


def run_script() -> str:
    finished = subprocess.run([sys.executable, SCRIPT], cwd=STUDY,
                              capture_output=True, text=True, check=False)
    assert finished.returncode == 0, (
        "agreement.py exited %d — it exits nonzero on any disagreement:\n%s%s"
        % (finished.returncode, finished.stdout[-3000:], finished.stderr))
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
    matches = [line for line in text.splitlines() if line.startswith(prefix)]
    assert len(matches) == 1, "expected one row starting %r, got %d" % (
        prefix, len(matches))
    return [cell.strip() for cell in matches[0].strip("|").split("|")]


def digest(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


# ----------------------------------------------------------- the numbers

def test_the_corpus_agrees_784_of_784(printed: str) -> None:
    assert "**Corpus agreement: 784/784, 0 disagreements.**" in printed
    assert ("Record set: 49 valid runs x 16 accepted records = 784, "
            "0 dropped.") in printed


def test_the_excluded_slot_is_named_with_its_refusal(printed: str) -> None:
    assert ("Excluded by RESULTS.json, not by this script: 1 of 50 slots — "
            "`run-026` (transcript-refused).") in printed


def test_the_grid_agrees_120_of_120(printed: str) -> None:
    assert "**Grid agreement: 120/120, 0 disagreements.**" in printed
    assert ("Study-mirror verdict distribution over the grid: reject 90, "
            "clear 17, manual-review 13.") in printed
    assert ("60 of 120 cells short-circuit at P1 and 30 more at P2, so 30 "
            "unsanctioned non-embargoed cells carry all the boundary work."
            ) in printed


def test_per_clause_deciding_counts_vector(printed: str) -> None:
    """106/147/148/145/238 deciding, 37/52/35/14/34 distinct probes — the
    vector DIVERSITY.md table H publishes. Reproducing it is how the script
    shows it recompiled the SCORED set and not some other one."""
    expected = {"P1": ("106", "37"), "P2": ("147", "52"), "P3": ("148", "35"),
                "P4": ("145", "14"), "P5": ("238", "34")}
    vector = []
    for clause, counts in expected.items():
        cells = row_cells(printed, "| %s | " % clause)
        vector.append((cells[0], cells[1], cells[2]))
        assert (cells[1], cells[2]) == counts, clause
    assert vector == [("P1", "106", "37"), ("P2", "147", "52"),
                      ("P3", "148", "35"), ("P4", "145", "14"),
                      ("P5", "238", "34")]


def test_the_witness_table_places_both_instruments(printed: str) -> None:
    """The thin encodings and the ones the grid cannot reach at all."""
    assert ("| P3 `>=` becomes `>` (70 excluded) | P3 | 49 | 1 | 1 |"
            ) in printed
    assert "| P4 lower bound 40 -> 41 | P4 | 52 | 2 | 2 |" in printed
    assert "| P5 inner clearance bound 40 -> 39 | P5 | 49 | 2 | 4 |" in printed
    assert "| P2 embargo list loses IR | P2 | 49 | 13 | 0 |" in printed
    assert "| P2 embargo list loses SY | P2 | 49 | 26 | 0 |" in printed
    assert ("| P4 personal-data condition inverted | P4 | 251 | 24 | 10 |"
            ) in printed


def test_the_out_of_domain_values_are_all_dropped_by_the_compiler(
        printed: str) -> None:
    """The float/bool/NaN divergences are unreachable, and it is the
    compiler's grammar that makes them so."""
    assert "| 69.99 (str, the control) | yes | — |" in printed
    for row in ("| 69.99 (float) | **no** | schema |",
                "| True (bool) | **no** | schema |",
                '| "NaN" | **no** | decimal-form |',
                '| "Infinity" | **no** | decimal-form |',
                '| "1e2" | **no** | decimal-form |',
                '| "-5" | **no** | decimal-form |'):
        assert row in printed, row
    assert "study=raise:InvalidOperation  clean=raise:InvalidOperation" \
        in printed


# ------------------------------------------------- the clean-room artifact

def test_mirror2_bytes_are_the_digest_the_document_publishes(
        document: str) -> None:
    """The bytes compared must be the bytes published. Otherwise a mirror
    edited into agreement after the fact reads exactly like independence."""
    assert digest(MIRROR2) == (
        "471c953d29a1508438122b15c577a3ba87a7e6769714494e4b1ba9728916b0d3")
    assert digest(NOTES) == (
        "80c1ec90b41fcaa3f9016edea1a29ecd36b63d386c9cc3082a6e8b9d97070413")
    assert ("| `analysis/mirror2.py` | `%s` |" % digest(MIRROR2)) in document
    assert ("| `analysis/MIRROR2-NOTES.md` | `%s` |" % digest(NOTES)) \
        in document


def test_the_notes_keep_the_error_the_check_caught(document: str) -> None:
    """MIRROR2-NOTES.md is left uncorrected on purpose — it is the evidence.
    The correction lives in the document, stated plainly."""
    with open(NOTES, encoding="utf-8") as handle:
        notes = handle.read()
    assert "would therefore fall through to `\"clear\"`" in notes
    assert "wrong about their own code, and the check caught" in document
    assert "does not compare false" in document


# ------------------------------------------------------ document and tree

def test_every_printed_table_appears_verbatim_in_the_document(
        printed: str, document: str) -> None:
    printed_tables = tables(printed)
    assert len(printed_tables) >= 3, "the script prints fewer tables than the "\
        "document's sections"
    for table in printed_tables:
        assert table in document, (
            "this table is not in MIRROR-AGREEMENT.md verbatim:\n%s" % table)


def test_the_document_carries_the_counts_verbatim(document: str) -> None:
    assert "**Corpus agreement: 784/784, 0 disagreements.**" in document
    assert "**Grid agreement: 120/120, 0 disagreements.**" in document


def test_the_document_is_labelled_post_hoc(document: str) -> None:
    for claim in ("**POST-HOC DESCRIPTIVE ANALYSIS.**",
                  "Computed 2026-08-07 from the retained\nbytes",
                  "after the study merged",
                  "Nothing\nhere was preregistered",
                  "It changes no registered claim",
                  "Every table\nbelow is regenerated by `analysis/agreement.py`",
                  "byte-lineage, not truth."):
        assert claim in document, claim


def test_the_document_keeps_the_shared_text_ceiling(document: str) -> None:
    """The upgrade is bounded, and the bound has to survive editing."""
    assert "the shared-text ceiling stands" in document
    assert "A misreading BOTH make remains invisible" in document
    assert "a different POLICY author" in document
    assert "real-world outcomes" in document


def test_the_follow_up_ledger_is_dispositioned(document: str) -> None:
    assert "## The follow-up ledger, dispositioned" in document
    for item in ("**(a) Boundary distance and duplicates — measured, closed.**",
                 "**(b) A second scorer — done, this document.**",
                 "**(c) Robustness to mutation of a stated literal — "
                 "mechanical, closed\nelsewhere.**",
                 "**(d) Semantic and adversarial rewording — genuinely open.**",
                 "**(e) The axis the study's own analysis names first — "
                 "policy richness.**",
                 "**(f) Priority, per the direction.**"):
        assert item in document, item
    assert "denamed-anchor cell" in document
    assert "coverage of the denamed classes collapses" in document
    assert "ADR-0023" in document


def test_the_ci_command_already_covers_this_directory() -> None:
    """`analysis` is already in the study-011 CI job's pytest invocation, so
    this file needs no new command. If someone narrows that invocation back to
    `harness/tests`, this test says so rather than letting the agreement stop
    being checked."""
    workflow = os.path.join(STUDY, "..", "..", ".github", "workflows",
                            "ci.yml")
    if not os.path.exists(workflow):
        pytest.skip("running outside the repository checkout")
    with open(workflow, encoding="utf-8") as handle:
        text = handle.read()
    assert "python -m pytest harness/tests analysis -q" in text


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
