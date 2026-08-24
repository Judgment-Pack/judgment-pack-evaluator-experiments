"""E5 — the ported census machinery, and the stimulus it does not have.

The machinery is Study 012's and is tested here on synthetic vectors, so the
freeze needs a registered census grid and not a build. The stimulus refusal is
tested too, because section 9's "no tradeoff statement combining them is
licensed" is exactly the claim a census quietly run on the gold grid would
manufacture.
"""
import collections
import json
import os

import pytest

from e4lib import census


# --- the carried renderers --------------------------------------------------

def test_token_writes_booleans_the_way_the_census_writes_them():
    assert census._token(True) == "true"
    assert census._token(False) == "false"
    assert census._token("approve") == "approve"
    assert census._token(40) == "40"


def test_show_signature_renders_a_multiset_with_its_counts():
    multiset = ((("approve",), 3), (("review",), 1))
    assert census.show_signature(multiset) == "(approve) x3, (review) x1"
    assert census.show_signature(()) == "none"


def test_show_multiset_sorts_by_the_rendering_not_by_a_number():
    """The one recorded behaviour change from Study 012: its values were risk
    scores and it sorted by `Decimal(value)`. A numeric sort over `approve`
    would raise."""
    counter = collections.Counter({"review": 2, "approve": 5})
    assert census.show_multiset(counter) == "approve x5, review x2"
    assert census.show_multiset(collections.Counter()) == "none"


def test_cover_greedily_is_an_upper_bound_that_is_exact_when_it_saturates():
    covering = {"a": {1, 2}, "b": {2, 3}, "c": {4}}
    assert census.cover_greedily(covering) == 3
    assert census.cover_greedily({"a": {1, 2, 3}, "b": {1}}) == 1
    assert census.cover_greedily({}) == 0


def test_cover_greedily_is_deterministic_under_ties():
    """The tie-break is on the sorted probe key, so the count is reproducible
    rather than dict-order-dependent."""
    covering = {"b": {1, 2}, "a": {3, 4}}
    assert census.cover_greedily(covering) == census.cover_greedily(
        {"a": {3, 4}, "b": {1, 2}}) == 2


# --- the two registered rows ------------------------------------------------

def test_the_encoding_key_is_a_multiset_not_a_sequence():
    """Two runs that answered the same stimulus the same way in a different
    internal order are ONE encoding: the census asks how many distinct readings
    the arm produced, and an ordering is not a reading."""
    assert census.encoding_key(["a", "b", "a"]) == census.encoding_key(
        ["a", "a", "b"])
    assert census.encoding_key(["a", "b"]) != census.encoding_key(["a", "a"])


def test_the_encoding_key_reads_structured_answers():
    key = census.encoding_key([("unresolved", ("no-match",))])
    assert isinstance(key, tuple)
    assert census.encoding_key([("unresolved", ("no-match",))]) == key


def test_signature_groups_orders_by_run_count_then_by_rendering():
    per_run = {"run-001": ["a"], "run-002": ["a"], "run-003": ["b"]}
    groups = census.signature_groups(per_run)
    assert [group["runs"] for group in groups] == [2, 1]
    assert groups[0]["runIds"] == ["run-001", "run-002"]


def test_pairwise_disagreement_publishes_the_distribution_not_a_mean():
    """A mean cannot distinguish one outlier from a uniform spread, and the
    spread is what the census is about."""
    per_run = {"r1": ["a", "a"], "r2": ["a", "a"], "r3": ["b", "b"]}
    spread = census.pairwise_disagreement(per_run)
    assert spread["pairs"] == 3
    assert spread["distribution"] == {"0": 1, "2": 2}
    assert spread["identicalPairs"] == 1
    assert spread["maxDisagreements"] == 2


def test_ragged_vectors_refuse_rather_than_comparing_two_questions():
    with pytest.raises(census.CensusError) as raised:
        census.pairwise_disagreement({"r1": ["a"], "r2": ["a", "b"]})
    assert str(raised.value).startswith("E5-RAGGED-VECTORS")


def test_the_census_carries_the_stimulus_label_into_every_record():
    """Section 9 makes "which stimulus" the load-bearing fact about every census
    number, so it is in the record and not in a caller's memory."""
    result = census.census("A", {"run-001": ["a"], "run-002": ["b"]},
                           "synthetic-grid")
    assert result["stimulus"] == "synthetic-grid"
    assert result["arm"] == "A"
    assert result["distinctEncodings"] == 2
    assert result["minimalCoveringSet"] == 2
    assert result["pairwiseDisagreement"]["pairs"] == 1


