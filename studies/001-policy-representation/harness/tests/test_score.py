"""Tests for the registered-analysis surface of ``score.py``.

WHAT THIS FILE DOES
-------------------
* Pins **McNemar's exact test** against tables whose p is computable by hand
  (symmetric, one-sided-degenerate, empty) and against the one number this study
  actually reports: the 44 / 12 discordant split of arm B against arm A on the
  answerable population, p = 2.0876568218419767e-05, which was computed
  independently from the retained logs before the implementation existed.
* Checks the ``--population`` filter: it selects on the instance document's
  ``variant`` field and nothing else, it is the identity for ``all``, and it
  raises rather than reporting on an empty analysis set.
* Checks the ``--bootstrap-unit`` clustering: ``pair`` draws the two twins of a
  base instance in or out together and thereby pins the variant mix of every
  replicate (the mechanism behind its measured effect on interval width),
  ``twin`` consumes randomness exactly as the shipped twin-level resample did
  (the guarantee that keeps already-published intervals reproducible) and remains
  the default, and on a single-variant population the two units produce identical
  draws and identical intervals from the same seed.
* Checks that escalation precision, recall and F1 are reported as **undefined**
  --- ``None`` in the summary, ``n/a`` in the markdown --- on any analysis set
  that populates only one row of the 2x2, and that the 2x2 counts survive that
  suppression.
* Scores a small synthetic corpus --- four base instances, both twins, two
  conditions, two trials --- whose pass^k, accuracy and McNemar counts are worked
  out in comments beside the fixture, and drives the same corpus through
  ``main()`` so the CLI flags are exercised, not just the function keywords.

WHAT THIS FILE DELIBERATELY DOES NOT DO
---------------------------------------
* No re-testing of the metric definitions --- accuracy, citation P/R/F1, the
  escalation 2x2, the redaction contract. ``test_harness.py`` owns those and this
  file would only duplicate their hand-computed fixtures.
* No assertion that any hypothesis passed or failed. A test that encoded a
  verdict would have to be edited when the data changed, which is the opposite of
  what a preregistered analysis is for.
* No network, no subprocess, no ``judgment-pack`` CLI, and no reading of the real
  ``results/`` corpus --- the study's own numbers are verified by re-running the
  scorer, not by a unit test that would freeze them.

Standard library plus pytest only.
"""

from __future__ import annotations

import json
import math
import os
import random
import sys
from fractions import Fraction

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
if HARNESS not in sys.path:
    sys.path.insert(0, HARNESS)

import run as run_mod  # noqa: E402
import score as score_mod  # noqa: E402

# The value the adversarial review computed by hand from the retained logs, for
# baseline A::codex::gpt-5.6-sol vs B::mock::judgment-pack-runtime at k = 5 on
# the answerable population. It is a fixed point of this file: the scorer is
# wrong if it moves.
REVIEW_P_44_12 = 2.0876568218419767e-05


# --------------------------------------------------------------------------- #
# Fixtures: four base instances, both twins, two conditions, two trials
# --------------------------------------------------------------------------- #


def _instance(base, variant):
    """One twin document, in the shape ``redact.py`` emits.

    Both twins of a pair share ``instance_id`` and ``pair_id`` and are told apart
    by ``twin_id`` and ``variant`` --- the identity contract ``score.py`` reads.
    """
    return {
        "instance_id": "p%d" % base,
        "pair_id": "p%d" % base,
        "twin_id": "p%d__%s" % (base, variant),
        "variant": variant,
        "facts": {"teams": {"A": {"salary": "1"}}},
        "gold": {"answer": True, "relevant_rules": ["R1"]},
        "redaction": {"applied": variant == "redacted",
                      "base_instance_id": "p%d" % base},
    }


def _corpus():
    docs = []
    for base in range(4):
        docs.append(_instance(base, "answerable"))
        docs.append(_instance(base, "redacted"))
    return docs


