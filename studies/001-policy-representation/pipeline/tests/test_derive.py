#!/usr/bin/env python3
"""Tests for derive.py.

Two layers:

* unit tests over hand-built facts documents, which pin the arithmetic and the
  presence discipline without depending on ``out/facts`` existing;
* contract tests that assert every field the pack reads is either emitted or
  deliberately omitted, and that the emitted values obey the JPS decimal grammar.

Run: python -m pytest pipeline/tests/test_derive.py
"""

from __future__ import annotations

import json
import re
import sys
from decimal import Decimal
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent
STUDY = PIPELINE.parent
sys.path.insert(0, str(PIPELINE))

import derive  # noqa: E402

DEC_RE = re.compile(r"-?(0|[1-9][0-9]*)(\.[0-9]+)?\Z")


# --------------------------------------------------------------------------- #
# builders
# --------------------------------------------------------------------------- #
def doc(teams=None, players=None, operations=None, instance_id="test#000"):
    return {
        "contract_version": "facts/v1",
        "instance_id": instance_id,
        "facts": {
            "teams": teams or {},
            "players": players or {},
            "operations": operations or [],
            "derived": {},
        },
        "gold": {"answer": False, "relevant_rules": []},
        "provenance": {"source": "test"},
    }


def contract(years="4", first="20000000", pct="5", direction="increase",
             applies="all_years", kind="explicit", **extra):
    c = {"years": years, "salary_kind": kind, "annual_change_pct": pct,
         "annual_change_direction": direction, "annual_change_applies_to": applies}
    if kind == "explicit":
        c["first_year_salary"] = first
    c.update(extra)
    return c


def player(draft_year="2016", age="19", team="A", signed=2020, years="4",
           first="20000000", kind="explicit", awards=None, **extra):
    p = {
        "draft": {"year": draft_year, "age_at_draft": age, "round": "1",
                  "pick": "3", "team": team},
        "contract": contract(years=years, first=first, kind=kind),
    }
    p["contract"]["signed_with_team"] = team
    p["contract"]["signed_during"] = {"kind": "moratorium_period", "year": str(signed)}
    if awards:
        p["awards"] = awards
    p.update(extra)
    return p


# --------------------------------------------------------------------------- #
# 1. decimal rendering
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("value,expected", [
    (Decimal("1"), "1"),
    (Decimal("1.500"), "1.5"),
    (Decimal("0"), "0"),
    (Decimal("-0.0"), "0"),
    (Decimal("-250000"), "-250000"),
    (Decimal("140588000"), "140588000"),
])
def test_dec_str_shapes(value, expected):
    assert derive.dec_str(value) == expected


def test_dec_str_always_matches_jps_grammar():
    for v in ["0.000000000001", "1e-30", "123456789012345678", "-7.5", "1E+9"]:
        assert DEC_RE.match(derive.dec_str(Decimal(v))), v


def test_dec_str_never_uses_exponent_notation():
    assert "E" not in derive.dec_str(Decimal("1e20"))
    assert "e" not in derive.dec_str(Decimal("1e-20"))


# --------------------------------------------------------------------------- #
# 2. constants are the ones the benchmark stipulates
# --------------------------------------------------------------------------- #
def test_benchmark_constants_match_rulearena_prompt():
    src = (STUDY / "rulearena" / "checkout" / "nba" / "auto_test.py").read_text(encoding="utf-8")
    assert "$140,588,000" in src and derive.CAP == Decimal("140588000")
    assert "$136,000,000" in src and derive.CAP_2023_24 == Decimal("136000000")
    assert "$9,700,000" in src and derive.AVG_PLAYER_SALARY_2023_24 == Decimal("9700000")
    assert "$178,132,000" in src and derive.FIRST_APRON == Decimal("178132000")
    assert "$188,931,000" in src and derive.SECOND_APRON == Decimal("188931000")
    assert "$170,814,000" in src and derive.LUXURY_TAX == Decimal("170814000")


def test_exception_amounts_follow_the_cba_percentages():
    assert derive.NTMLE_AMOUNT == Decimal("0.0912") * derive.CAP
    assert derive.BAE_AMOUNT == Decimal("0.0332") * derive.CAP
    assert derive.ROOM_MLE_AMOUNT == Decimal("0.05678") * derive.CAP
    assert derive.TMLE_AMOUNT == Decimal("5000000") * (derive.CAP / derive.CAP_2023_24)


