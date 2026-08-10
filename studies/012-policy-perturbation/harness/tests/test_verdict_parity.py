#!/usr/bin/env python3
"""§5's tables, parsed out of the preregistration and diffed against the code
that computes the verdicts (§6 C5's last paragraph).

C5 registers that "the §5.1 level verdicts, §5.2 contrast verdicts and §5.3
decision-table row are computed by the scorer from the integers it just wrote,
by the registered rules, with no operator input and no flag that changes a cut",
and that "a harness test parses §5.1's, §5.2's and §5.3's tables out of this
file and diffs them against the scorer's own". This is that test.

Five tables are diffed, each located by its own header shape rather than by a
line number:

  §5.1  | condition | level |                          -> `LEVEL_TABLE`
  §5.2  | condition | contrast |                       -> `CONTRAST_TABLE`
  §5.2  | condition (levels on the S1 raw rate) | …    -> `PLACEMENT_CONTRAST_TABLE`
  §5.2  | condition | second contrast |                -> `SECOND_CONTRAST_TABLE`
  §5.3  | # | condition | outcome for R1 | published as | -> `DECISION_TABLE`

and then the two cuts are located where §5.1 says they land — `k >= 27` and
`k <= 3` at n = 30 — by asking the interval code, not by asserting a constant
against itself. The §4.3 vectors close the loop: the frozen file, this suite's
own transcription (`fixtures.REGISTERED_VECTORS`) and the scorer's data must
agree, and the arithmetic must reproduce every one of them.

§5.3 (ii)'s arm-D outcomes have no table in the preregistration, so they are
held to the registered SENTENCE instead: round 4, finding 6 pins the first
outcome's condition — new-keyed HIGH on three or more of the four narrow
numeric classes, old-keyed not HIGH-patterned — as quoted text and as computed
behaviour, because the scorer had substituted a stricter rule of its own.

The last two cases are a PHRASE lint over §5.4's prose rather than a table diff
(round 6, finding 4). Round 5's rule pinned the operating-characteristic table's
row LABELS, and the withdrawn names for `0.7359`/`0.3536` survived in the text
beside them — so the section is parsed by heading, its tables dropped, and what
is left must name the CONFIRMED-side figure coverage-side wherever it discusses
it and must not carry any of the three names §5.4's own paragraph withdraws.

A third phrase lint holds §4.6 (round 9, finding 2). Its two reading cells
asserted what the author understood, on a cut that reads labels and cannot see
whether any accepted record exercised a threshold; they now say what the
integers show, §4.6 registers the limit in its own paragraph, and the lint
asserts that paragraph's final sentence and refuses either withdrawn reading in
any cell — of the file's table or the scorer's. A parity diff cannot catch this
one, because it asks only that the two sides agree.

A fourth holds §5.4's endpoint assumption (round 9, finding 9). Row 5 is the
one figure combining the primary and the S1 placement endpoint, and §5.4's own
fourth independence layer promises that any such figure is marked: the section
must say that the scenario assigns its `p` to both endpoints and that `H ⊆ raw`
pathwise then leaves the two per-slot indicators equal almost surely, which is
what makes reading one arm-A pattern for both rules exact under this scenario.
The lint is held to a known answer as round 6's is, and a numeric pin
recomputes the alternative §5.4 names — the two patterns independent — from the
same call, so the three published figures are the code's and not a second
transcription of it.

Round 10, finding 4 adds the containment companion and the first parser for
§5.4's SIX-column joint tables, which no test read for nine rounds. §2.3
registers that class 0 nests in class 1 and class 2 in class 3; correctness is a
property of the record, so those coverage indicators are ordered pathwise and
§5.4's first independence layer is unavailable between them at any nondegenerate
marginals. The five rules that carry N are therefore published twice — the
independence figures unchanged, as the incoherent approximation they are, beside
a containment-respecting companion — and this file diffs both sets against the
scorer's two functions, parses the independence joint table and its companion
cell by cell, and asserts the infeasibility (`q**6 < 4q - 3`, `q**4 < 3q - 2` at
N = 25 and N = 30) and the direction facts, including the N = 20 reversal, from
the exact rationals rather than transcribing them.

Round 9, finding 12 adds the diff §5.4's own opening sentence already claimed.
The MARGINAL level table — P(HIGH), P(LOW), P(MID) against a true p — is
parsed by its header and recomputed cell by cell, and the note beneath it is
held to the same arithmetic: it called every `0.0000` in the FILE rounded when
four of that table's cells are exact, and gave a magnitude for P(HIGH | p =
0.30) that no tail of this distribution reproduces. The exact cells are pinned
as a set and the magnitude is regenerated from the code, so neither half can
drift back into a transcription.
"""
from __future__ import annotations
import os
import re
from fractions import Fraction

import pytest

import fixtures
import policy_mirror
import score_rates

VECTOR = re.compile(r"`k=(\d+) → \[(\d\.\d{4}), (\d\.\d{4})\]`")


def table(body: str, header: list) -> list:
    """The rows of the one pipe table whose header matches, by shape."""
    matches = [rows for cells, rows in fixtures.markdown_tables(body)
               if [fixtures.plain(cell) for cell in cells] == header]
    assert len(matches) == 1, (
        "PREREGISTRATION.md holds %d tables with the header %r; §5's tables are "
        "identified by their headers and one of them is not unique"
        % (len(matches), header))
    return [[fixtures.plain(cell) for cell in row] for row in matches[0]]


# --- §5.1 -------------------------------------------------------------------

def encoded(rows) -> list:
    """One of the scorer's own tables, put through the same normalization the
    file's cells go through, so the diff is between two rules and not between
    two spellings of one."""
    return [tuple(fixtures.plain(cell) for cell in row) for row in rows]


def test_the_level_table_is_the_scorers_level_table(preregistration):
    registered = [tuple(row) for row in
                  table(preregistration, ["condition", "level"])]
    assert registered == encoded(score_rates.LEVEL_TABLE)
    assert registered[0] == ("L_{i,X} >= %.2f" % score_rates.HIGH_CUT, "HIGH")
    assert registered[1] == ("otherwise, U_{i,X} <= %.2f" % score_rates.LOW_CUT,
                             "LOW")
    assert registered[2] == ("otherwise", "MID")


def test_the_level_rule_applies_to_every_endpoint_it_is_registered_over(
        preregistration):
    """§5.1: the rule applies unchanged to the primary ITT rate, to the S1
    raw-placement rate, to the per-protocol rate and to §4.6 S10's old-edge
    cross-scored rate. Every level verdict names which of them it is a verdict
    on.

    Round 12, finding 6: §5.1 said THREE and this tuple has always held four,
    for ten rounds, with nothing diffing the prose against the tuple. The count
    is asserted on both sides here, because that is the only thing that stops
    the pair drifting apart again.
    """
    assert score_rates.LEVEL_ENDPOINTS == ("primary", "placement",
                                           "perProtocol", "oldEdge")
    flat = " ".join(preregistration.split())
    assert "names which of the four it is a verdict on" in flat
    assert len(score_rates.LEVEL_ENDPOINTS) == 4


def test_the_level_verdict_reads_bounds_and_not_observed_coverage():
    """The cuts are stated ON BOUNDS, so a denominator carrying more misses
    faces a boundary that already carries them. 26 of 30 is 0.867 observed and
    MID; 22 of 25 is 0.88 observed and MID; a smaller denominator does not buy
    a HIGH by having a higher point estimate."""
    assert score_rates.level_verdict(score_rates.rate_block(26, 30, "N")) == "MID"
    assert score_rates.level_verdict(score_rates.rate_block(22, 25, "N")) == "MID"
    assert score_rates.level_verdict(score_rates.rate_block(27, 30, "N")) == "HIGH"
    assert score_rates.level_verdict(score_rates.rate_block(3, 30, "N")) == "LOW"
    assert score_rates.level_verdict(score_rates.rate_block(4, 30, "N")) == "MID"
    # No rate, no verdict — not a default.
    assert score_rates.level_verdict(score_rates.rate_block(0, 0, "V_X")) \
        == score_rates.UNRESOLVED


def test_the_two_cuts_land_where_section_5_1_says_they_land(preregistration):
    """§5.1: "at n = 30, land at: HIGH iff `k ≥ 27` … LOW iff `k ≤ 3`".

    Asked of the interval code rather than asserted as a constant: the
    thresholds are where the exact bounds cross 0.70 and 0.30, and the two
    neighbours on either side are checked so the cut is a cut and not a
    coincidence.
    """
    trials = fixtures.REGISTERED_CUTS["trials"]
    high = fixtures.REGISTERED_CUTS["high"]
    low = fixtures.REGISTERED_CUTS["low"]
    assert score_rates.high_threshold(trials) == high
    assert score_rates.low_threshold(trials) == low
    assert score_rates.lower_bound(high, trials) >= score_rates.HIGH_CUT
    assert score_rates.lower_bound(high - 1, trials) < score_rates.HIGH_CUT
    assert score_rates.upper_bound(low, trials) <= score_rates.LOW_CUT
    assert score_rates.upper_bound(low + 1, trials) > score_rates.LOW_CUT
    flat = " ".join(preregistration.split())
    assert "HIGH iff `k ≥ %d`" % high in flat
    assert "LOW iff `k ≤ %d`" % low in flat


def test_the_per_protocol_floor_is_the_registered_one(preregistration):
    """§5.1's second floor: below `V_X` = 11 a perfect arm cannot read HIGH
    (0.6915 at V = 10, 0.7151 at V = 11), so the six S11 verdicts are
    UNRESOLVED-BY-DESIGN rather than a table of MIDs. The primary and S1 have
    NO floor: ITT fixes their denominator at N."""
    assert score_rates.PER_PROTOCOL_FLOOR == 11
    assert score_rates.lower_bound(11, 11) >= score_rates.HIGH_CUT
    assert score_rates.lower_bound(10, 10) < score_rates.HIGH_CUT
    flat = " ".join(preregistration.split())
    assert "%.4f at V = 10" % score_rates.lower_bound(10, 10) in flat
    assert "%.4f at V = 11" % score_rates.lower_bound(11, 11) in flat


# --- §5.2 -------------------------------------------------------------------

def test_the_contrast_table_is_the_scorers_contrast_table(preregistration):
    registered = [tuple(row) for row in
                  table(preregistration, ["condition", "contrast"])]
    assert registered == encoded(score_rates.CONTRAST_TABLE)


def test_the_placement_contrast_table_is_the_scorers(preregistration):
    registered = [tuple(row) for row in table(
        preregistration, ["condition (levels on the S1 raw rate)",
                          "placement contrast"])]
    assert registered == encoded(score_rates.PLACEMENT_CONTRAST_TABLE)


def test_the_second_contrast_table_is_the_scorers(preregistration):
    """[D-17]'s weaker contrast, whose second row is an em dash in the file and
    `None` in the scorer: it is reported beside the level-gated verdict and
    never in place of it, so "otherwise" names no verdict at all."""
    registered = [tuple(row) for row in
                  table(preregistration, ["condition", "second contrast"])]
    assert registered == encoded(
        (condition, verdict if verdict is not None else "—")
        for condition, verdict in score_rates.SECOND_CONTRAST_TABLE)
    assert score_rates.SECOND_CONTRAST_TABLE[1][1] is None