def _row(twin_id, trial, decision, *, arm="A", backend="mock", model="m",
         parse_ok=True, error=None):
    return {
        "schema": "jps-study-001-result/1",
        "instance_id": twin_id.split("__", 1)[0],
        "row_id": twin_id,
        "arm": arm, "backend": backend, "model": model,
        "params": {}, "trial": trial, "seed": 0,
        "prediction": None if not parse_ok else
        {"decision": decision, "cited_rules": ["R1"], "reason": ""},
        "raw_text": "", "parse_ok": parse_ok,
        "parse_error": None if parse_ok else "no-json-object",
        "latency_ms": 1, "error": error,
        "facts_sha256": "x", "prompt_sha256": "y",
        "harness_commit": "c", "harness_dirty": False, "arm_config": {},
    }


# Gold decision is "illegal" on an answerable twin and "cannot_decide" on a
# redacted one. The two conditions are laid out so every number below is
# countable by eye:
#
#   arm A   answerable p0,p1,p2: illegal,  illegal   -> all_correct
#           answerable p3:       illegal,  legal     -> half right
#           redacted   p0..p3:   illegal,  legal     -> never right, never escalates
#   arm B   answerable p0..p3:   illegal,  cannot_decide  -> half right (false escalation)
#           redacted   p0..p3:   cannot_decide, cannot_decide -> all_correct
#
# answerable population (4 instances, k = 2):
#   pass^k  A = 3/4 = 0.75 ; B = 0/4 = 0.0
#   accuracy A = (1 + 1 + 1 + .5)/4 = 0.875 ; B = 0.5
#   McNemar A-vs-B: baseline-only correct = p0,p1,p2 = 3 ; condition-only = 0
#           -> n = 3, p = 2 * C(3,0)/2^3 = 0.25
# all population (8 instances):
#   pass^k  A = 3/8 = 0.375 ; B = 4/8 = 0.5
#   McNemar: baseline-only = 3 (the answerable ones), condition-only = 4 (the
#            redacted ones) -> n = 7, min = 3, tail = 64/128 -> p = 1.0


def _rows():
    rows = []
    for base in range(4):
        ans = "p%d__answerable" % base
        red = "p%d__redacted" % base
        a_second = "illegal" if base < 3 else "legal"
        rows.append(_row(ans, 1, "illegal"))
        rows.append(_row(ans, 2, a_second))
        rows.append(_row(red, 1, "illegal"))
        rows.append(_row(red, 2, "legal"))
        for trial, decision in ((1, "illegal"), (2, "cannot_decide")):
            rows.append(_row(ans, trial, decision, arm="B", model="jp"))
        for trial in (1, 2):
            rows.append(_row(red, trial, "cannot_decide", arm="B", model="jp"))
    return rows


@pytest.fixture()
def corpus(tmp_path):
    """Write the synthetic corpus to disk and return (instance_dir, results)."""
    inst_dir = tmp_path / "inst"
    inst_dir.mkdir()
    for doc in _corpus():
        (inst_dir / (doc["twin_id"] + ".json")).write_text(
            json.dumps(doc), encoding="utf-8")
    results = tmp_path / "res.jsonl"
    results.write_text("\n".join(json.dumps(r) for r in _rows()) + "\n",
                       encoding="utf-8")
    return str(inst_dir), str(results)


def _score(corpus, **kwargs):
    inst_dir, results_path = corpus
    instances = run_mod.load_instances(inst_dir)
    results = score_mod.load_results([results_path])
    kwargs.setdefault("bootstrap", 40)
    kwargs.setdefault("seed", 20260806)
    kwargs.setdefault("baseline", "A::mock::m")
    return score_mod.score(instances, results, **kwargs)


# --------------------------------------------------------------------------- #
# McNemar's exact test
# --------------------------------------------------------------------------- #


def test_mcnemar_zero_discordant_is_one():
    """No instance separates the conditions: no evidence, p = 1.0 exactly."""
    assert score_mod.mcnemar_exact_p(0, 0) == 1.0


@pytest.mark.parametrize("b", [1, 3, 7, 22, 100])
def test_mcnemar_symmetric_tables_are_one(b):
    """b == c is the null itself; the two-sided p is capped at 1.0, never above."""
    p = score_mod.mcnemar_exact_p(b, b)
    assert p == 1.0