def test_minimum_salary_is_deliberately_unavailable():
    assert derive.MINIMUM_PLAYER_SALARY is None
    assert derive.MINIMUM_ANNUAL_SALARY is None


# --------------------------------------------------------------------------- #
# 3. salary schedules
# --------------------------------------------------------------------------- #
def test_schedule_is_linear_on_the_first_year_salary():
    sched = derive.contract_schedule(contract(years="4", first="20000000", pct="5"))
    assert sched == [Decimal("20000000"), Decimal("21000000"),
                     Decimal("22000000"), Decimal("23000000")]


def test_schedule_handles_decrease():
    sched = derive.contract_schedule(
        contract(years="3", first="10000000", pct="10", direction="decrease"))
    assert sched == [Decimal("10000000"), Decimal("9000000"), Decimal("8000000")]


def test_schedule_applies_year_overrides():
    c = contract(years="3", first="11000000", pct="5",
                 applies="first_two_salary_cap_years",
                 year_salary_overrides=[{"which_year": "3", "salary": "30000000"}])
    assert derive.contract_schedule(c) == [
        Decimal("11000000"), Decimal("11550000"), Decimal("30000000")]


def test_schedule_of_a_minimum_contract_is_unknown():
    assert derive.contract_schedule(contract(kind="minimum", years="2")) is None
    assert derive.contract_first_year_amount(contract(kind="minimum")) is None


def test_percent_of_cap_contract_uses_the_stipulated_cap():
    c = {"years": "2", "salary_kind": "percent_of_salary_cap",
         "percent_of_salary_cap": "9.12", "annual_change_pct": "5",
         "annual_change_direction": "increase", "annual_change_applies_to": "all_years"}
    assert derive.contract_first_year_amount(c) == Decimal("0.0912") * derive.CAP


# --------------------------------------------------------------------------- #
# 4. player view
# --------------------------------------------------------------------------- #
def test_years_of_service_and_age():
    p = derive.PlayerView("A", player(draft_year="2016", age="19"))
    assert p.yos == 8
    assert p.age == 27


def test_free_agent_class_from_preceding_season_coverage():
    # 2020 + 4 seasons -> covers 2020..2023, i.e. all three preceding -> Qualifying
    assert derive.PlayerView("A", player(signed=2020, years="4")).fa_class == "qualifying"
    # 2022 + 2 -> covers 2022, 2023 -> Early Qualifying
    assert derive.PlayerView("A", player(signed=2022, years="2")).fa_class == "early_qualifying"
    # 2023 + 1 -> covers 2023 only -> Non-Qualifying
    assert derive.PlayerView("A", player(signed=2023, years="1")).fa_class == "non_qualifying"


def test_player_still_under_contract_has_no_free_agent_class():
    p = derive.PlayerView("A", player(signed=2023, years="4"))
    assert p.under_contract is True
    assert p.fa_class is None
    assert p.current_salary == Decimal("21000000")   # second season of the schedule


def test_prior_team_follows_a_stated_trade():
    raw = player(team="A")
    raw["transactions"] = [{"type": "traded", "to_team": "B",
                            "during": {"kind": "regular_season", "cap_year": "2022-2023"}}]
    assert derive.PlayerView("A", raw).prior_team == "B"


def test_higher_max_criteria_needs_all_nba_or_dpoy_not_all_defensive():
    yes = derive.PlayerView("A", player(awards=[{"cap_year": "2023-24",
                                                 "award": "all_nba_second_team"}]))
    no = derive.PlayerView("A", player(awards=[{"cap_year": "2023-24",
                                                "award": "all_nba_defensive_second_team"}]))
    assert yes.higher_max is True
    assert no.higher_max is False


def test_higher_max_two_of_the_preceding_three_seasons():
    p = derive.PlayerView("A", player(awards=[
        {"cap_year": "2021-22", "award": "all_nba_third_team"},
        {"cap_year": "2022-23", "award": "all_nba_third_team"}]))
    assert p.higher_max is True