def test_the_contrasts_are_computed_by_the_registered_rules():
    """The three rules, applied to the level pairs they are stated over —
    including the two cases §5.2 says INDETERMINATE covers: the arm landed in
    the middle, and the baseline itself was not HIGH."""
    assert score_rates.contrast_verdict("HIGH", "LOW") == "COLLAPSE"
    assert score_rates.contrast_verdict("HIGH", "HIGH") == "TRACKING"
    assert score_rates.contrast_verdict("HIGH", "MID") == "INDETERMINATE"
    assert score_rates.contrast_verdict("MID", "LOW") == "INDETERMINATE"
    assert score_rates.placement_contrast_verdict("HIGH", "LOW") \
        == "PLACEMENT-COLLAPSE"
    assert score_rates.placement_contrast_verdict("HIGH", "HIGH") \
        == "PLACEMENT-TRACKING"
    assert score_rates.placement_contrast_verdict("MID", "LOW") \
        == "PLACEMENT-INDETERMINATE"
    # An unresolved level cannot become a contrast in either direction.
    for level in ("HIGH", "LOW", "MID"):
        assert score_rates.contrast_verdict(score_rates.UNRESOLVED, level) \
            == score_rates.UNRESOLVED
        assert score_rates.contrast_verdict(level, score_rates.UNRESOLVED) \
            == score_rates.UNRESOLVED
    # [D-17]'s second contrast: §5.2's own worked example — arm E LOW at k = 3
    # while arm A reads MID at k = 26 — is INDETERMINATE and COLLAPSE-DISJOINT
    # at the same time, which is the information the level-gated rule discards.
    baseline = score_rates.rate_block(26, 30, "N")
    arm = score_rates.rate_block(3, 30, "N")
    assert score_rates.level_verdict(baseline) == "MID"
    assert score_rates.level_verdict(arm) == "LOW"
    assert score_rates.contrast_verdict("MID", "LOW") == "INDETERMINATE"
    assert score_rates.second_contrast_verdict(baseline, arm) == "COLLAPSE-DISJOINT"
    assert score_rates.second_contrast_verdict(baseline, baseline) is None


# --- §5.3 -------------------------------------------------------------------

DECISION_HEADER = ["#", "condition", "outcome for R1", "published as"]


def decision_rows(body: str) -> list:
    """§5.3's decision table as (row number, condition, outcome, published as,
    gloss) — the published cell split on its em dash, because the scorer keeps
    the name and its gloss in separate members."""
    rows = []
    for number, condition, outcome, published in table(body, DECISION_HEADER):
        name, _, gloss = published.partition(" — ")
        rows.append((int(number), condition, outcome, name, gloss))
    return rows


def test_the_decision_table_is_the_scorers_decision_table(preregistration):
    registered = decision_rows(preregistration)
    table_in_code = [(entry["row"],) + encoded([(entry["condition"],
                                                 entry["outcome"],
                                                 entry["publishedAs"],
                                                 entry["gloss"])])[0]
                     for entry in score_rates.DECISION_TABLE]
    assert [row[0] for row in registered] == list(range(1, len(registered) + 1))
    assert registered == table_in_code


def test_the_decision_table_is_ordered_exhaustive_and_total(preregistration):
    """§5.3: "evaluated top to bottom, the first row whose condition holds is
    the outcome, and the last row always holds"."""
    assert len(score_rates.DECISION_TABLE) == 7
    assert score_rates.DECISION_TABLE[-1]["condition"] == "(else)"
    assert score_rates.DECISION_TABLE[-1]["publishedAs"] == "INDETERMINATE"
    # Rows 1-3 are gates and produce no R1 verdict in either direction.
    for row in score_rates.DECISION_TABLE[:3]:
        assert row["outcome"] == "not adjudicated"
    assert score_rates.DECISION_TABLE[3]["outcome"] == "unsupported"
    assert score_rates.DECISION_TABLE[4]["outcome"] == "confirmed for this instance"
    assert ("the first row whose condition holds is the outcome, and the last "
            "row always holds") in " ".join(preregistration.split())


def test_the_pattern_thresholds_and_the_gate_are_the_registered_counts(preregistration):
    """§5.3's notation, in code: `nP`, `nC` and `nH` count over the four narrow
    numeric classes, "three or more of the four" is 3, the control gate is
    "five of six" over arms B and C, class 4 is the embargo-membership class
    whose LOW verdict in arm E overrides every other reading of arm E, and class
    3 is the interior review band row 5's fifth conjunct reads (round 9, finding
    2). Both class conditions are LEVEL verdicts on arm E — class 3 since round
    10, finding 3, class 4 since round 11, finding 1."""
    assert score_rates.NARROW_NUMERIC_CLASSES == (0, 1, 2, 5)
    assert score_rates.EMBARGO_CLASS == 4
    assert score_rates.INTERIOR_CLASS == 3
    # The two class-level conjuncts of row 5 are different classes, and neither
    # is one of the four the pattern counts run over.
    assert score_rates.INTERIOR_CLASS != score_rates.EMBARGO_CLASS
    assert score_rates.INTERIOR_CLASS not in score_rates.NARROW_NUMERIC_CLASSES
    assert score_rates.PATTERN_MINIMUM == 3
    assert score_rates.CONTROL_GATE_MINIMUM == 5
    assert score_rates.CONTROL_ARMS == ("B", "C")
    assert score_rates.BASELINE_ARM == "A"
    flat = " ".join(preregistration.split())
    assert "COLLAPSE on the four narrow numeric classes 0, 1, 2 and 5" in flat
    assert ("arm B reads TRACKING on at least five of its six classes and arm "
            "C reads TRACKING on at least five of its six") in flat


# --- §4.3's registered vectors ----------------------------------------------

def registered_vectors(body: str) -> dict:
    """§4.3's three vector sets as the frozen file registers them: the n = 30
    markdown table, and the n = 25 and n = 50 vectors written inline."""
    vectors = {30: {}, 25: {}, 50: {}}
    for row in table(body, ["k / 30", "exact 95% interval", ""]):
        k = int(row[0])
        low, high = re.match(r"\[(\d\.\d{4}), (\d\.\d{4})\]", row[1]).groups()
        vectors[30][k] = (float(low), float(high))
    twenty_five = body.split("**The n = 25 vectors are retained**")[1]
    twenty_five = twenty_five.split("And **Study 011's registered vectors")[0]
    fifty = body.split("And **Study 011's registered vectors")[1]
    fifty = fifty.split("so the ported")[0]
    for trials, text in ((25, twenty_five), (50, fifty)):
        for k, low, high in VECTOR.findall(text):
            vectors[trials][int(k)] = (float(low), float(high))
    return vectors


def test_the_registered_vectors_are_the_ones_the_file_registers(preregistration):
    """Three sources, one table: the frozen preregistration, this suite's own
    transcription of it, and the scorer's data. Two of them agreeing would
    prove only that one was copied from the other."""
    from_file = registered_vectors(preregistration)
    assert from_file == fixtures.REGISTERED_VECTORS
    assert from_file == score_rates.REGISTERED_VECTORS
    assert sorted(from_file) == [25, 30, 50]
    assert len(from_file[30]) == 11 and len(from_file[25]) == 9 \
        and len(from_file[50]) == 6


@pytest.mark.parametrize("trials", (30, 25, 50))
def test_the_interval_code_reproduces_every_registered_vector(trials):
    """C4's last item, and the port control it exists to be: n = 30 is this
    study's own denominator, n = 25 is [D-1]'s live alternative, and n = 50 is
    Study 011's — numbers a predecessor already published, so the ported
    arithmetic is checked against something that did not come from it."""
    for k, (low, high) in sorted(fixtures.REGISTERED_VECTORS[trials].items()):
        computed_low, computed_high = score_rates.clopper_pearson(k, trials)
        assert round(computed_low, 4) == low, "lower bound at k=%d/%d" % (k, trials)
        assert round(computed_high, 4) == high, "upper bound at k=%d/%d" % (k, trials)


def test_the_cut_locations_are_marked_at_the_vectors_they_fall_on(preregistration):
    """§4.3's n = 30 table marks the two §5.1 cut locations in its own third
    column, and they must be the k the interval code puts them at."""
    marks = {}
    for row in table(preregistration, ["k / 30", "exact 95% interval", ""]):
        if row[2]:
            marks[int(row[0])] = row[2]
    assert {3, 4, 26, 27} <= set(marks)
    assert "a perfect arm" in marks[30]
    assert "LOW cut" in marks[3] and "largest k" in marks[3]
    assert "HIGH cut" in marks[27] and "smallest k" in marks[27]
    assert marks[4].startswith("first k above the LOW cut")
    assert marks[26].startswith("last k below the HIGH cut")
    assert score_rates.low_threshold(30) == 3
    assert score_rates.high_threshold(30) == 27


# --- §4.6's load-bearing table, and the S5 cut it turns on -------------------

READING_HEADER = ["S1 (raw placement)", "S5 / S2 (labels)", "the reading",
                  "what §5.3 (i) does with it"]


def reading_rows(body: str) -> list:
    """§4.6's three readings as (placement cell, labels cell, reading cell,
    published cell), straight out of the frozen file."""
    return [tuple(row) for row in table(body, READING_HEADER)]


def encoded_reading(entry: dict) -> tuple:
    """One `READING_TABLE` row put back into the four cells the file writes,
    so the diff is between two rules and not two spellings."""
    placement = entry["placementLevel"]
    if entry["placementGloss"]:
        placement += " — " + entry["placementGloss"]
    return (placement, entry["labels"], entry["reading"],
            entry["publishedAs"] + " — " + entry["gloss"])


def test_the_reading_table_is_the_scorers_reading_table(preregistration):
    """Round 3, finding 9: §4.6 registers the table that separates a placement
    collapse from a comprehension collapse from a label collapse, and the
    scorer computed none of it. It is `READING_TABLE` now, and this is the same
    three-way diff §5's other tables get."""
    registered = reading_rows(preregistration)
    assert registered == [encoded_reading(entry)
                          for entry in score_rates.READING_TABLE]
    assert [entry["publishedAs"] for entry in score_rates.READING_TABLE] == [
        "PLACEMENT collapse", "comprehension collapse", "label collapse"]


def test_the_s5_cut_is_the_ceiling_the_file_names(preregistration):
    """The cut is the word §4.6 uses. The ceiling of `|H| / (|H| + |Q|)` is 1,
    so an arm is at it exactly when no accepted record was mislabelled — no
    threshold is chosen here, and S9's `mislabel share >= 0.20` is not borrowed,
    because §4.6 says S9 is not this study's decision rule and no contrast reads
    it."""
    assert score_rates.S5_CEILING == 1.0
    assert score_rates.S5_BRANCHES == ("at the ceiling", "degraded")
    ceiling = score_rates.label_branch({"rate": 1.0, "h": 30, "q": 0})
    degraded = score_rates.label_branch({"rate": 30 / 31, "h": 30, "q": 1})
    silent = score_rates.label_branch({"rate": None, "h": 0, "q": 0})
    assert ceiling["branch"] == "at the ceiling"
    # One mislabelled record in an arm of thirty runs is below the ceiling, and
    # the cut is on the ceiling and not near it.
    assert degraded["branch"] == "degraded"
    # Round 10, finding 8: an arm with no accepted record has no accuracy to
    # read, and §4.6 registers that — the cut is "at least one accepted record
    # AND |Q| = 0", so `rate is not None` implements the first conjunct instead
    # of supplying an unregistered one of the scorer's own.
    assert silent["branch"] == "degraded" and silent["rate"] is None
    plain = fixtures.plain(preregistration)
    assert ("at the ceiling iff it has at least one accepted record and "
            "|Q| = 0 among them") in plain
    assert "An arm with no accepted record at all has no accuracy to read" in plain
    # …and the reading that arm reaches must be true of it. Round 9 made row 2's
    # cell concrete, which is what made this corner visible: "at least one
    # accepted record was mislabelled" was a flat counterfactual about records
    # that do not exist.
    reading = score_rates.reading_verdict({"nP": 4, "nC": 4, "nH": 0},
                                          silent["branch"])
    assert reading["publishedAs"] == "comprehension collapse"
    assert "no accepted record at all" in reading["reading"]
    flat = " ".join(preregistration.split())
    assert "the one-step escalation at mislabel share ≥ 0.20" in flat
    assert score_rates.MISLABEL_ESCALATION not in (score_rates.S5_CEILING,)


# The sentence §4.6 registers about what the ceiling establishes, in the form
# `fixtures.plain()` leaves it: emphasis off, whitespace collapsed. Prose and
# lint are one string so the weakening cannot drift back a word at a time.
#
# Round 11, finding 1: it used to say "an intact class 4", which is a property
# of the arm, and the rule that ran established no such property — the class-4
# gate was a §5.2 contrast, so it was unavailable whenever arm A was not HIGH
# there and CONFIRMED was published for an arm E that reached the embargo class
# in none of its thirty runs. The rule is arm E's own level now (§5.3 (iv)) and
# the sentence says what the rule establishes, which is what this lint is for.
CEILING_LIMIT = ("CONFIRMED therefore means the placement pattern with clean "
                 "labels and arm E reading LOW on neither class 4 nor class 3; "
                 "it does not mean the author understood the thresholds, and "
                 "this file does not claim it does.")