@pytest.mark.parametrize("b,c,expected", [
    (1, 0, 1.0),                  # 2 * P(X <= 0) with n = 1  -> 2 * 1/2
    (5, 0, 2 * 1 / 32.0),         # 2 * C(5,0)/2^5
    (3, 0, 2 * 1 / 8.0),          # the value the synthetic fixture below reports
    (10, 0, 2 * 1 / 1024.0),
    (4, 1, 2 * (1 + 5) / 32.0),   # n = 5, min = 1
    (12, 3, 2 * (1 + 15 + 105 + 455) / 32768.0),
])
def test_mcnemar_small_tables_match_hand_computation(b, c, expected):
    assert score_mod.mcnemar_exact_p(b, c) == pytest.approx(expected, rel=1e-12)


def test_mcnemar_is_symmetric_in_its_arguments():
    """Which condition happens to be the baseline cannot change a two-sided p."""
    for b, c in ((44, 12), (0, 9), (5, 6), (31, 17)):
        assert score_mod.mcnemar_exact_p(b, c) == score_mod.mcnemar_exact_p(c, b)


def test_mcnemar_matches_the_reviewed_44_12_split():
    """The one number this study reports: B vs A, answerable, k = 5."""
    p = score_mod.mcnemar_exact_p(44, 12)
    assert p == pytest.approx(REVIEW_P_44_12, rel=1e-8)
    assert "%.3e" % p == "2.088e-05"


def test_mcnemar_never_exceeds_one_and_is_exact():
    """Cross-check against an independent exact evaluation over many tables."""
    for b in range(0, 25):
        for c in range(0, 25):
            n = b + c
            if n == 0:
                expected = 1.0
            else:
                tail = Fraction(sum(math.comb(n, i) for i in range(min(b, c) + 1)),
                                1 << n)
                expected = float(min(Fraction(1), 2 * tail))
            got = score_mod.mcnemar_exact_p(b, c)
            assert 0.0 <= got <= 1.0
            assert got == pytest.approx(expected, rel=1e-12)


def test_mcnemar_rejects_negative_counts():
    with pytest.raises(ValueError):
        score_mod.mcnemar_exact_p(-1, 3)


def test_mcnemar_counts_only_discordant_instances(corpus):
    """Concordant instances must not reach the test, on either population."""
    summary = _score(corpus, population="answerable")
    m = summary["conditions"]["B::mock::jp"]["mcnemar_pass_at_k"]
    assert m["n_baseline_only_correct"] == 3
    assert m["n_condition_only_correct"] == 0
    assert m["n_discordant"] == 3
    assert m["p_value"] == pytest.approx(0.25)

    # The same two conditions over both twins: the redacted instances flip four
    # cells into the other cell, and the test stops separating them.
    everything = _score(corpus, population="all")
    m_all = everything["conditions"]["B::mock::jp"]["mcnemar_pass_at_k"]
    assert (m_all["n_baseline_only_correct"], m_all["n_condition_only_correct"],
            m_all["n_discordant"]) == (3, 4, 7)
    assert m_all["p_value"] == 1.0


def test_baseline_condition_carries_no_mcnemar_entry(corpus):
    summary = _score(corpus, population="answerable")
    assert "mcnemar_pass_at_k" not in summary["conditions"]["A::mock::m"]
    assert "mcnemar_pass_at_k" in summary["conditions"]["B::mock::jp"]


def test_mcnemar_reaches_the_markdown(corpus):
    markdown = score_mod.render_markdown(_score(corpus, population="answerable"))
    assert "McNemar's exact test on the pass^k indicator" in markdown
    assert "| `B::mock::jp` | 3 | 0 | 3 | 0.2500 |" in markdown


# --------------------------------------------------------------------------- #
# Analysis population
# --------------------------------------------------------------------------- #


def test_population_all_is_the_identity():
    by_id = {score_mod.instance_key(d): d for d in _corpus()}
    ids = sorted(by_id)
    assert score_mod.filter_population(ids, by_id, "all") == ids