def test_free_agent_amount_multipliers():
    # prior salary 23,000,000 >= estimated average -> 150%
    p = derive.PlayerView("A", player(signed=2020, years="4", first="20000000"))
    assert p.prior_salary == Decimal("23000000")
    assert p.free_agent_amount() == Decimal("1.50") * Decimal("23000000")
    # below the estimated average player salary -> 190%
    q = derive.PlayerView("A", player(signed=2020, years="4", first="1000000"))
    assert q.free_agent_amount() == Decimal("1.90") * q.prior_salary


# --------------------------------------------------------------------------- #
# 5. presence discipline
# --------------------------------------------------------------------------- #
def test_all_39_always_present_booleans_are_emitted_for_an_empty_instance():
    d = derive.derive(doc())
    for k in derive.ALWAYS_PRESENT:
        assert k in d, k
        assert isinstance(d[k], bool), k
    assert len(derive.ALWAYS_PRESENT) == 39


def test_no_value_is_ever_a_json_number():
    d = derive.derive(doc(
        teams={"A": {"salary": "160000000"}, "B": {"salary": "120000000"}},
        players={"A": player()},
        operations=[{"label": "A", "type": "sign", "team": "A", "player": "A",
                     "parsed": True, "raw": "", "contract": contract()}]))
    for k, v in d.items():
        assert isinstance(v, (bool, str)), (k, v)
        if isinstance(v, str):
            assert DEC_RE.match(v), (k, v)


def test_unavailable_quantity_is_omitted_not_guessed():
    """A minimum-salary signing leaves the cap ratios out rather than inventing one."""
    d, notes = derive.derive_with_notes(doc(
        teams={"A": {"salary": "160000000"}},
        players={"A": player(signed=2023, years="1")},
        operations=[{"label": "A", "type": "sign", "team": "A", "player": "A",
                     "parsed": True, "raw": "",
                     "contract": contract(kind="minimum", years="2")}]))
    assert d["uses-minimum-player-salary-exception"] is True
    assert d["has-new-contract-service-7-to-9"] is True          # gate is still emitted
    assert "ratio-max-first-year-salary-to-cap-service-7-to-9" not in d
    assert "ratio-max-first-year-salary-to-cap-service-7-to-9" in notes


def test_minimum_annual_salary_ratio_is_never_emitted():
    d = derive.derive(doc(
        teams={"A": {"salary": "160000000"}},
        players={"A": player(signed=2023, years="1", first="5000000")},
        operations=[{"label": "A", "type": "sign", "team": "A", "player": "A",
                     "parsed": True, "raw": "", "contract": contract(years="2", first="5500000")}]))
    assert d["uses-non-qualifying-veteran-free-agent-exception"] is True
    assert "ratio-non-qualifying-veteran-free-agent-first-year-salary-to-minimum-annual-salary" not in d


# --------------------------------------------------------------------------- #
# 6. exception selection (reading R5)
# --------------------------------------------------------------------------- #
def _one_signing(team_salary, player_raw, contract_):
    d = derive.Derivation(doc(
        teams={"A": {"salary": team_salary}, "B": {"salary": team_salary}},
        players={"A": player_raw},
        operations=[{"label": "A", "type": "sign", "team": "A", "player": "A",
                     "parsed": True, "raw": "", "contract": contract_}]))
    d.assign_exceptions()
    return d.signings[0]


def test_team_with_room_uses_room_not_an_exception():
    s = _one_signing("50000000", player(signed=2023, years="1", team="B"),
                     contract(years="2", first="10000000"))
    assert s.exception == "room"


def test_over_cap_team_below_first_apron_signs_outside_free_agent_on_the_ntmle():
    s = _one_signing("160000000", player(signed=2023, years="1", team="B"),
                     contract(years="2", first="30000000"))
    assert s.exception == "non_taxpayer_mid_level"


def test_team_above_first_apron_signs_on_the_taxpayer_mle():
    s = _one_signing("180000000", player(signed=2023, years="1", team="B"),
                     contract(years="2", first="30000000"))
    assert s.exception == "taxpayer_mid_level"


def test_prior_team_re_signing_claims_the_lowest_sufficient_bird_tier():
    # prior salary 23,000,000; 120% = 27,600,000 -> Non-Bird suffices
    s = _one_signing("160000000", player(signed=2020, years="4", team="A"),
                     contract(years="2", first="25000000"))
    assert s.exception == "non_qualifying_veteran_free_agent"
    # 40,000,000 exceeds 175% of 23,000,000 -> Bird
    s2 = _one_signing("160000000", player(signed=2020, years="4", team="A"),
                      contract(years="2", first="45000000"))
    assert s2.exception == "qualifying_veteran_free_agent"