# The sentence §4.6 registers about what the reading NAMES mean, linted the same
# way and for the same reason (round 11, finding 4). It is what licenses
# publishing "comprehension collapse" as a label rather than as a finding about
# the author, so it is load-bearing prose; before round 11 it was the only
# load-bearing sentence in §4.6 with no lint, and it said "the two readings
# above" of a three-row table without naming which two.
NAMING_LIMIT = ("The two readings above — PLACEMENT collapse and comprehension "
                "collapse — are therefore named for the explanations they make "
                "available, not for propositions this rule establishes")
# The two mental-state readings round 9 finding 2 withdrew. A reading cell says
# what the integers show; neither of these is something a set of correct labels
# can pin down.
WITHDRAWN_READINGS = ("understood the thresholds", "could not derive")
# The two PLACEMENT universals round 10 finding 2 withdrew, kept in their own
# tuple because `WITHDRAWN_READINGS` is round 9's record about mental states and
# these are a different round's record about a bound. A LOW S1 verdict is
# `k <= 3` at n = 30, not `k = 0`, so a cell saying no record was placed at the
# boundary is false of every arm the row fires on with one to three reaching
# runs — and false arm-wide besides, because `nP >= 3` publishes the sentence
# while the fourth narrow class may read HIGH.
WITHDRAWN_PLACEMENT_CLAIMS = ("none was placed at the boundary",
                              "the records are not at the boundary")
# Round 11, finding 8's withdrawn universal, in its own tuple for the same
# reason: this is a claim about arm D's row 3, and the keying — not the cut — is
# what makes it false. Row 3 reads LOW on the labelled PRIMARY and LOW on S10,
# and an arm D that placed a record at its own (45, 72) in every run and
# mislabelled every one of them reads exactly that. The row is right; the
# sentence beside it was not.
WITHDRAWN_D_PLACEMENT_CLAIM = ("placed records at neither threshold pair",
                               "placed at neither pair")
# The sentence that replaced it, which has to be in BOTH files: the scorer's
# gloss travels into `RATES.md` and `RESULTS.json`, the registered blockquote
# travels nowhere, and a lint over the negative alone would let them drift.
D_PLACEMENT_RESIDUAL = "It does not say the records went nowhere"
# Round 12, finding 2: the same cell's other half, and the third round of one
# defect. §5.1 registers LOW as `k <= 3` at n = 30 and the row fires at LOW on
# THREE of the four narrow numeric classes, so "no coverage" and "no placement"
# were a zero published of an arm that may have reached each of three classes
# three times of thirty and the fourth in every run, on both keyings at once.
# The lint is POSITIVE and derived from the two cuts, because rounds 10 and 11
# both answered this family with a phrase blacklist and a replacement was
# written past each of them — the bound has to be asserted, not merely the
# absence of a word.
D_ROW_THREE_BOUND = (
    "LOW on at least %d of the four narrow numeric classes on each keying, "
    "each of those classes reached at most %d times of 30 and the fourth "
    "free to read HIGH: LOW bounds both, it does not zero either"
    % (score_rates.D_NARROW_MINIMUM, score_rates.low_threshold(30)))
# …with the two withdrawn zeroes kept beside it, as the negative half.
WITHDRAWN_D_ZERO_CLAIM = ("no correctly-labelled coverage", "no placement at")
# Round 12, finding 1: §5.3's row 2 publishes a NAME that is a past-tense
# clause, and its gloss asserted that clause unconditionally one sentence after
# the `why` that disconfirms it — "arm A reads MID there. the denamed text
# degraded authoring generally". §5.3 (iv) registers that only the WITHDRAWAL
# survives an unresolved baseline and the ATTRIBUTION does not, and that
# paragraph travels nowhere while the gloss travels into `RESULTS.json` and
# `RATES.md`. The gloss now carries the condition, in §5.3 (iv)'s own words and
# as a NECESSARY one, so it adds no claim the registration does not already
# make; this is round 11 finding 4's remedy applied to the table round 11 did
# not sweep.
E_ATTRIBUTION_RESIDUAL = "is established only where arm A reads HIGH on class 4"
# The §5.3 (iv) sentence the gloss above is the published copy of. It was the
# load-bearing prose of a registered override with no lint at all, unlike
# `CEILING_LIMIT` and `NAMING_LIMIT` one section over.
E_WITHDRAWAL_LIMIT = ("the withdrawal is a statement about arm E alone and is "
                      "established whatever arm A read")
# The §4.6 ceiling witness needs a LABELLING premise beside its record-type and
# frequency ones — round 13's second named residual. `|Q| = 0` is a claim about
# what the AUTHOR recorded, and the record type fixes only the other side of
# `split_records()`'s comparison. One string asserted in BOTH registered
# statements, as `D_PLACEMENT_RESIDUAL` is, because rounds 12 and 13 each
# corrected this witness and each left it short — and the behaviour is driven
# beside the lint, because a phrase alone can be written past.
WITNESS_LABELLING_PREMISE = (
    "the record type fixes what the mirror returns and not what the author "
    "recorded, so the witness needs the labels too")


def test_the_reading_cells_claim_no_mental_state(preregistration):
    """Round 9, finding 2. §4.6's row-1 reading cell said "the author understood
    the thresholds and did not test them" and §5.3's row 5 published it, on a
    rule that cannot see whether any accepted record exercised a threshold:
    `policy_mirror.verdict()` returns at the sanctions and embargo clauses
    before it reads `riskScore`, so a whole arm of such records reads `|Q| = 0`.

    The registered inference is now what the rule establishes, and this is the
    lint that keeps it there — the §4.6 paragraph must carry its final sentence,
    and no cell of the scorer's own table may reassert either withdrawn reading.
    Without it the weakening can drift back a cell at a time and the parity diff
    would still pass, because the diff only asks that the two sides AGREE.

    Round 11, finding 4: the sentence that licenses the published NAMES is
    linted here too, and it names its two referents. The names travel into
    `RESULTS.json`, `RATES.md` and the row-7 `why`; this paragraph travels
    nowhere, which is why the second reading's gloss now carries its words.
    """
    assert CEILING_LIMIT in fixtures.plain(preregistration)
    assert NAMING_LIMIT in fixtures.plain(preregistration)
    # …and the gloss the name is published with says the same thing, because
    # that is the copy a reader of the published bytes actually holds.
    assert ("named for the explanation it makes available, not for a "
            "proposition this rule establishes"
            in score_rates.READING_TABLE[1]["gloss"])
    for entry in score_rates.READING_TABLE:
        for member in ("reading", "publishedAs", "gloss", "labels",
                       "placementGloss"):
            cell = entry[member]
            for withdrawn in WITHDRAWN_READINGS:
                assert withdrawn not in cell, (
                    "READING_TABLE's %r cell says %r: §4.6 registers that "
                    "|Q| = 0 is a fact about labels and not about the author "
                    "(round 9, finding 2)" % (member, cell))
    # …and the file's own cells, which the parity test holds the code's to.
    for row in reading_rows(preregistration):
        for cell in row:
            for withdrawn in WITHDRAWN_READINGS:
                assert withdrawn not in cell, (cell, withdrawn)


def test_the_ceiling_witness_carries_its_labelling_premise(preregistration,
                                                          pins, study):
    """Round 13's second named residual, and the fourth round on one witness.

    §4.6's degenerate arm E — every accepted record a non-sanctioned SY
    registration — was registered as reading `|Q| = 0` from its record TYPE.
    `split_records()` compares the RECORDED `decision.outcome` against the
    mirror's verdict, so the type fixes one side of that comparison and nothing
    about the other: the same vendors recorded as anything but the mirror's own
    answer are Q and the arm's labels read `degraded`.

    What that costs the arm is row 5's ceiling and nothing else (round 14,
    finding 3). Coverage is EXISTENTIAL within a run — §4.2 counts a run into
    `k` where `H(s) ∩ class_i(s) != {}` — so the run keeps class 4 while any
    one of its class-4 records carries the mirror's own answer, and row 2 reads
    the AGGREGATE level and fires only at LOW. So the MIXED labelling is the
    row this witness has to get right, and the consequence is taken from
    `level_verdict()` and `decision_row()` rather than asserted about them.

    The prose is held by one string in BOTH registered statements; the
    arithmetic is driven at arm E's own registered pair and predicates rather
    than against a transcription of them.
    """
    assert WITNESS_LABELLING_PREMISE in fixtures.plain(preregistration)
    assert WITNESS_LABELLING_PREMISE in fixtures.plain(
        score_rates.decision_row.__doc__)

    definition = score_rates.load_arm(os.path.join(study, "arms"), "E",
                                      pins["arms"]["E"])
    predicate = definition["classes"][score_rates.EMBARGO_CLASS]["predicate"]
    vendor = {"legalName": "Damascus Freight", "sanctionsHit": False,
              "registeredCountry": "SY", "handlesPersonalData": False,
              "riskScore": "12.5"}
    # Derived, not transcribed: the embargo clause answers before `riskScore`.
    mirrored = policy_mirror.verdict(vendor, definition["tLow"],
                                     definition["tHigh"])
    assert mirrored == "reject"

    def population(*outcomes):
        return {"sy-%d" % index: {"caseId": "sy-%d" % index, "vendor": vendor,
                                  "decision": {"outcome": outcome}}
                for index, outcome in enumerate(outcomes, 1)}

    # Three populations of one run: the labels move and the record type does
    # not. `in_primary` is §4.2's own test — H meets the class — so the MIXED
    # row is the one the witness has to get right: the ceiling is gone and the
    # run's coverage is not.
    for outcomes, quarantined, branch, in_primary in (
            ((mirrored, mirrored), 0, "at the ceiling", 2),
            ((mirrored, "clear"), 1, "degraded", 1),
            (("clear", "manual-review"), 2, "degraded", 0)):
        accepted = population(*outcomes)
        high, quarantine = score_rates.split_records(
            accepted, definition["tLow"], definition["tHigh"])
        assert len(quarantine) == quarantined, outcomes
        assert score_rates.label_branch(
            {"rate": len(high) / len(accepted), "h": len(high),
             "q": len(quarantine)})["branch"] == branch, outcomes
        # The record TYPE reaches class 4 on every labelling; only the labels
        # decide whether §4.2's `k` counts the run, and ONE right record is
        # enough for it to.
        assert len(score_rates.class_members(accepted, sorted(accepted),
                                             predicate)) == 2, outcomes
        assert len(score_rates.class_members(accepted, high,
                                             predicate)) == in_primary, outcomes
        # …and it reaches no other class either way, which is the witness's
        # "places nothing in classes 0, 1, 2, 3 and 5" — a predicate fact that
        # needs no labelling premise, unlike the two above it.
        assert [index for index, entry in enumerate(definition["classes"])
                if index != score_rates.EMBARGO_CLASS
                and score_rates.class_members(accepted, sorted(accepted),
                                              entry["predicate"])] == []

    # …and what the premise COSTS the arm, from the two functions that decide
    # it rather than from a sentence. Losing a whole run of thirty leaves class
    # 4 HIGH; row 2 wants LOW, which §5.1 puts at `low_threshold(n)`.
    n = pins["batch"]["n"]
    kept = score_rates.level_verdict(score_rates.rate_block(n - 1, n, "N"))
    lost = score_rates.level_verdict(
        score_rates.rate_block(score_rates.low_threshold(n), n, "N"))
    assert (kept, lost) == ("HIGH", "LOW")

    def row(embargo_level, branch):
        counts = {"nP": 4, "nC": 4, "nH": 0}
        levels = {arm: {"primary": ["HIGH"] * len(definition["classes"])}
                  for arm in fixtures.ARMS}
        levels["E"]["primary"][score_rates.EMBARGO_CLASS] = embargo_level
        return score_rates.decision_row(
            True, True, {}, {"passed": True}, counts,
            reading=score_rates.reading_verdict(counts, branch), levels=levels)

    at_ceiling, degraded = score_rates.S5_BRANCHES
    # The ceiling is what the premise takes, and taking it costs the arm row 5…
    assert row(kept, at_ceiling)["row"] == 5
    assert row(kept, degraded)["row"] == 7
    # …while row 2 is bought by the AGGREGATE alone, on either labelling.
    assert row(lost, at_ceiling)["row"] == 2
    assert row(lost, degraded)["row"] == 2