def test_population_selects_only_the_matching_variant():
    by_id = {score_mod.instance_key(d): d for d in _corpus()}
    ids = sorted(by_id)
    answerable = score_mod.filter_population(ids, by_id, "answerable")
    redacted = score_mod.filter_population(ids, by_id, "redacted")
    assert answerable == ["p0__answerable", "p1__answerable",
                          "p2__answerable", "p3__answerable"]
    assert redacted == ["p0__redacted", "p1__redacted",
                        "p2__redacted", "p3__redacted"]
    assert set(answerable).isdisjoint(redacted)
    assert sorted(answerable + redacted) == ids
    assert all(by_id[i]["variant"] == "answerable" for i in answerable)
    assert all(by_id[i]["variant"] == "redacted" for i in redacted)


def test_population_raises_on_an_empty_selection():
    """Documents with no ``variant`` are not guessed at; the filter refuses."""
    docs = [{"instance_id": "x1", "twin_id": "x1", "facts": {}},
            {"instance_id": "x2", "twin_id": "x2", "facts": {}}]
    by_id = {score_mod.instance_key(d): d for d in docs}
    with pytest.raises(ValueError) as exc:
        score_mod.filter_population(sorted(by_id), by_id, "answerable")
    assert "variant" in str(exc.value)


def test_population_rejects_an_unknown_name():
    by_id = {score_mod.instance_key(d): d for d in _corpus()}
    with pytest.raises(ValueError):
        score_mod.filter_population(sorted(by_id), by_id, "eligible")


def test_population_is_applied_after_the_intersection_and_recorded(corpus):
    summary = _score(corpus, population="answerable")
    assert summary["population"] == "answerable"
    assert summary["paired_instances"] == 4
    assert summary["redacted_instances"] == 0
    assert summary["instance_ids"] == ["p0__answerable", "p1__answerable",
                                       "p2__answerable", "p3__answerable"]
    point = summary["conditions"]["A::mock::m"]["point"]
    assert point["pass_at_k"] == pytest.approx(0.75)
    assert point["accuracy"] == pytest.approx(0.875)
    assert summary["conditions"]["B::mock::jp"]["point"]["pass_at_k"] == 0.0

    header = score_mod.render_markdown(summary).splitlines()[2]
    assert "Analysis population: `answerable`" in header


def test_population_defaults_to_all_and_changes_the_endpoint(corpus):
    summary = _score(corpus)
    assert summary["population"] == "all"
    assert summary["paired_instances"] == 8
    assert summary["redacted_instances"] == 4
    # The endpoint the composite reports is not the endpoint the registered
    # population reports --- the whole point of DEVIATIONS.md section 2.
    assert summary["conditions"]["A::mock::m"]["point"]["pass_at_k"] == pytest.approx(0.375)
    assert summary["conditions"]["B::mock::jp"]["point"]["pass_at_k"] == pytest.approx(0.5)


# --------------------------------------------------------------------------- #
# Bootstrap unit
# --------------------------------------------------------------------------- #


def test_pair_clusters_group_the_two_twins_of_a_base_instance():
    by_id = {score_mod.instance_key(d): d for d in _corpus()}
    ids = sorted(by_id)
    clusters = score_mod.bootstrap_clusters(ids, by_id, "pair")
    assert clusters == [["p0__answerable", "p0__redacted"],
                        ["p1__answerable", "p1__redacted"],
                        ["p2__answerable", "p2__redacted"],
                        ["p3__answerable", "p3__redacted"]]


def test_twin_clusters_are_singletons_in_input_order():
    by_id = {score_mod.instance_key(d): d for d in _corpus()}
    ids = sorted(by_id)
    assert score_mod.bootstrap_clusters(ids, by_id, "twin") == [[i] for i in ids]


def test_bootstrap_unit_rejects_an_unknown_name():
    by_id = {score_mod.instance_key(d): d for d in _corpus()}
    with pytest.raises(ValueError):
        score_mod.bootstrap_clusters(sorted(by_id), by_id, "instance")