def test_exception_availability_is_false_when_the_class_is_too_low():
    """An Early Qualifying free agent claiming the Bird exception is not entitled to it."""
    d = derive.derive(doc(
        teams={"A": {"salary": "160000000"}},
        players={"A": player(signed=2022, years="2", team="A", first="20000000")},
        operations=[{"label": "A", "type": "sign", "team": "A", "player": "A",
                     "parsed": True, "raw": "", "contract": contract(years="2", first="60000000")}]))
    assert d["uses-qualifying-veteran-free-agent-exception"] is True
    assert d["qualifying-veteran-free-agent-exception-available"] is False


def test_minimum_contract_always_uses_the_minimum_player_salary_exception():
    s = _one_signing("180000000", player(signed=2023, years="1", team="B"),
                     contract(kind="minimum", years="2"))
    assert s.exception == "minimum_player_salary"


# --------------------------------------------------------------------------- #
# 7. traded player exceptions (reading R7)
# --------------------------------------------------------------------------- #
def _trade_doc(sends, receives, a_salary="160000000", b_salary="160000000", players_=None):
    return doc(
        teams={"A": {"salary": a_salary}, "B": {"salary": b_salary}},
        players=players_ or {},
        operations=[{"label": "A", "type": "trade", "parsed": True, "raw": "",
                     "trade": {"from_team": "A", "to_team": "B",
                               "sends": sends, "receives": receives}}])


def test_two_outgoing_players_selects_the_aggregated_exception():
    ps = {"A": player(signed=2023, years="3", first="10000000"),
          "B": player(signed=2023, years="3", first="10000000"),
          "C": player(signed=2023, years="3", first="30000000")}
    d = derive.derive(_trade_doc(
        [{"kind": "player", "player": "A"}, {"kind": "player", "player": "B"}],
        [{"kind": "player", "player": "C"}], players_=ps))
    assert d["uses-aggregated-standard-traded-player-exception"] is True
    assert d["aggregated-traded-player-count"] == "2"


def test_taking_back_more_than_outgoing_plus_250k_selects_the_expanded_exception():
    ps = {"A": player(signed=2023, years="3", first="10000000"),
          "C": player(signed=2023, years="3", first="30000000")}
    d = derive.derive(_trade_doc([{"kind": "player", "player": "A"}],
                                 [{"kind": "player", "player": "C"}], players_=ps))
    assert d["uses-expanded-traded-player-exception"] is True
    # 2024-25 Salaries: incoming 31,500,000; outgoing 10,500,000; 125% = 13,125,000
    assert d["expanded-traded-player-exception-incoming-excess-over-125-percent-outgoing"] \
        == "18375000"


def test_matched_salaries_select_the_standard_exception():
    ps = {"A": player(signed=2023, years="3", first="10000000"),
          "C": player(signed=2023, years="3", first="10000000")}
    d = derive.derive(_trade_doc([{"kind": "player", "player": "A"}],
                                 [{"kind": "player", "player": "C"}], players_=ps))
    assert d["uses-standard-traded-player-exception"] is True
    assert d["standard-traded-player-exception-incoming-excess-over-base-limit"] == "0"
    assert d["traded-player-exception-incoming-excess-over-base-limit-max"] == "0"


def test_unstated_destination_team_omits_the_dependent_ratios():
    ps = {"A": player(signed=2023, years="3", first="10000000")}
    d, notes = derive.derive_with_notes(doc(
        teams={"A": {"salary": "160000000"}}, players=ps,
        operations=[{"label": "A", "type": "trade", "parsed": True, "raw": "",
                     "caveats": ["trade_destination_team_not_stated"],
                     "trade": {"from_team": "A", "to_team": None,
                               "sends": [{"kind": "player", "player": "A"}],
                               "receives": [{"kind": "player", "player": "B"}]}}]))
    assert d["uses-any-traded-player-exception"] is False