def test_the_reading_cells_bound_placement_rather_than_zeroing_it(preregistration):
    """Round 10, finding 2. §4.6's row-1 cells said "none was placed at the
    boundary" and "the records are not at the boundary" of a LOW S1 verdict,
    which §5.1 registers as `k <= 3` at n = 30 — up to three of thirty runs
    placing an accepted record in the class, per class, and the sentence is
    published arm-wide at `nP >= 3` while a fourth narrow class may read HIGH.

    `reading_verdict()` carries that cell into `verdicts` and `RESULTS.json`, so
    it is a published sentence and not a table gloss. The parity diff cannot
    catch it — it asks only that the two sides agree — so the withdrawn
    universals are linted out of both, and the surviving cell is tied to the cut
    the scorer computes rather than to a number transcribed beside it.
    """
    for entry in score_rates.READING_TABLE:
        for member in ("reading", "publishedAs", "gloss", "labels",
                       "placementGloss"):
            cell = entry[member]
            for withdrawn in WITHDRAWN_PLACEMENT_CLAIMS:
                assert withdrawn not in cell, (
                    "READING_TABLE's %r cell says %r: a LOW S1 verdict bounds "
                    "placement at %d of 30 and does not zero it (round 10, "
                    "finding 2)"
                    % (member, cell, score_rates.low_threshold(30)))
    for row in reading_rows(preregistration):
        for cell in row:
            for withdrawn in WITHDRAWN_PLACEMENT_CLAIMS:
                assert withdrawn not in cell, (cell, withdrawn)
    # The positive half: the row that confirms names §5.1's own cut, computed.
    cut = "at most %d times of 30" % score_rates.low_threshold(30)
    assert cut in score_rates.READING_TABLE[0]["reading"]
    assert cut in score_rates.READING_TABLE[0]["placementGloss"]
    # …in §5.1's own words, so no second number entered the file.
    assert ("the arm reached the class at most %d times of 30"
            % score_rates.low_threshold(30)) in fixtures.plain(preregistration)


def test_the_label_collapse_cells_name_the_class_they_hold_of(preregistration):
    """Round 11, finding 5, and it is round 10's finding 2 one row down.

    §5.3's row 6 and §4.6's third reading fire on the same condition — `nC >= 3`
    and `nP < 3` — and both published "the records are still at the boundary" of
    an arm on which one or two of the four narrow classes may be genuine
    placement collapses (`nP < 3` is not `nP = 0`), and on which a class that is
    merely *not LOW* may have been reached in as few as four of thirty runs
    against arm A's thirty. What the integers establish is label failure on at
    least `nC - nP` of the four and a BOUND on the rest.

    Both sentences are machine-published — the row's gloss into `RESULTS.json`
    and `ANALYSIS.md`, the reading's cells into `verdicts["reading"]` — so this
    is a published claim and not a table gloss. Asserted over the FILE's cells
    as well as the scorer's, because a parity diff of two agreeing falsehoods
    still passes, and the floor is derived from the cut rather than transcribed
    beside it.
    """
    floor = "as few as %d of 30 runs" % (score_rates.low_threshold(30) + 1)
    decision = score_rates.DECISION_TABLE[5]
    reading = score_rates.READING_TABLE[2]
    assert decision["publishedAs"] == "LABEL-COLLAPSE-ONLY"
    assert reading["publishedAs"] == "label collapse"
    for cell in (decision["gloss"], reading["placementLevel"],
                 reading["reading"]):
        assert "at least one" in cell, (
            "the row fires at nC >= 3 and nP < 3, which is a claim about at "
            "least nC - nP of the four classes and not about the arm: %r"
            % cell)
    for cell in (decision["gloss"], reading["placementGloss"]):
        assert floor in cell, (
            "not LOW is not HIGH: a class this row calls still at the boundary "
            "may be reached in %d of 30 runs (%r)"
            % (score_rates.low_threshold(30) + 1, cell))
    # …and the file's own cells, which the two parity diffs hold the code's to.
    registered_gloss = decision_rows(preregistration)[5][4]
    placement, _labels, registered_reading, _published = \
        reading_rows(preregistration)[2]
    assert "at least one" in registered_gloss and floor in registered_gloss
    assert "at least one" in placement and floor in placement
    assert "at least one" in registered_reading


def test_row_twos_gloss_does_not_assert_the_attribution(preregistration):
    """Round 12, finding 1, and it is round 11's finding 4 one table over.

    Round 11 made row 2 a LEVEL test on arm E and named arm A's own class-4
    level in the published `why`, which is right and is not what this is about.
    What did not follow is the published SENTENCE. `published()` copies the
    gloss verbatim on every firing and `render_markdown()` prints it straight
    after the `why`, so `RATES.md` read "arm E reads LOW on class 4, and arm A
    reads MID there. the denamed text degraded authoring generally" — the fact
    that disconfirms the attribution sitting beside it as an uninterpreted
    datum. §5.3 (iv) registers the split (the withdrawal survives an unresolved
    baseline, the attribution does not) in a blockquote that reaches no
    published byte, and its own closing sentence — "nothing is asserted here
    that the level cannot carry" — was false while the gloss stood.

    The NAME is kept, as `LABEL-COLLAPSE-ONLY` was kept in the same table one
    round earlier: it is registered pre-data, three scenarios key on it and ten
    rounds of review prose describe the file by it. The condition travels in
    the gloss instead, stated as a NECESSARY one so it asserts no sufficiency
    the registration does not.

    Linted on BOTH sides, and on §5.3 (iv) itself, because the parity diff asks
    only that the two sides agree.
    """
    row = score_rates.DECISION_TABLE[1]
    assert row["publishedAs"] == "E-DEGRADED-GENERALLY"
    assert row["outcome"] == "not adjudicated"
    assert E_ATTRIBUTION_RESIDUAL in row["gloss"], (
        "row 2's gloss asserts the attribution unconditionally: §5.3 (iv) "
        "registers that only the withdrawal survives an unresolved baseline "
        "(round 12, finding 1): %r" % row["gloss"])
    assert E_ATTRIBUTION_RESIDUAL in fixtures.plain(preregistration)
    # The withdrawal is the half the level DOES carry, and it stays unqualified.
    assert "every other reading of arm E is withdrawn" in row["gloss"]
    # …and §5.3 (iv)'s own sentence, which the gloss is the published copy of.
    quoted = fixtures.plain(" ".join(line.lstrip("> ")
                                     for line in preregistration.splitlines()))
    assert E_WITHDRAWAL_LIMIT in quoted
    assert ("The row's outcome is not adjudicated in either direction, so "
            "nothing is asserted here that the level cannot carry") in quoted


def test_a_near_ceiling_accuracy_with_one_mislabelled_record_is_degraded():
    """Round 5, finding 13: the cut is the INTEGER `|Q| = 0` §4.6 registers, and
    the scorer compared the published float against 1.0.

    `|H| / (|H| + 1)` is never 1, but the nearest float to it IS exactly 1.0
    once |H| passes 2^53, so an arm holding a mislabelled record reached "at the
    ceiling" — the one S5 branch §4.6's table lets confirm R1. The count below is
    absurd for a batch of thirty runs, and that is the point: a rule registered
    on an integer has to hold at every |H|, not at the ones this study expects to
    see, and the alternative fix — a tolerance — would be a number §4.6 never
    registered.
    """
    h, q = 10 ** 17, 1
    rate = h / (h + q)
    assert rate == 1.0, "the fixture is a fixture only if the float rounds up"
    # Exactly what the old cut asked, kept here so the case cannot quietly stop
    # being the case: on the float alone this arm is at the ceiling.
    assert rate >= score_rates.S5_CEILING
    branch = score_rates.label_branch({"rate": rate, "h": h, "q": q})
    assert branch["branch"] == "degraded"
    assert branch["q"] == 1
    # The fix moves the decision, not the published surface: the float and the
    # registered ceiling are still there to be read.
    assert branch["rate"] == rate
    assert branch["ceiling"] == score_rates.S5_CEILING


def test_the_three_readings_are_reachable_at_known_counts():
    """Each row of §4.6's table, from the counts §5.3's notation registers —
    including the row round 3 found unreachable, which is the whole point:
    a placement collapse whose labels are degraded is a COMPREHENSION collapse
    and does not confirm R1."""
    at_ceiling, degraded = score_rates.S5_BRANCHES
    collapse = {"nP": 4, "nC": 4, "nH": 0}
    placement = score_rates.reading_verdict(collapse, at_ceiling)
    comprehension = score_rates.reading_verdict(collapse, degraded)
    label = score_rates.reading_verdict({"nP": 0, "nC": 4, "nH": 0}, degraded)
    none_of_them = score_rates.reading_verdict({"nP": 0, "nC": 0, "nH": 4},
                                               at_ceiling)
    assert placement["publishedAs"] == "PLACEMENT collapse"
    assert placement["confirmsR1"] is True
    assert comprehension["publishedAs"] == "comprehension collapse"
    assert comprehension["confirmsR1"] is False
    assert label["publishedAs"] == "label collapse"
    assert label["confirmsR1"] is False
    # Round 11, finding 5: `nP < 3` is not `nP = 0`, and the third reading is
    # reached with two of the four narrow classes a genuine placement collapse —
    # which is the arm its cells now have to be true of.
    mixed = score_rates.reading_verdict({"nP": 2, "nC": 4, "nH": 0}, degraded)
    assert mixed["publishedAs"] == "label collapse"
    assert mixed["confirmsR1"] is False
    assert none_of_them["publishedAs"] is None
    # Three of four is the registered pattern minimum here as everywhere else.
    assert score_rates.reading_verdict({"nP": 3, "nC": 3, "nH": 0},
                                       at_ceiling)["confirmsR1"] is True
    assert score_rates.reading_verdict({"nP": 2, "nC": 2, "nH": 0},
                                       at_ceiling)["publishedAs"] is None
    # An unresolved batch has no counts and therefore no reading.
    assert score_rates.reading_verdict({"nP": None, "nC": None, "nH": None},
                                       degraded) is None


# --- §5.3 (ii)'s three registered outcomes for arm D ------------------------

def test_arm_ds_outcomes_are_the_ones_section_5_3_registers(preregistration):
    """Round 3, finding 10: "Three outcomes are registered for arm D, not two",
    and the scorer aggregated outcomes for arm E alone. The two the file names
    are named here, with the two explanations of the first published beside it
    and neither asserted."""
    flat = " ".join(preregistration.split())
    assert "**Three outcomes are registered for arm D, not two.**" in flat
    assert "published as **OLD-EDGE-PREFERENCE**" in flat
    assert "It is a **general degradation**" in flat
    published = [entry["publishedAs"] for entry in score_rates.D_OUTCOME_TABLE]
    assert published == ["COVERAGE-FOLLOWS-THE-NUMBERS", "OLD-EDGE-PREFERENCE",
                         "GENERAL-DEGRADATION", "D-INDETERMINATE"]
    assert score_rates.D_OUTCOME_TABLE[-1]["condition"] == "(else)"
    # Registered with TWO explanations, not one, and nothing in this study
    # separates them — the earlier name asserted the first.
    explanations = score_rates.D_OUTCOME_TABLE[1]["explanations"]
    assert len(explanations) == 2
    assert explanations[0].startswith("contamination")
    assert explanations[1].startswith("round-number salience")
    assert "Nothing in this study separates them" in flat
    assert score_rates.D_OLD_EDGE_NOTE.startswith(
        "Nothing in this study separates the two explanations")
    # The count §5.3 (ii) does not spell is §5.3 (i)'s own, not a new one.
    assert score_rates.D_NARROW_MINIMUM == score_rates.PATTERN_MINIMUM == 3
    # Round 4, finding 6: the first outcome's condition is registered in this
    # sentence, and the scorer's row 1 must be BOTH of its halves. The scorer
    # required all six contrasts to read TRACKING and never consulted the
    # old-keyed levels, which is neither half. The sentence is inside §5.3
    # (ii)'s blockquote and spans three lines, so it is matched with the
    # blockquote markers removed rather than against `flat`.
    quoted = " ".join(" ".join(line.lstrip("> ")
                               for line in preregistration.splitlines()).split())
    assert ("published as **COVERAGE-FOLLOWS-THE-NUMBERS** (new-keyed HIGH on "
            "three or more of the four narrow numeric classes, old-keyed not "
            "HIGH-patterned)") in quoted
    condition = score_rates.D_OUTCOME_TABLE[0]["condition"]
    assert "new-keyed level verdicts are HIGH on 3 or more of the four narrow " \
           "numeric classes" in condition
    assert "old-keyed (S10) verdicts are not HIGH-patterned" in condition
    assert "TRACKING" not in condition