def test_pair_resampling_never_splits_a_pair():
    """A drawn pair contributes both twins; a dropped pair contributes neither."""
    by_id = {score_mod.instance_key(d): d for d in _corpus()}
    ids = sorted(by_id)
    clusters = score_mod.bootstrap_clusters(ids, by_id, "pair")
    rng = random.Random(20260806)
    for _ in range(200):
        draw = score_mod.resample_clusters(clusters, rng)
        assert len(draw) == 8  # 4 clusters drawn, 2 members each
        for base in range(4):
            assert (draw.count("p%d__answerable" % base)
                    == draw.count("p%d__redacted" % base))


def test_pair_resampling_pins_the_variant_mix_and_twin_does_not():
    """The mechanism behind clustering's measured effect on interval width.

    Because every cluster is one answerable twin plus its redacted counterpart,
    a clustered replicate is 50/50 by construction and carries no
    mixture-composition variance at all; an unclustered replicate does. That is
    why ``pair`` *narrows* the composite-population intervals on this study's
    corpus rather than widening them, and the module docstring says so; this test
    is the part of that claim a fixture can hold.
    """
    by_id = {score_mod.instance_key(d): d for d in _corpus()}
    ids = sorted(by_id)

    def mixes(unit, seed):
        clusters = score_mod.bootstrap_clusters(ids, by_id, unit)
        rng = random.Random(seed)
        return [sum(1 for i in score_mod.resample_clusters(clusters, rng)
                    if by_id[i]["variant"] == "answerable")
                for _ in range(200)]

    assert set(mixes("pair", 20260806)) == {4}
    assert len(set(mixes("twin", 20260806))) > 1


def test_twin_resampling_consumes_randomness_like_the_shipped_scorer():
    """The back-compat guarantee, asserted at the point where it could break.

    ``--bootstrap-unit twin`` must draw exactly what ``[paired[rng.randrange(n)]
    for _ in range(n)]`` drew, or every already-published interval silently moves.
    """
    by_id = {score_mod.instance_key(d): d for d in _corpus()}
    ids = sorted(by_id)
    clusters = score_mod.bootstrap_clusters(ids, by_id, "twin")

    new_rng = random.Random(4321)
    legacy_rng = random.Random(4321)
    n = len(ids)
    for _ in range(50):
        got = score_mod.resample_clusters(clusters, new_rng)
        legacy = [ids[legacy_rng.randrange(n)] for _ in range(n)]
        assert got == legacy


def test_pair_and_twin_coincide_on_a_single_variant_population(corpus):
    """Every cluster is a singleton there, so the units cannot differ."""
    by_id = {score_mod.instance_key(d): d for d in _corpus()}
    ids = score_mod.filter_population(sorted(by_id), by_id, "answerable")
    pair = score_mod.bootstrap_clusters(ids, by_id, "pair")
    twin = score_mod.bootstrap_clusters(ids, by_id, "twin")
    assert pair == twin

    rng_a, rng_b = random.Random(99), random.Random(99)
    for _ in range(25):
        assert (score_mod.resample_clusters(pair, rng_a)
                == score_mod.resample_clusters(twin, rng_b))

    by_pair = _score(corpus, population="answerable", bootstrap_unit="pair")
    by_twin = _score(corpus, population="answerable", bootstrap_unit="twin")
    assert by_pair["bootstrap_clusters"] == by_twin["bootstrap_clusters"] == 4
    del by_pair["bootstrap_unit"], by_twin["bootstrap_unit"]
    assert json.dumps(by_pair, sort_keys=True) == json.dumps(by_twin, sort_keys=True)


def test_the_default_bootstrap_unit_is_twin(corpus):
    """The published intervals were computed twin-level; the default keeps them.

    Flipping this default would restate every previously published composite
    interval with no flag, no warning and no note in any recorded command --- a
    worse defect than the one the option answers, and one no verdict in
    RESULTS-FIRST-PROMPT-ARMS.md would have flagged.
    """
    assert score_mod.build_parser().parse_args(
        ["--instances", "x", "--results", "y"]).bootstrap_unit == "twin"
    default = _score(corpus)
    assert default["bootstrap_unit"] == "twin"
    explicit = _score(corpus, bootstrap_unit="twin")
    assert json.dumps(default, sort_keys=True) == json.dumps(explicit, sort_keys=True)


