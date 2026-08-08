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
"""
from __future__ import annotations
import re

import pytest

import fixtures
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


def test_the_level_rule_applies_to_every_endpoint_it_is_registered_over():
    """§5.1: the rule applies unchanged to the primary ITT rate, to the S1
    raw-placement rate and to the per-protocol rate, and §4.6 S10 counts a
    fourth family of level verdicts under the same rule. Every level verdict
    names which of them it is a verdict on."""
    assert score_rates.LEVEL_ENDPOINTS == ("primary", "placement",
                                           "perProtocol", "oldEdge")


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
    "five of six" over arms B and C, and class 4 is the embargo-membership
    class whose collapse overrides every other reading of arm E."""
    assert score_rates.NARROW_NUMERIC_CLASSES == (0, 1, 2, 5)
    assert score_rates.EMBARGO_CLASS == 4
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
    # No accepted record is no evidence the author could apply the values, and
    # the conservative direction of an absent measurement does not confirm.
    assert silent["branch"] == "degraded" and silent["rate"] is None
    flat = " ".join(preregistration.split())
    assert "the one-step escalation at mislabel share ≥ 0.20" in flat
    assert score_rates.MISLABEL_ESCALATION not in (score_rates.S5_CEILING,)


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


def test_arm_ds_outcome_is_computed_from_the_registered_levels():
    """The four rows at known level verdicts, over the six classes: the
    predicted tracking, the old-edge preference, the general degradation, and
    the mixed case §5.3 (ii) names no outcome for."""
    tracking = [{"index": index, "contrast": "TRACKING"} for index in range(6)]
    indeterminate = [{"index": index,
                      "contrast": "TRACKING" if index in (3, 4)
                      else "INDETERMINATE"} for index in range(6)]
    high_six = ["HIGH"] * 6
    # New-keyed LOW on the four narrow numeric classes, HIGH on 3 and 4.
    new_low = ["LOW", "LOW", "LOW", "HIGH", "HIGH", "LOW"]
    old_high = ["HIGH", "HIGH", "HIGH", "HIGH", "HIGH", "HIGH"]
    old_low = ["LOW", "LOW", "LOW", "HIGH", "HIGH", "LOW"]
    assert score_rates.arm_d_outcome(high_six, old_low,
                                     tracking)["publishedAs"] \
        == "COVERAGE-FOLLOWS-THE-NUMBERS"
    preference = score_rates.arm_d_outcome(new_low, old_high, indeterminate)
    assert preference["publishedAs"] == "OLD-EDGE-PREFERENCE"
    assert preference["counts"] == {"newKeyedLow": 4, "oldKeyedHigh": 4,
                                    "oldKeyedLow": 0, "tracking": 2,
                                    "narrowMinimum": 3, "classes": 6}
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
    from fractions import Fraction
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
    for prefix, value in computed.items():
        matched = [rule for rule in registered if rule.startswith(prefix)]
        assert len(matched) == 1, (
            "§5.4 holds %d rules beginning %r" % (len(matched), prefix))
        printed = registered[matched[0]][trials]
        assert abs(value - printed) < 5e-5, (
            "§5.4 prints %s for %r at N = %d; this file computes %.6f"
            % (printed, matched[0], trials, value))


@pytest.mark.parametrize("trials", TRIALS)
def test_the_power_to_reach_row_four_is_not_the_marginal(trials):
    """Round 3, finding 11: §5.4 labels `0.7142 / 0.9187 / 0.9796` "the power to
    reach decision row 4", and they are the marginal `P(nH >= 3)`. Reaching row
    4 also requires that arm E does not collapse on class 4 (row 2) and that the
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
    # The joint figure IS the marginal times the gate, to within the class-4
    # term — arm E's class 4 sits at p = 0.95 in this scenario and reading LOW
    # there is a 1e-23 event, so the two agree to every place §5.4 prints and
    # the difference below is the double's own epsilon, not the term.
    assert characteristics["pLowIntact"] < 1e-20
    assert abs(joint - marginal * characteristics["gate"]) < 1e-12
    assert joint < marginal
    # …and the gate is what does it: at N = 20 the design's own precondition for
    # reading arm E holds one time in eighteen.
    assert round(characteristics["gate"], 4) == {20: 0.0557, 25: 0.4031,
                                                 30: 0.7658}[trials]


def test_the_joint_row_four_figures_are_checked_against_the_file_when_it_carries_them(
        preregistration):
    """The half of the previous test that binds the FILE.

    §5.4 does not carry the joint row yet — the amendment round 3's finding 11
    calls for is what adds it — so this asserts the mislabel is still the only
    thing to fix and, the moment a row beginning "row 4 reached" appears, that
    it carries the computed figures rather than a second transcription of them.
    """
    registered = operating_characteristics(preregistration)
    joint_rows = [rule for rule in registered if rule.startswith("row 4 reached")]
    assert len(joint_rows) <= 1
    for rule in joint_rows:
        for trials in TRIALS:
            computed = score_rates.decision_operating_characteristics(
                trials)["joint"]["row4"]
            assert abs(computed - registered[rule][trials]) < 5e-5, (
                "§5.4's joint row 4 prints %s at N = %d; this file computes %.7f"
                % (registered[rule][trials], trials, computed))