def test_arm_ds_degradation_row_does_not_claim_the_records_went_nowhere(
        preregistration):
    """Round 11, finding 8 — the residual round 10 disclosed by name so this
    round would inherit it rather than rediscover it.

    Row 3's two conditions are LOW on the labelled PRIMARY and LOW on S10, and
    the two keyings are asymmetric by registration: the new-keyed side is
    correctly-labelled coverage under D's own (45, 72), the old-keyed side is
    raw placement under arm A's. An arm D that put a record in each of its four
    narrow numeric classes in all thirty runs and mislabelled every one of them
    therefore reads LOW on both sides and reaches this row — while its records
    are exactly where D's own policy says to put them. "The author placed
    records at neither threshold pair" was false of that arm, and it was
    published: the gloss goes into `RATES.md` beside the `why`.

    The registered sentence and the scorer's cell now say what the two LOW
    readings support and point at D's own S1 placement rates, which are already
    published per class, for the case they do not separate. Linted in the house
    form because the parity diff only asks that the two sides AGREE, so a
    withdrawn universal can walk back into both of them together.
    """
    quoted = fixtures.plain(" ".join(line.lstrip("> ")
                                     for line in preregistration.splitlines()))
    for withdrawn in WITHDRAWN_D_PLACEMENT_CLAIM:
        assert withdrawn not in quoted, (
            "§5.3 (ii) says %r: row 3 reads LOW on the labelled primary and LOW "
            "on S10, which an arm D that placed correctly at its own pair and "
            "mislabelled also reads (round 11, finding 8)" % withdrawn)
        for entry in score_rates.D_OUTCOME_TABLE:
            for member in ("condition", "publishedAs", "gloss"):
                assert withdrawn not in entry[member], (entry["row"], member)
    # The positive half, tied on both sides: the gloss travels into `RATES.md`
    # and `RESULTS.json`, the blockquote travels nowhere, and a lint over the
    # withdrawn phrases alone would let the two drift a word at a time.
    assert D_PLACEMENT_RESIDUAL in quoted
    degradation = score_rates.D_OUTCOME_TABLE[2]
    assert degradation["publishedAs"] == "GENERAL-DEGRADATION"
    assert D_PLACEMENT_RESIDUAL in degradation["gloss"]
    assert "S1 placement rates" in degradation["gloss"]
    assert "S1 placement rates" in quoted
    # Row 3's CONDITION is accurate and is NOT what moved: only the gloss
    # asserted something the two LOW readings do not support.
    assert ("new-keyed level verdicts are LOW on at least %d of the four narrow "
            "numeric classes" % score_rates.D_NARROW_MINIMUM) \
        in degradation["condition"]
    assert ("old-keyed (S10) verdicts are LOW on at least %d of them"
            % score_rates.D_NARROW_MINIMUM) in degradation["condition"]
    # Round 12, finding 2: the cell's other half. "No coverage" and "no
    # placement" are zeroes, and neither keying reads zero — LOW is `k <= 3`
    # and the row asks for it on three of the four classes, so the fourth is
    # free to read HIGH in all thirty runs on both sides at once. The bound is
    # asserted positively and derived from the two registered cuts, because a
    # third blacklist entry is what the last two rounds already tried.
    assert D_ROW_THREE_BOUND in degradation["gloss"], degradation["gloss"]
    assert D_ROW_THREE_BOUND in quoted
    for withdrawn in WITHDRAWN_D_ZERO_CLAIM:
        assert withdrawn not in quoted, (
            "§5.3 (ii) says %r of a row that fires at LOW on %d of the four "
            "narrow numeric classes, and LOW is %d of 30 and not 0 (round 12, "
            "finding 2)"
            % (withdrawn, score_rates.D_NARROW_MINIMUM,
               score_rates.low_threshold(30)))
        for entry in score_rates.D_OUTCOME_TABLE:
            for member in ("condition", "publishedAs", "gloss"):
                assert withdrawn not in entry[member], (entry["row"], member)


def test_arm_ds_outcome_is_computed_from_the_registered_levels():
    """The four rows at known level verdicts, over the six classes: the
    predicted tracking, the old-edge preference, the general degradation, and
    the cases §5.3 (ii) names no outcome for.

    Round 4, finding 6: every row is driven by the LEVELS, because that is what
    the registered conditions are stated on. The contrast argument is varied
    under a fixed pair of level vectors to show it decides nothing.
    """
    tracking = [{"index": index, "contrast": "TRACKING"} for index in range(6)]
    indeterminate = [{"index": index,
                      "contrast": "TRACKING" if index in (3, 4)
                      else "INDETERMINATE"} for index in range(6)]
    high_six = ["HIGH"] * 6
    # New-keyed LOW on the four narrow numeric classes, HIGH on 3 and 4.
    new_low = ["LOW", "LOW", "LOW", "HIGH", "HIGH", "LOW"]
    old_high = ["HIGH", "HIGH", "HIGH", "HIGH", "HIGH", "HIGH"]
    old_low = ["LOW", "LOW", "LOW", "HIGH", "HIGH", "LOW"]
    # New-keyed HIGH on the narrow classes, old-keyed not HIGH-patterned: the
    # registered condition, and it holds whatever the contrasts read — the
    # second call is the same levels with two contrasts INDETERMINATE, which the
    # earlier all-six-TRACKING rule published as D-INDETERMINATE.
    for rows in (tracking, indeterminate):
        follows = score_rates.arm_d_outcome(high_six, old_low, rows)
        assert follows["publishedAs"] == "COVERAGE-FOLLOWS-THE-NUMBERS"
        assert follows["counts"]["newKeyedHigh"] == 4
        assert follows["counts"]["oldKeyedHigh"] == 0
    preference = score_rates.arm_d_outcome(new_low, old_high, indeterminate)
    assert preference["publishedAs"] == "OLD-EDGE-PREFERENCE"
    assert preference["counts"] == {"newKeyedHigh": 0, "newKeyedLow": 4,
                                    "oldKeyedHigh": 4, "oldKeyedLow": 0,
                                    "tracking": 2, "narrowMinimum": 3,
                                    "classes": 6}
    assert len(preference["explanations"]) == 2 and preference["separates"]
    degradation = score_rates.arm_d_outcome(new_low, old_low, indeterminate)
    assert degradation["publishedAs"] == "GENERAL-DEGRADATION"
    assert degradation["explanations"] == []
    # Two narrow classes LOW is one short of the registered three, and the file
    # names no outcome for the mixed case: it is published as one.
    mixed = ["LOW", "LOW", "MID", "HIGH", "HIGH", "MID"]
    assert score_rates.arm_d_outcome(mixed, old_low,
                                     indeterminate)["publishedAs"] \
        == "D-INDETERMINATE"
    # And the old-keyed exclusion, which the scorer never used to compute: the
    # SAME new-keyed levels that read COVERAGE-FOLLOWS-THE-NUMBERS above, with
    # the old edges held too, are not it — the records cover both threshold
    # pairs, so the numbers separate nothing. TRACKING on all six contrasts does
    # not rescue it, which is exactly what the earlier rule got wrong.
    both = score_rates.arm_d_outcome(high_six, old_high, tracking)
    assert both["publishedAs"] == "D-INDETERMINATE"
    assert both["counts"] == {"newKeyedHigh": 4, "newKeyedLow": 0,
                              "oldKeyedHigh": 4, "oldKeyedLow": 0,
                              "tracking": 6, "narrowMinimum": 3, "classes": 6}


# --- §5.4's operating characteristics ---------------------------------------

OC_HEADER = ["registered rule", "where", "N = 20", "N = 25", "N = 30"]
TRIALS = (20, 25, 30)
# The MARGINAL pattern probabilities §5.4 publishes, recomputed here rather
# than copied: `nH >= 3` reads arm E's own levels, `nP >= 3` needs arm A HIGH
# on the same class as well.
REGISTERED_MARGINAL_NH = {20: 0.7142, 25: 0.9187, 30: 0.9796}
# The JOINT probability of REACHING decision row 4, which §5.4 labelled the
# marginal with (round 3, finding 11): row 4 is reached only when arm E does
# not collapse on class 4 (row 2) and the B/C control gate passes (row 3), so
# the marginal is multiplied by the gate's 0.0557 / 0.4031 / 0.7658. Seven
# significant figures, computed by `decision_operating_characteristics()` with
# this study's own interval code; the amendment §5.4 needs must carry these.
REGISTERED_JOINT_ROW4 = {20: 0.03978409, 25: 0.3703584, 30: 0.7501924}
REGISTERED_JOINT_ROW5 = {20: 0.0364, 25: 0.3536, 30: 0.7359}
# Round 10, finding 4: the same five rules with §5.4's layer 1 repaired on the
# two nested class pairs. Pinned the way the joint rows above are — to the
# places §5.4 publishes them — so the companion cannot drift back out of the
# registration, and read off `containment_operating_characteristics()` rather
# than off its sibling.
REGISTERED_CONTAINMENT = {
    "nP": {20: 0.4276, 25: 0.7188, 30: 0.8699},
    "gate": {20: 0.1078, 25: 0.4010, 30: 0.6702},
    "row5": {20: 0.0714, 25: 0.3408, 30: 0.6253},
    "nH": {20: 0.6845, 25: 0.8588, 30: 0.9358},
    "row4": {20: 0.0738, 25: 0.3444, 30: 0.6272},
}
# The §5.4 row each of those is published in, by the row label's own prefix.
# The prefixes are deliberately disjoint from the independence rows' — a
# companion row beginning "the B/C control gate" would make the prefix match
# above ambiguous, which is the parser telling the file how to name its rows.
CONTAINMENT_ROWS = {
    "under containment — nP >= 3": "nP",
    "under containment — the B/C control gate": "gate",
    "under containment — the coverage-side CONFIRMED-and-gate quantity": "row5",
    "under containment — nH >= 3": "nH",
    "under containment — row 4 reached": "row4",
}


def operating_characteristics(body: str) -> dict:
    """§5.4's operating-characteristic table, keyed by the rule's own first
    cell, as {rule: {trials: printed value}}."""
    rows = {}
    for rule, _where, twenty, twenty_five, thirty in table(body, OC_HEADER):
        rows[rule] = dict(zip(TRIALS, (float(twenty), float(twenty_five),
                                       float(thirty))))
    return rows