def test_an_empty_arm_censuses_to_zero_rather_than_raising():
    result = census.census("B", {}, "synthetic-grid")
    assert result["runs"] == 0 and result["distinctEncodings"] == 0
    assert result["pairwiseDisagreement"] is None


def test_the_rendered_table_is_deterministic():
    per_arm = [census.census("A", {"run-001": ["a"], "run-002": ["a"]}, "grid")]
    assert census.render_markdown(per_arm) == census.render_markdown(per_arm)
    assert "Descriptive" in census.render_markdown(per_arm)


# --- the registered stimulus (SCAFFOLD item S6) -----------------------------

def test_the_registered_stimulus_is_the_gold_row_input_set(preregistration):
    """SCAFFOLD item S6, closed. Section 5 registers the census stimulus and the
    module reads it rather than refusing — as IDS and ORDER only, because a gold
    row's expectation is an oracle and the census is not scored against one."""
    flat = " ".join(preregistration.split())
    # 020's §5.1 states the same stimulus in its own words AND adds the
    # obligation Study 019 stated nowhere: the count is freeze-pinned.
    assert ("**E5: interpretive-spread census** — per-arm distinct structural "
            "encodings and pairwise- disagreement profiles over the frozen "
            "gold-row input set, the count freeze-pinned in `PINS.json`") in flat
    rows = [{"id": "r-%02d" % index, "expect": {"disposition": "approve"}}
            for index in range(105)]
    stimulus = census.registered_stimulus(rows, "sha256:" + "a" * 64)
    assert stimulus["count"] == 105
    assert stimulus["points"] == [row["id"] for row in rows]
    assert stimulus["goldSha256"] == "sha256:" + "a" * 64
    assert stimulus["label"] == census.stimulus_label(105)


def test_the_registered_count_is_a_freeze_pin(pins):
    """§5.1's E5 registers the census count as freeze-pinned and Study 019
    pinned no count at all — which is how a published census table came to name
    a row count its own data did not have, twice. The pin is null until the gold
    suite lands, and `study_label()` reads it, so a REGISTERED attempt is
    unreachable while it is."""
    import integrity
    assert ("censusStimulusCount", ("censusStimulus", "count")) in \
        integrity.FREEZE_PINS
    assert pins["censusStimulus"]["path"] == "gold/GOLD.json"
    if pins["censusStimulus"]["count"] is None:
        assert "censusStimulusCount" in integrity.unfilled_pins(pins)


def test_the_stimulus_label_is_derived_from_the_suite_it_was_read_over(
        study, requires_artifact):
    requires_artifact("design/gold/gold.json")
    """ROUND-1 R1-19's enforcing test. The label was the constant string
    "the gold-row input set (105 gold inputs)" while the committed suite had
    grown past 105, so a published census table would have named a count its own
    data does not have. The label is computed from the stimulus now, and this
    drives it at the COMMITTED suite's real size rather than at a literal."""
    with open(os.path.join(study, "design/gold/gold.json"), "rb") as handle:
        gold = json.loads(handle.read().decode("utf-8"))
    rows = gold["rows"]
    stimulus = census.registered_stimulus(rows)
    assert stimulus["count"] == len(rows)
    assert stimulus["label"] == "the gold-row input set (%d gold inputs)" % len(rows)
    # and the label moves with the suite rather than with an edit here
    assert census.stimulus_label(len(rows) + 1) != stimulus["label"]


def test_the_stimulus_carries_section_nines_reading_with_it(preregistration):
    """Section 9 is unchanged and still governs: the census's rows and the E4
    kill rates live on different stimuli, and the label travels inside the
    record so a reader of one table cannot lose it."""
    flat = " ".join(preregistration.split())
    assert "no tradeoff statement combining them is licensed" in flat
    stimulus = census.registered_stimulus([{"id": "r-01"}])
    assert "no tradeoff statement" in stimulus["note"]
    record = census.census("A", {"run-001": ["approve"]}, stimulus["label"])
    assert record["stimulus"] == census.stimulus_label(1)


def test_an_empty_or_duplicated_stimulus_refuses_by_name():
    """The two ways a suite handed to the census is not a stimulus: no cells at
    all, and two different cells that would become one census point."""
    with pytest.raises(census.CensusError) as raised:
        census.registered_stimulus([])
    assert str(raised.value).startswith("E5-STIMULUS-EMPTY")
    with pytest.raises(census.CensusError) as raised:
        census.registered_stimulus([{"id": "r-01"}, {"id": "r-01"}])
    assert str(raised.value).startswith("E5-STIMULUS-DUPLICATE-CELLS")