def test_bootstrap_unit_is_recorded_and_changes_the_cluster_count(corpus):
    by_pair = _score(corpus, bootstrap_unit="pair")
    by_twin = _score(corpus, bootstrap_unit="twin")
    assert by_pair["bootstrap_unit"] == "pair"
    assert by_pair["bootstrap_clusters"] == 4
    assert by_twin["bootstrap_unit"] == "twin"
    assert by_twin["bootstrap_clusters"] == 8
    # Point estimates are not resampled, so they must be untouched by the unit.
    assert (by_pair["conditions"]["B::mock::jp"]["point"]
            == by_twin["conditions"]["B::mock::jp"]["point"])
    header = score_mod.render_markdown(by_pair).splitlines()[2]
    assert "resamples of 4 `pair` clusters" in header


# --------------------------------------------------------------------------- #
# Escalation metrics on a population that cannot estimate them
#
# The 2x2 needs both of its rows. A single-variant analysis set has one, and the
# 0.0 that `aggregate` returns for an empty denominator would then be published
# as "escalation F1 0.000, 95% CI [0.000, 0.000]" --- a measured-looking null on
# the quantity PREREGISTRATION.md section 6 makes H2's criterion. These tests
# hold the suppression, and hold that the counts survive it.
# --------------------------------------------------------------------------- #


def test_escalation_is_estimable_only_when_both_rows_are_populated():
    by_id = {score_mod.instance_key(d): d for d in _corpus()}
    ids = sorted(by_id)
    assert score_mod.escalation_is_estimable(ids, by_id)
    assert not score_mod.escalation_is_estimable(
        [i for i in ids if by_id[i]["variant"] == "answerable"], by_id)
    assert not score_mod.escalation_is_estimable(
        [i for i in ids if by_id[i]["variant"] == "redacted"], by_id)
    # A property of the instance set, not of --population: an intersection that
    # happens to hold one variant is just as unable to estimate the 2x2.
    assert not score_mod.escalation_is_estimable(["p0__answerable"], by_id)
    assert score_mod.escalation_is_estimable(
        ["p0__answerable", "p0__redacted"], by_id)


@pytest.mark.parametrize("population", ["answerable", "redacted"])
def test_single_variant_population_reports_escalation_as_undefined(corpus, population):
    summary = _score(corpus, population=population)
    assert summary["escalation_estimable"] is False
    for cond, entry in summary["conditions"].items():
        for metric in score_mod.ESCALATION_RATE_METRICS:
            assert entry["point"][metric] is None, (cond, metric)
            assert entry["ci95"][metric] is None, (cond, metric)
            assert entry["delta_vs_baseline"][metric] is None, (cond, metric)
        # Everything else is untouched: only the three ratios were undefined.
        assert entry["point"]["pass_at_k"] is not None
        assert entry["delta_vs_baseline"]["accuracy"]["ci95"] is not None


def test_the_escalation_counts_survive_the_suppression(corpus):
    """The false-escalation count is section 6's cost criterion and must stay.

    Arm B answers ``cannot_decide`` on one of its two trials on every answerable
    twin: 4 instances x 1 trial = 4 escalations that should not have happened,
    against arm A's none.
    """
    summary = _score(corpus, population="answerable")
    tables = {c: e["escalation_2x2"] for c, e in summary["conditions"].items()}
    assert tables["B::mock::jp"] == {"should_and_did": 0, "should_not_but_did": 4,
                                     "should_but_did_not": 0, "neither": 4}
    assert tables["A::mock::m"]["should_not_but_did"] == 0