@pytest.mark.parametrize("trials", TRIALS)
def test_the_registered_operating_characteristics_are_reproduced(trials,
                                                                 preregistration):
    """§5.4's own table, rule by rule, against this file's arithmetic — the
    figures it publishes for the rules §5.3 registers.

    Every row here is computed from `level_operating_characteristics()`'s two
    probabilities under §5.4's registered scenario, so a cut that moved would
    move these numbers and this test rather than being noticed later.
    """
    characteristics = score_rates.decision_operating_characteristics(trials)
    level_high = score_rates.level_operating_characteristics(
        trials, Fraction(19, 20))
    level_collapsed = score_rates.level_operating_characteristics(
        trials, Fraction(1, 20))
    # The joint arithmetic stands on the same two marginals §5.4's first table
    # publishes, and not on a second derivation of them.
    assert characteristics["pHigh"] == level_high["pHigh"]
    assert characteristics["pLowCollapsed"] == level_collapsed["pLow"]
    q, collapsed = characteristics["pHigh"], characteristics["pLowCollapsed"]
    computed = {
        "per-class COLLAPSE": q * collapsed,
        "all four narrow COLLAPSE": (q * collapsed) ** 4,
        "nP >= 3": characteristics["marginal"]["nP"],
        "the B/C control gate": characteristics["gate"],
        "all twelve TRACKING": q ** 18,
        "CONFIRMED and the gate holds": characteristics["joint"]["row5"],
        "nH >= 3": characteristics["marginal"]["nH"],
    }
    registered = operating_characteristics(preregistration)
    # Round 5, finding 5: the two renamed rows must CARRY their renames —
    # a prefix match alone would let the coverage-side qualifiers drift
    # back out of the registration unnoticed.
    qualified = {"CONFIRMED and the gate holds": "coverage-side",
                 "nP": "coverage pattern"}
    for prefix, value in computed.items():
        matched = [rule for rule in registered if rule.startswith(prefix)]
        assert len(matched) == 1, (
            "§5.4 holds %d rules beginning %r" % (len(matched), prefix))
        for stem, needed in qualified.items():
            if prefix.startswith(stem):
                assert needed in matched[0], (
                    "§5.4's %r row lost its %r qualifier"
                    % (matched[0], needed))
        printed = registered[matched[0]][trials]
        assert abs(value - printed) < 5e-5, (
            "§5.4 prints %s for %r at N = %d; this file computes %.6f"
            % (printed, matched[0], trials, value))


@pytest.mark.parametrize("trials", TRIALS)
def test_the_power_to_reach_row_four_is_not_the_marginal(trials):
    """Round 3, finding 11: §5.4 labels `0.7142 / 0.9187 / 0.9796` "the power to
    reach decision row 4", and they are the marginal `P(nH >= 3)`. Reaching row
    4 also requires that arm E does not read LOW on class 4 (row 2) and that the
    B/C control gate passes (row 3), and the decision table is evaluated in that
    order — so the power to publish R1-UNSUPPORTED is the smaller number.

    Both are pinned here, to the places each is published at, so the amendment
    §5.4 needs is machine-checked the moment it lands: the marginal row keeps
    its figures and the new joint row must carry `REGISTERED_JOINT_ROW4`.
    """
    characteristics = score_rates.decision_operating_characteristics(trials)
    marginal = characteristics["marginal"]["nH"]
    joint = characteristics["joint"]["row4"]
    assert round(marginal, 4) == REGISTERED_MARGINAL_NH[trials]
    assert "%.7g" % joint == "%.7g" % REGISTERED_JOINT_ROW4[trials]
    assert round(characteristics["joint"]["row5"], 4) \
        == REGISTERED_JOINT_ROW5[trials]
    # Round 9, finding 2: row 5 gained a fifth conjunct — arm E does not read
    # LOW on class 3 — and it enters this model as `1 - P(E class 3 LOW)`, in
    # EVERY arm-A pattern, because round 10 finding 3 made it a level verdict on
    # arm E and it therefore reads arm A not at all. Round 11 finding 1: the
    # class-4 term has that shape too now, for the same reason — it used to be
    # `1 - P(A HIGH) * P(E class 4 LOW)` and to drop out of the one arm-A
    # pattern in which row 2 had stopped gating anything. E's class 3 sits at
    # p = 0.95 in §5.4's registered scenario just as its class 4 does. All
    # either term can subtract from `row5` is bounded by `pLowIntact`, so every
    # printed §5.4 figure stands — the bound and the figure are asserted
    # separately, because deriving one from the other would check nothing.
    assert characteristics["pLowIntact"] < 5e-5 / 2
    assert abs(characteristics["joint"]["row5"]
               - REGISTERED_JOINT_ROW5[trials]) < 5e-5
    # The joint figure IS the marginal times the gate times the class-4 term —
    # exactly, since round 11 finding 1 made row 2 a level verdict on arm E and
    # the term a constant factor rather than a per-shape one. Arm E's class 4
    # sits at p = 0.95 in this scenario and reading LOW there is a 1e-23 event,
    # so the two agree to every place §5.4 prints and the difference below is
    # the double's own epsilon, not the term.
    assert characteristics["pLowIntact"] < 1e-20
    assert abs(joint - marginal * characteristics["gate"]) < 1e-12
    assert joint < marginal
    # …and the gate is what does it: at N = 20 the design's own precondition for
    # reading arm E holds one time in eighteen.
    assert round(characteristics["gate"], 4) == {20: 0.0557, 25: 0.4031,
                                                 30: 0.7658}[trials]


def test_the_joint_row_four_figures_are_checked_against_the_file(preregistration):
    """The half of the previous test that binds the FILE.

    §5.4 CARRIES the joint row — the amendment round 3's finding 11 called for
    is what added it, in the same commit as this test — so this requires the
    row to BE there, exactly once, and to carry the computed figures rather
    than a second transcription of them. Round 12, finding 3: the old `<= 1`
    admitted zero rows and then looped over nothing, so deleting the registered
    row passed here vacuously, and the pins above bind
    `decision_operating_characteristics()` and not the file, so nothing else in
    the suite would have noticed.
    """
    registered = operating_characteristics(preregistration)
    joint_rows = [rule for rule in registered if rule.startswith("row 4 reached")]
    assert len(joint_rows) == 1, (
        "§5.4 holds %d rules beginning %r" % (len(joint_rows), "row 4 reached"))
    rule = joint_rows[0]
    for trials in TRIALS:
        computed = score_rates.decision_operating_characteristics(
            trials)["joint"]["row4"]
        assert abs(computed - registered[rule][trials]) < 5e-5, (
            "§5.4's joint row 4 prints %s at N = %d; this file computes %.7f"
            % (registered[rule][trials], trials, computed))


# --- §5.4's containment companion (round 10, finding 4) ---------------------

# §5.4's two SIX-COLUMN joint-figure tables, which no test read until round 10:
# the independence one it has published since round 2, and the
# containment-respecting companion beside it. Identified by their headers like
# every other table here, and the headers differ in exactly the cell whose
# meaning differs — a loose floor computed for six free events against the sharp
# one four indicators imply.
JOINT_HEADER = ["true p", "P(HIGH), one class", "P(all four narrow HIGH)",
                "P(all six HIGH)", "Fréchet lower bound on all six",
                "P(all twelve TRACKING, B and C)"]
CONTAINMENT_JOINT_HEADER = (JOINT_HEADER[:4]
                            + ["sharp Fréchet floor on all six",
                               JOINT_HEADER[5]])
JOINT_TRIALS = 30                      # both joint tables are §5.4's at N = 30


def containment_values(characteristics: dict) -> dict:
    """The five companion quantities, keyed as `CONTAINMENT_ROWS` keys them."""
    return {"nP": characteristics["marginal"]["nP"],
            "gate": characteristics["gate"],
            "row5": characteristics["joint"]["row5"],
            "nH": characteristics["marginal"]["nH"],
            "row4": characteristics["joint"]["row4"]}


@pytest.mark.parametrize("trials", TRIALS)
def test_the_containment_companion_rows_are_reproduced(trials, preregistration):
    """Round 10, finding 4. §5.4's layer 1 treats the six per-class indicators of
    an arm as independent, and §2.3's class 0 nests in class 1 and class 2 in
    class 3 — so those indicators are ordered pathwise and independence between
    them is available at no nondegenerate marginals. The five rules that carry N
    are therefore published twice, and this is the diff for the second set.

    The sibling's figures are NOT recomputed here and must not move: they stay
    published as the incoherent approximation they are, and
    `test_the_power_to_reach_row_four_is_not_the_marginal` still pins them.
    """
    characteristics = score_rates.containment_operating_characteristics(trials)
    computed = containment_values(characteristics)
    registered = operating_characteristics(preregistration)
    for prefix, key in sorted(CONTAINMENT_ROWS.items()):
        matched = [rule for rule in registered if rule.startswith(prefix)]
        assert len(matched) == 1, (
            "§5.4 holds %d rules beginning %r" % (len(matched), prefix))
        assert round(computed[key], 4) == REGISTERED_CONTAINMENT[key][trials]
        printed = registered[matched[0]][trials]
        assert abs(computed[key] - printed) < 5e-5, (
            "§5.4 prints %s for %r at N = %d; this file computes %.6f"
            % (printed, matched[0], trials, computed[key]))
    # The companion stands on the SAME two marginals as its sibling — it repairs
    # the joint model and nothing else — and on the groups §2.3's nesting
    # leaves, which `test_mirror.py` asserts over the landmark grid.
    sibling = score_rates.decision_operating_characteristics(trials)
    assert characteristics["pHigh"] == sibling["pHigh"]
    assert characteristics["pLowCollapsed"] == sibling["pLowCollapsed"]
    assert characteristics["pLowIntact"] == sibling["pLowIntact"]
    assert characteristics["groups"] == [[0, 1], [2, 3], [4], [5]]
    # The three rules §5.4 companions in PROSE rather than in a row of its own.
    section = "\n".join(section_5_4(preregistration))
    for key in ("perClassCollapse", "allFourNarrowCollapse"):
        assert "%.4f" % characteristics[key] in section, key
    assert "%.4f" % characteristics["conjunctions"]["allTwelveTracking"] in section
    # …and per-class COLLAPSE is a MARGINAL, so the containment leaves it where
    # it was: the row §5.4 says does not move must not move. The two sides are
    # the same exact rational rounded at different points, so the comparison is
    # to the double's own epsilon and not to a tolerance.
    assert abs(characteristics["perClassCollapse"]
               - sibling["pHigh"] * sibling["pLowCollapsed"]) < 1e-15


def test_the_unequal_marginal_pair_is_coupled_and_not_multiplied():
    """Round 11, finding 2. The companion merged each nested pair at EQUAL
    marginals and, where the marginals differ, multiplied the pair's two LOW
    indicators — layer-1 independence left standing between arm E's class 2 and
    class 3, which is the very thing round 10 condemned the sibling for.

    The repair is invisible in doubles: the two exact rationals collapse to the
    same IEEE double at every registered N, which is why `REGISTERED_CONTAINMENT`
    above is unedited. So this binds the SHAPE instead of the digits, on
    synthetic rationals where the coupling is large enough to see.

    At `low = 1/2`, `nested_low = 1/4`, other weights (2, 1) and a nested weight
    of 1, the coupled value is exactly `(l - n)·l + (1 - l)·l² = 1/4` against the
    product form's `(1 - n)·P(nP >= 3) = 3/4 · 3/8 = 9/32`. The product
    OVERSTATES by 1/32, in the same direction the repair moves row 5.
    """
    low, nested_low = Fraction(1, 2), Fraction(1, 4)
    others, nested_weight = (2, 1), 1
    coupled = score_rates._ordered_placement(3, others, nested_weight,
                                             low, nested_low)
    product = (1 - nested_low) * score_rates._weighted_at_least(
        3, others + (nested_weight,), low)
    assert coupled == Fraction(1, 4)
    assert product == Fraction(9, 32)
    assert product - coupled == Fraction(1, 32)
    assert coupled == ((low - nested_low) * low + (1 - low) * low ** 2)
    # The fourth cell of the containment's 2x2 table is EMPTY by construction:
    # {3 LOW} is a subset of {2 LOW}, so at equal marginals "3 not LOW" carries
    # "2 not LOW" and the nested group can contribute nothing to `nP` — the same
    # value the helper returns when arm A is not HIGH on that group at all.
    assert (score_rates._ordered_placement(3, others, nested_weight, low, low)
            == score_rates._ordered_placement(3, others, 0, low, low)
            == (1 - low) * score_rates._weighted_at_least(3, others, low))
    # …and where the group carries nothing into `nP` the two events really are
    # independent, so the product is exact and the helper agrees with it.
    assert (score_rates._ordered_placement(3, others, 0, low, nested_low)
            == (1 - nested_low) * score_rates._weighted_at_least(3, others, low))
    # An outer class more likely to read LOW than its inner one is not a
    # dependence to model but a scenario containment forbids, and the helper
    # refuses it rather than returning a negative cell.
    with pytest.raises(ValueError) as caught:
        score_rates._ordered_placement(3, others, nested_weight,
                                       nested_low, low)
    assert "infeasible scenario" in str(caught.value)
    # The registered scenario satisfies the feasibility containment implies at
    # every N: class 3 sits at p = 0.95 and class 2 at p = 0.05, and the ordering
    # says the intact class cannot be the likelier of the two to read LOW.
    for trials in TRIALS:
        figures = score_rates.containment_operating_characteristics(trials)
        assert figures["pLowIntact"] <= figures["pLowCollapsed"]