# --------------------------------------------------------------------------- #
# 8. cash, picks, over-38
# --------------------------------------------------------------------------- #
def test_cash_flags_and_ratio():
    d = derive.derive(_trade_doc(
        [{"kind": "cash", "amount": "8000000"}],
        [{"kind": "player", "player": "C"}],
        players_={"C": player(signed=2023, years="3", first="10000000")}))
    assert d["includes-cash-in-trade"] is True
    assert d["pays-cash-in-trade"] is True
    assert d["ratio-aggregate-cash-paid-or-received-to-cap"] == derive.dec_str(
        Decimal("8000000") / derive.CAP)


def test_stepien_gap_detected_when_two_consecutive_drafts_lose_their_pick():
    teams = {"A": {"salary": "160000000",
                   "draft_picks": {"own_first_round_years_ahead": "7",
                                   "own_first_round_missing_years": ["2026"],
                                   "acquired_first_round_picks": []}},
             "B": {"salary": "160000000"}}
    d = derive.derive(doc(
        teams=teams,
        operations=[{"label": "A", "type": "trade", "parsed": True, "raw": "",
                     "trade": {"from_team": "A", "to_team": "B",
                               "sends": [{"kind": "draft_pick", "owner": "self",
                                          "round": "1", "year": "2025"}],
                               "receives": [{"kind": "cash", "amount": "1000000"}]}}]))
    assert d["includes-first-round-pick-trade"] is True
    assert d["first-round-pick-trade-leaves-consecutive-drafts-without-pick"] is True
    assert d["first-round-pick-sold-for-cash"] is True


def test_over_38_contract_detection_and_reattribution_direction():
    # age 27 in 2024-25 would not reach 38; age 36 on a 4-year deal does.
    old = player(draft_year="2010", age="22")            # age 36 in 2024-25
    d = derive.derive(doc(
        teams={"A": {"salary": "100000000"}},
        players={"A": old},
        operations=[{"label": "A", "type": "sign", "team": "A", "player": "A",
                     "parsed": True, "raw": "",
                     "contract": contract(years="5", first="20000000")}]))
    assert d["over-38-contract-present"] is True
    with_re = Decimal(d["ratio-post-signing-team-salary-with-over-38-reattribution-to-cap"])
    without = Decimal(d["ratio-post-signing-team-salary-without-over-38-reattribution-to-cap"])
    assert with_re > without


# --------------------------------------------------------------------------- #
# 9. determinism and idempotence
# --------------------------------------------------------------------------- #
def test_derive_is_pure_and_repeatable():
    d0 = doc(teams={"A": {"salary": "160000000"}},
             players={"A": player()},
             operations=[{"label": "A", "type": "sign", "team": "A", "player": "A",
                          "parsed": True, "raw": "", "contract": contract()}])
    a = derive.derive(d0)
    b = derive.derive(d0)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert d0["facts"]["derived"] == {}          # input untouched


def test_derive_ignores_any_preexisting_derived_block():
    d0 = doc(teams={"A": {"salary": "160000000"}})
    clean = derive.derive(d0)
    d0["facts"]["derived"] = {"any-transaction-without-exception": True, "junk": "1"}
    again = derive.derive(d0)
    assert again == clean


# --------------------------------------------------------------------------- #
# 10. contract with the pack
# --------------------------------------------------------------------------- #
def test_every_pointer_the_pack_reads_is_known_to_this_module():
    pack = json.loads((STUDY / "packs" / "nba-transaction-legality.json")
                      .read_text(encoding="utf-8"))
    needed = set(re.findall(r'"/facts/derived/([^"]*)"', json.dumps(pack)))
    assert len(needed) == 124
    src = (PIPELINE / "derive.py").read_text(encoding="utf-8")
    missing = [n for n in sorted(needed) if f'"{n}"' not in src]
    assert missing == [], missing


@pytest.mark.skipif(not (PIPELINE / "out" / "facts" / "index.json").exists(),
                    reason="parser output not present")
def test_corpus_wide_presence_and_grammar():
    facts = PIPELINE / "out" / "facts"
    seen = set()
    for path in sorted(facts.glob("comp_*.json"))[:40]:
        d = derive.derive(json.loads(path.read_text(encoding="utf-8")))
        for k in derive.ALWAYS_PRESENT:
            assert k in d and isinstance(d[k], bool), (path.name, k)
        for k, v in d.items():
            assert isinstance(v, (bool, str))
            if isinstance(v, str):
                assert DEC_RE.match(v), (path.name, k, v)
        seen |= set(d)
    assert len(seen) > 60