def test_composite_population_still_reports_escalation_numbers(corpus):
    summary = _score(corpus, population="all")
    assert summary["escalation_estimable"] is True
    point = summary["conditions"]["B::mock::jp"]["point"]
    # B escalates on every redacted trial (8 TP) and on half the answerable ones
    # (4 FP), missing none: precision 8/12, recall 1.0.
    assert point["escalation_precision"] == pytest.approx(8 / 12.0)
    assert point["escalation_recall"] == pytest.approx(1.0)
    assert point["escalation_f1"] == pytest.approx(
        2 * (8 / 12.0) / ((8 / 12.0) + 1.0))
    assert summary["conditions"]["B::mock::jp"][
        "delta_vs_baseline"]["escalation_f1"]["ci95"] is not None


def test_undefined_escalation_prints_n_a_and_never_a_zero(corpus):
    markdown = score_mod.render_markdown(_score(corpus, population="answerable"))
    heading = "## Escalation on redacted twins (full 2x2)"
    assert heading + " -- NOT ESTIMABLE on this analysis set" in markdown
    assert "no redacted (should-escalate) instance" in markdown

    section = markdown.split(heading, 1)[1].split("## Paired differences", 1)[0]
    # The counts are there; the three ratios and the interval are not numbers.
    assert "| `B::mock::jp` | 0 | 4 | 0 | 4 | n/a | n/a | n/a | n/a |" in section
    rows = [line for line in section.splitlines() if line.startswith("| `")]
    assert len(rows) == 2
    assert all("0.000" not in row for row in rows)

    deltas = markdown.split("## Paired differences", 1)[1].split("## McNemar", 1)[0]
    # The escalation F1 difference is the last (point, interval) pair in the row.
    assert deltas.rstrip().splitlines()[-1].endswith("| n/a | n/a |")


def test_estimable_escalation_keeps_its_heading_and_numbers(corpus):
    markdown = score_mod.render_markdown(_score(corpus, population="all"))
    assert "## Escalation on redacted twins (full 2x2)\n" in markdown
    assert "NOT ESTIMABLE" not in markdown
    assert "always-escalate agent" in markdown


# --------------------------------------------------------------------------- #
# End to end
# --------------------------------------------------------------------------- #


def test_scoring_the_synthetic_corpus_is_deterministic(corpus):
    first = _score(corpus, population="answerable", bootstrap=64)
    second = _score(corpus, population="answerable", bootstrap=64)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["schema"] == "jps-study-001-score/2"


def test_cli_carries_the_flags_into_the_summary(corpus, tmp_path, capsys):
    inst_dir, results_path = corpus
    out_json = tmp_path / "summary.json"
    rc = score_mod.main([
        "--instances", inst_dir,
        "--results", results_path,
        "--baseline", "A::mock::m",
        "--population", "answerable",
        "--bootstrap-unit", "pair",
        "--bootstrap", "32",
        "--seed", "20260806",
        "--out-json", str(out_json),
    ])
    assert rc == 0
    summary = json.loads(out_json.read_text(encoding="utf-8"))
    assert summary["schema"] == "jps-study-001-score/2"
    assert summary["population"] == "answerable"
    assert summary["bootstrap_unit"] == "pair"
    assert summary["bootstrap_clusters"] == 4
    assert summary["paired_instances"] == 4
    m = summary["conditions"]["B::mock::jp"]["mcnemar_pass_at_k"]
    assert (m["n_baseline_only_correct"], m["n_condition_only_correct"],
            m["n_discordant"]) == (3, 0, 3)
    assert m["p_value"] == pytest.approx(0.25)
    assert "Analysis population: `answerable`" in capsys.readouterr().out


def test_cli_defaults_are_all_and_twin(corpus, tmp_path):
    """Both defaults are the shipped behaviour, so an old command still means it."""
    inst_dir, results_path = corpus
    out_json = tmp_path / "default.json"
    assert score_mod.main([
        "--instances", inst_dir,
        "--results", results_path,
        "--bootstrap", "8",
        "--out-json", str(out_json),
    ]) == 0
    summary = json.loads(out_json.read_text(encoding="utf-8"))
    assert summary["population"] == "all"
    assert summary["bootstrap_unit"] == "twin"
    assert summary["bootstrap_clusters"] == 8
    assert summary["paired_instances"] == 8