def test_the_nested_pairs_make_layer_one_unavailable(preregistration):
    """The arithmetic §5.4's new sentences stand on, asserted rather than
    transcribed (round 10, finding 4).

    Two claims. FIRST, that two of the independence table's cells are not merely
    modelled wrongly but attainable by no population with these marginals: with
    the nestings respected the six classes are four indicators, so the sharp
    Fréchet floor on the all-six conjunction is `max(0, 4q - 3)` and not the
    printed `max(0, 6q - 5)`, and `q**6` falls below it at N = 25 and N = 30.
    Exact rationals throughout — whether a cell is inside the feasible set is
    not a question a double should answer.

    SECOND, the DIRECTION, which is what §5.4's withdrawn sentence had wrong:
    conjunctions rise under containment at every N, tolerances fall at the two
    N's [D-1] compares, and at N = 20 four of the five tolerance rules rise
    instead because at `q = 0.7358` five-of-six is in practice a conjunction.
    The non-uniformity is asserted, not smoothed over: a test that only checked
    "smaller" would be pinning a claim the file does not make.
    """
    scenario = Fraction(19, 20)
    for trials in (25, 30):
        q = score_rates.probability_at_least(
            score_rates.high_threshold(trials), trials, scenario)
        assert q ** 6 < 4 * q - 3, trials
        assert q ** 4 < 3 * q - 2, trials
        # …and the cell that is NOT infeasible, so the claim stays the narrow one
        assert q ** 18 > 12 * q - 11, trials
    twenty = score_rates.probability_at_least(
        score_rates.high_threshold(20), 20, scenario)
    assert 4 * twenty - 3 < 0 and twenty ** 6 > 0
    assert twenty ** 4 > 3 * twenty - 2
    # A degenerate arm is the one place the conjunction meets its floor.
    perfect = score_rates.probability_at_least(
        score_rates.high_threshold(30), 30, Fraction(1))
    assert perfect ** 6 == 4 * perfect - 3 == 1

    for trials in TRIALS:
        q = score_rates.probability_at_least(
            score_rates.high_threshold(trials), trials, scenario)
        indep = score_rates.decision_operating_characteristics(trials)
        containment = score_rates.containment_operating_characteristics(trials)
        # Conjunctions: fewer indicators, so a larger product, at every N.
        assert q ** 4 > q ** 6 and q ** 3 > q ** 4 and q ** 12 > q ** 18
        conjunctions = containment["conjunctions"]
        assert conjunctions["allSix"] == float(q ** 4)
        assert conjunctions["allFourNarrow"] == float(q ** 3)
        assert conjunctions["allTwelveTracking"] == float(q ** 12)
        # Tolerances: down at 25 and 30, up at 20 — except `nH >= 3`, which is
        # down at all three.
        falls = trials in (25, 30)
        for key, value in sorted(containment_values(containment).items()):
            sibling = {"nP": indep["marginal"]["nP"], "gate": indep["gate"],
                       "row5": indep["joint"]["row5"],
                       "nH": indep["marginal"]["nH"],
                       "row4": indep["joint"]["row4"]}[key]
            assert (value < sibling) is (falls or key == "nH"), (trials, key)
        # …and the companion is a SCENARIO, not a bound: one coherent coupling
        # in the other direction puts the gate well above it.
        assert containment["comonotoneGate"] > containment["gate"]

    # Every corrected floor, cap and conjunction §5.4 and §2.1 print in PROSE
    # rather than in a table cell, so none of them is a transcription either.
    section = "\n".join(section_5_4(preregistration))
    for trials in (25, 30):
        figures = score_rates.containment_joint_figures(trials, scenario)
        for key in ("frechetAllSix", "frechetAllFourNarrow", "cap", "allSix",
                    "allFourNarrow"):
            assert "%.4f" % figures[key] in preregistration, (trials, key)
        # …and the two "runs in ten" halves, which §5.4's baseline bullet used
        # to pair across two different quantities at two different N.
        assert "%.4f" % (1 - figures["allSix"]) in section, trials
    for p_text in ("0.98", "0.95"):
        assert "%.4f" % score_rates.containment_joint_figures(
            30, Fraction(p_text))["frechetAllTwelve"] in section, p_text
    twenty_figures = score_rates.containment_joint_figures(20, scenario)
    assert "%.4f" % twenty_figures["frechetAllFourNarrow"] in section
    assert "%.4f" % float(twenty) in section
    assert "%.4f" % score_rates.containment_operating_characteristics(
        30)["comonotoneGate"] in section
    # §2.1's registered DRIFT rule quotes its own false-positive rate, and the
    # containment moves that one by more than an order of magnitude because the
    # rule counts CLASSES and a nested pair carries two of them at once.
    #
    # Round 16, finding 5: the rendering check below is a SECOND assertion, not
    # the guard. §2.1's rule has two limbs — four or more classes below HIGH,
    # OR any one class LOW — and the code carried only the first. No 4dp or
    # float-valued assertion could ever have caught that: the one-limb and
    # two-limb figures are the SAME IEEE double at every registered N, so the
    # existing check was incapable of failing on the missing limb at any
    # precision. What holds the RULE is exact rational arithmetic, plus a
    # marginal where the limbs visibly separate.
    for trials in (20, 25, 30):
        weights = tuple(len(group) for group in score_rates.class_groups())
        high = score_rates.probability_at_least(
            score_rates.high_threshold(trials), trials, score_rates.SCENARIO_P)
        low = score_rates._tail_le(score_rates.low_threshold(trials), trials,
                                   score_rates.SCENARIO_P)
        both = score_rates._drift_suspected(weights, high, low)
        one = score_rates._weighted_at_least(
            score_rates.DRIFT_SUSPECTED_MINIMUM, weights, 1 - high)
        # The second limb is really there, exactly…
        assert both > one, trials
        # …and this is WHY no printed digit moves: the two collapse to one
        # double, which is the fact that made the old assertion vacuous.
        assert "%.4f" % float(both) == "%.4f" % float(one), trials
        assert float(score_rates.containment_operating_characteristics(
            trials)["driftSuspected"]) == float(both), trials
    # Visible rather than at 1e-31: at a marginal where a class is LOW one time
    # in ten, the whole rule fires at 0.3536 and the four-of-six limb alone at
    # 0.0528. An implementation carrying one limb fails here by a wide margin.
    assert score_rates._drift_suspected(
        (2, 2, 1, 1), Fraction(4, 5), Fraction(1, 10)) == Fraction(221, 625)
    assert score_rates._weighted_at_least(
        score_rates.DRIFT_SUSPECTED_MINIMUM, (2, 2, 1, 1),
        Fraction(1, 5)) == Fraction(33, 625)
    # And the power the second limb is FOR, which is why §2.1 registers it: a
    # single class collapsed to p = 0.05 reads LOW nine times in ten and puts at
    # most two of six classes below HIGH, so the four-of-six limb alone never
    # fires on it.
    collapsed = score_rates._tail_le(score_rates.low_threshold(30), 30,
                                     score_rates.SCENARIO_P_COLLAPSED)
    assert collapsed > Fraction(9, 10)
    for trials in (25, 30):
        drift = score_rates.containment_operating_characteristics(
            trials)["driftSuspected"]
        assert "%.4f" % drift in preregistration, trials


def test_the_joint_figures_tables_are_the_scorers_arithmetic(preregistration):
    """§5.4's six-column joint tables, cell by cell.

    Round 10, finding 4's second half: the independence table — the source of
    `q⁶`, `q¹⁸` and the Fréchet column — was parsed by NO test through nine
    review rounds, so every one of its cells was a transcription. It is parsed
    here beside its containment-respecting companion, both against this study's
    own arithmetic, and the infeasibility that separates them is asserted from
    the exact rationals rather than from the printed four places.
    """
    independence = table(preregistration, JOINT_HEADER)
    containment = table(preregistration, CONTAINMENT_JOINT_HEADER)
    assert [row[0] for row in independence] == [row[0] for row in containment]
    assert [row[0] for row in independence] == ["1.00", "0.98", "0.95"]

    for p_text, one, four, six, floor, twelve in independence:
        q = score_rates.probability_at_least(
            score_rates.high_threshold(JOINT_TRIALS), JOINT_TRIALS,
            Fraction(p_text))
        for column, printed, value in (
                ("P(HIGH)", one, q),
                ("all four narrow", four, q ** 4),
                ("all six", six, q ** 6),
                ("Fréchet", floor, max(Fraction(0), 6 * q - 5)),
                ("all twelve", twelve, q ** 18)):
            assert "%.4f" % float(value) == printed, (
                "§5.4's joint table prints %s for %s at p = %s; this file "
                "computes %.6f" % (printed, column, p_text, float(value)))

    for p_text, one, four, six, floor, twelve in containment:
        figures = score_rates.containment_joint_figures(
            JOINT_TRIALS, Fraction(p_text))
        for key, printed in (("q", one), ("allFourNarrow", four),
                             ("allSix", six), ("frechetAllSix", floor),
                             ("allTwelveTracking", twelve)):
            assert "%.4f" % figures[key] == printed, (
                "§5.4's containment table prints %s for %s at p = %s; this "
                "file computes %.6f" % (printed, key, p_text, figures[key]))
        # A containment-respecting figure is by construction inside the feasible
        # set its own floor draws; if it were not, the companion would be as
        # unreachable as the table it corrects.
        assert figures["allSix"] >= figures["frechetAllSix"]
        assert figures["allFourNarrow"] >= figures["frechetAllFourNarrow"]
        assert figures["allSix"] <= figures["cap"]

    # The two cells §5.4 names as reachable by no population, at BOTH nondegenerate
    # p rows the table prints — and the degenerate row, where the floor is met.
    for p_text in ("0.98", "0.95"):
        q = score_rates.probability_at_least(
            score_rates.high_threshold(JOINT_TRIALS), JOINT_TRIALS,
            Fraction(p_text))
        assert q ** 6 < max(Fraction(0), 4 * q - 3), p_text
        assert q ** 4 < max(Fraction(0), 3 * q - 2), p_text


# --- §5.4's MARGINAL level table (round 9, finding 12) ----------------------

LEVEL_OC_HEADER = ["true p", "P(HIGH)", "P(LOW)", "P(MID)"]
# Round 9, finding 12: §5.4's note said every 0.0000 in the FILE was rounded,
# and these four cells are exact — at p = 1 no outcome has k <= 3, at p = 0
# none has k >= 27. Pinned as a SET so that a cut which moved and made a fifth
# cell exactly zero fires here and forces the note to be rewritten with it.
EXACT_ZERO_CELLS = {("1.00", "P(LOW)"), ("1.00", "P(MID)"),
                    ("0.00", "P(HIGH)"), ("0.00", "P(MID)")}
ZERO_NOTE_P = Fraction(3, 10)          # the row §5.4's note gives a figure for
BANNED_ZERO_NOTE_FIGURE = "4 × 10⁻¹¹"  # the figure round 9 found; not any tail
SUPERSCRIPT = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def level_cells(body: str) -> dict:
    """§5.4's MARGINAL table as {(printed p, column): (printed cell, computed
    value)} — the file's own cells beside this study's own arithmetic."""
    cells = {}
    for p_text, *printed in table(body, LEVEL_OC_HEADER):
        characteristics = score_rates.level_operating_characteristics(
            30, Fraction(p_text))
        for column, cell, key in zip(LEVEL_OC_HEADER[1:], printed,
                                     ("pHigh", "pLow", "pMid")):
            cells[(p_text, column)] = (cell, characteristics[key])
    return cells


def test_the_marginal_level_table_is_the_scorers_arithmetic(preregistration):
    """§5.4's opening sentence says this table is asserted by a harness test.
    Round 5 pinned the DECISION-rule characteristics and round 3 the interval
    vectors; nothing diffed the marginal level table until round 9 finding 12."""
    cells = level_cells(preregistration)
    assert len(cells) == 12 * 3
    for (p_text, column), (printed, value) in sorted(cells.items()):
        assert "%.4f" % value == printed, (
            "§5.4 prints %s for %s at p = %s; this file computes %.6e"
            % (printed, column, p_text, value))


# --- §5.4's PROSE, pinned by phrase (round 6, finding 4) ---------------------

SECTION_HEADING = "### 5.4 "
# The three names round 6 finding 4 found §5.4's prose still giving these
# figures. Each asserts something §5.4's own coverage-side paragraph withdraws:
# that the number is the joint the study will report, that it is the chance of
# arriving at row 5, and that it covers the whole CONFIRMED conjunction.
BANNED_5_4_PHRASES = ("the actual joint", "actually reaching row 5",
                      "whole registered CONFIRMED outcome")
COVERAGE_SIDE = "coverage-side"
# §5.4's CONFIRMED-side figure at N = 30, which is the one the false names were
# attached to. Where the prose discusses it, the prose names what it is.
CONFIRMED_FIGURE = "0.7359"


def section_5_4(body: str) -> list:
    """§5.4's own lines, from its heading down to the next `### ` heading.

    Located by heading TEXT, never by line number: the section moves every time
    anything above it is edited, and a lint anchored to a line number is a lint
    that silently starts reading §5.3."""
    lines = body.splitlines()
    starts = [index for index, line in enumerate(lines)
              if line.startswith(SECTION_HEADING)]
    assert len(starts) == 1, (
        "PREREGISTRATION.md holds %d headings beginning %r, and §5.4 is located "
        "by that heading" % (len(starts), SECTION_HEADING))
    for index in range(starts[0] + 1, len(lines)):
        if lines[index].startswith("### "):
            return lines[starts[0]:index]
    return lines[starts[0]:]


def prose_blocks_5_4(body: str) -> list:
    """[(heading, that subsection's PROSE)] for §5.4 — every line of the section
    that is not a pipe-table row, split at its `#### ` headings.

    The tables are dropped and the headings are kept, because round 5 finding 5
    already pins the table LABELS and round 6 finding 4 is that the false names
    survived in the text AROUND them. A subsection is the unit because a
    restatement four screens from the coverage-side paragraph is exactly what
    the finding caught: `0.7359` named honestly under one heading and as the
    registered joint outcome under another."""
    lines = section_5_4(body)
    blocks, heading, prose = [], lines[0].strip(), []
    for line in lines[1:]:
        if line.startswith("#### "):
            blocks.append((heading, "\n".join(prose)))
            heading, prose = line.strip(), []
            continue
        if line.strip().startswith("|"):
            continue
        prose.append(line)
    blocks.append((heading, "\n".join(prose)))
    return blocks


def phrase_defects_5_4(body: str) -> list:
    """Every way §5.4's prose breaks round 6 finding 4's rule, as sentences; the
    empty list is the passing state.

    Separate from the tests below so that one of them can hold this walk to a
    body whose answer is known — a lint nobody has run on a planted defect is a
    claim that it fires, not a check that it does."""
    defects = []
    for heading, prose in prose_blocks_5_4(body):
        lowered = prose.lower()
        for phrase in BANNED_5_4_PHRASES:
            if phrase.lower() in lowered:
                defects.append(
                    "%s: the prose says %r. §5.4's own paragraph registers every "
                    "CONFIRMED-side figure as a coverage-side quantity — S5 is "
                    "outside the model — and this names it the confirmatory "
                    "outcome (round 6, finding 4)" % (heading, phrase))
        if CONFIRMED_FIGURE in prose and COVERAGE_SIDE not in lowered:
            defects.append(
                "%s: the prose discusses %s and never calls it %s. The figure is "
                "exact for the coverage pattern and an UPPER BOUND for CONFIRMED, "
                "and a restatement that drops the qualifier restates the wrong "
                "quantity (round 6, finding 4)"
                % (heading, CONFIRMED_FIGURE, COVERAGE_SIDE))
    return defects


def test_the_section_five_four_prose_calls_the_confirmed_figures_coverage_side(
        preregistration):
    """Round 6, finding 4. §5.4 correctly registers `0.7359`/`0.3536` as
    coverage-side upper bounds because S5 — arm E's labels at the ceiling — is
    unmodelled, and its sample-size prose nevertheless still called them the
    registered joint/CONFIRMED outcome. Round 5's test checked only the table
    LABELS, so the false names survived in the text beside them.

    This is the lint the disposition registers: the prose of every subsection of
    §5.4 that discusses the figure names it coverage-side, and none of the three
    withdrawn names appears anywhere in the section's prose."""
    defects = phrase_defects_5_4(preregistration)
    assert defects == [], "§5.4's prose:\n  " + "\n  ".join(defects)


def test_the_five_four_phrase_lint_fires_on_a_planted_name():
    """The known answer the lint is held to: a §5.4 carrying each withdrawn name
    and a coverage-side-free restatement of the figure, and a clean one built
    from the same parts.

    Without this the lint could pass by never reading anything — a heading
    matcher that finds no section, a table filter that eats the whole body — and
    the passing suite would say the prose is pinned when nothing is."""
    def body(prose: str) -> str:
        return ("## 5. Verdicts\n\n### 5.4 What N = 30 can and cannot resolve\n\n"
                "| registered rule | N = 30 |\n| --- | --- |\n"
                "| CONFIRMED and the gate hold — the actual joint | 0.7359 |\n\n"
                "#### Why 30\n\n" + prose + "\n\n### 5.5 What a verdict does not "
                "license\n\nnothing here is §5.4's.\n")
    # The table row carries a banned name and the figure: round 5's rule owns the
    # labels, this one owns the prose, and the two do not reach into each other.
    clean = body("N = 30 is the proposal, on the coverage-side CONFIRMED "
                 "quantity (0.7359 against 0.3536).")
    assert phrase_defects_5_4(clean) == []
    for phrase in BANNED_5_4_PHRASES:
        planted = body("N = 30 is the proposal, on %s (0.7359 against 0.3536), "
                       "and its coverage-side reading is registered above."
                       % phrase)
        defects = phrase_defects_5_4(planted)
        assert len(defects) == 1 and phrase in defects[0], (phrase, defects)
    unqualified = body("N = 30 is the proposal, on the control gate (0.7658 "
                       "against 0.4031) and the registered joint outcome (0.7359 "
                       "against 0.3536).")
    defects = phrase_defects_5_4(unqualified)
    assert len(defects) == 1 and CONFIRMED_FIGURE in defects[0], defects
    # …and the section really is bounded by its own two headings: §5.5's text is
    # not §5.4's prose, and §5.3's is not either.
    assert len(prose_blocks_5_4(clean)) == 2
    assert "5.5" not in "".join(prose for _heading, prose in prose_blocks_5_4(clean))


# --- §5.4's endpoint assumption, pinned (round 9, finding 9) -----------------

# Row 5 reads ONE arm-A HIGH pattern for a primary rule (the gate, row 2) and
# for an S1 rule (`nP`), which §5.4's own fourth independence layer says must
# be marked wherever it happens. The two phrases are the load-bearing halves of
# what makes that reading exact: the scenario's `p` goes to both endpoints, and
# `H(r) ⊆ A(r)` pathwise then leaves the two per-slot indicators equal.
REQUIRED_5_4_PHRASES = ("to both endpoints", "equal almost surely")
# The other extreme, which §5.4 now prints so the premise is visibly material:
# arm A's S1 HIGH pattern independent of its primary pattern.
ENDPOINT_INDEPENDENT_ROW5 = {20: 0.0210, 25: 0.3057, 30: 0.7116}


def endpoint_assumption_defects(body: str) -> list:
    """Every way §5.4's prose fails to say what identifies its two endpoints;
    the empty list is the passing state."""
    prose = "\n".join(text for _heading, text in prose_blocks_5_4(body))
    return ["§5.4's prose never says %r: the row-5 joint reads one arm-A "
            "pattern for a primary rule and an S1 rule, and that identity "
            "is an assumption of the scenario (round 9, finding 9)" % phrase
            for phrase in REQUIRED_5_4_PHRASES if phrase not in prose]


def test_the_section_five_four_prose_states_what_identifies_the_endpoints(
        preregistration):
    """Round 9, finding 9. Layer 4 promises that any figure combining the
    primary and S1 is marked; row 5 is the one, and the mark is the paragraph
    that says why reading one pattern twice is exact here."""
    defects = endpoint_assumption_defects(preregistration)
    assert defects == [], "§5.4's prose:\n  " + "\n  ".join(defects)


def test_the_endpoint_assumption_lint_fires_when_the_sentence_is_removed():
    """The known answer the lint is held to, as round 6's lint is."""
    def body(prose: str) -> str:
        return ("## 5. Verdicts\n\n### 5.4 What N = 30 can and cannot "
                "resolve\n\n" + prose + "\n\n### 5.5 What a verdict does "
                "not license\n\nnot §5.4's.\n")
    carried = body("The scenario assigns its p to both endpoints, and with "
                   "H(s) inside A(s) path by path the two per-slot "
                   "indicators are equal almost surely.")
    assert endpoint_assumption_defects(carried) == []
    stripped = body("The scenario says nothing about how its two endpoints "
                    "relate.")
    assert len(endpoint_assumption_defects(stripped)) \
        == len(REQUIRED_5_4_PHRASES)


@pytest.mark.parametrize("trials", TRIALS)
def test_the_endpoint_identity_is_what_makes_row_five_exact(
        trials, preregistration):
    """The alternative §5.4 now names, computed from the three quantities the
    same call already returns rather than transcribed: arm A's S1 HIGH pattern
    independent of its primary pattern makes row 5 strictly smaller, and §5.4
    prints the number this file computes."""
    characteristics = score_rates.decision_operating_characteristics(trials)
    alternative = (characteristics["gate"]
                   * (1 - characteristics["pLowIntact"])
                   * characteristics["marginal"]["nP"])
    assert round(alternative, 4) == ENDPOINT_INDEPENDENT_ROW5[trials]
    assert alternative < characteristics["joint"]["row5"]
    assert "%.4f" % alternative in "\n".join(section_5_4(preregistration))


# --- §5.4's zero note, against the arithmetic (round 9, finding 12) ----------

def test_the_section_five_four_zero_note_matches_the_arithmetic(preregistration):
    """Round 9, finding 12. The note under §5.4's marginal table claimed every
    0.0000 in the FILE was rounded — four of that table's own cells are exact —
    and gave a magnitude for P(HIGH | p = 0.30) that is not the one this file
    computes. Both halves are pinned to the code rather than to a transcription."""
    cells = level_cells(preregistration)
    assert {key for key, (_cell, value) in cells.items()
            if value == 0.0} == EXACT_ZERO_CELLS
    # …and the zero is the exact rational's, not a double that underflowed.
    high_k, low_k = score_rates.high_threshold(30), score_rates.low_threshold(30)
    assert score_rates.probability_at_least(high_k, 30, Fraction(0)) == Fraction(0)
    assert score_rates._tail_le(low_k, 30, Fraction(1)) == Fraction(0)
    prose = "\n".join(text for _heading, text in prose_blocks_5_4(preregistration))
    assert BANNED_ZERO_NOTE_FIGURE not in prose
    mantissa, exponent = ("%.1e" % float(score_rates.probability_at_least(
        high_k, 30, ZERO_NOTE_P))).split("e")
    figure = "%s × 10%s" % (mantissa, str(int(exponent)).translate(SUPERSCRIPT))
    assert figure in prose, "§5.4's zero note must give %s" % figure
