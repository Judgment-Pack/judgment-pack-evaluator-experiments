"""Tests for the deterministic RuleArena NBA facts parser.

WHAT THIS CHECKS
----------------
* the corpus really is 216 instances and all 216 produce a facts document;
* a hand-checked round trip: specific instances parse to specific values, so a
  refactor that changes *meaning* fails rather than merely changing coverage;
* every value the JPS grammar would ever ORDER-COMPARE is a decimal STRING
  matching ``-?(0|[1-9][0-9]*)(\\.[0-9]+)?`` and no ``facts`` subtree contains a
  bare JSON number;
* every fact is reachable by an RFC 6901 JSON Pointer (resolver implemented
  here, stdlib only) and pointer round-tripping returns the same object;
* determinism: parsing twice yields byte-identical serialisations;
* ``facts.derived`` is present and empty (``derive.py`` owns it).

WHAT THIS DELIBERATELY DOES NOT CHECK
-------------------------------------
Nothing about the CBA, legality, derived quantities, or whether the gold labels
are right.  This file tests extraction fidelity only.
"""

from __future__ import annotations

import json
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
PIPELINE = os.path.dirname(HERE)
STUDY = os.path.dirname(PIPELINE)
CHECKOUT = os.path.join(STUDY, "rulearena", "checkout")

sys.path.insert(0, PIPELINE)

import parse_nba  # noqa: E402

DECIMAL_RE = re.compile(r"-?(0|[1-9][0-9]*)(\.[0-9]+)?\Z")

# Keys whose values must be JPS-grammar decimal strings wherever they appear.
NUMERIC_KEYS = {
    "salary", "amount", "first_year_salary", "annual_change_pct", "years",
    "pick", "age_at_draft", "own_first_round_years_ahead", "minimum_plus_amount",
    "players_signed_before_new_season", "percent_of_salary_cap",
    "stated_total_salary", "stated_total_years", "day",
}


@pytest.fixture(scope="session")
def parsed():
    docs, residues, caveats = parse_nba.parse_checkout(CHECKOUT)
    return docs, residues, caveats


@pytest.fixture(scope="session")
def by_id(parsed):
    docs, _, _ = parsed
    return {d["instance_id"]: d for d in docs}


# ---------------------------------------------------------------------------
# corpus shape
# ---------------------------------------------------------------------------

def test_corpus_is_216_instances(parsed):
    docs, _, _ = parsed
    assert len(docs) == 216
    assert len({d["instance_id"] for d in docs}) == 216


def test_per_file_counts(parsed):
    docs, _, _ = parsed
    counts = {}
    for d in docs:
        counts[d["provenance"]["file"]] = counts.get(d["provenance"]["file"], 0) + 1
    assert counts == {"comp_0.json": 81, "comp_1.json": 89, "comp_2.json": 46}


def test_every_instance_has_the_contract_shape(parsed):
    docs, _, _ = parsed
    for d in docs:
        assert set(d) >= {"instance_id", "facts", "gold", "provenance"}
        facts = d["facts"]
        assert set(facts) >= {"teams", "players", "operations", "derived"}
        assert isinstance(facts["teams"], dict)
        assert isinstance(facts["players"], dict)
        assert isinstance(facts["operations"], list)
        assert facts["operations"], d["instance_id"]
        assert set(d["gold"]) == {
            "answer", "illegal_operation", "problematic_team", "relevant_rules"}
        assert isinstance(d["gold"]["answer"], bool)
        assert d["provenance"]["commit"] == parse_nba.SOURCE_COMMIT


def test_derived_is_empty_and_owned_elsewhere(parsed):
    docs, _, _ = parsed
    for d in docs:
        assert d["facts"]["derived"] == {}


def test_no_residue(parsed):
    """The parser must consume every sentence; residue is a hard failure here.

    If this ever fails, the residues themselves are the deliverable -- do not
    loosen the assertion, record them in PARSE-COVERAGE.md.
    """
    _, residues, _ = parsed
    assert residues == [], residues[:5]


def test_all_operations_parsed(parsed):
    docs, _, _ = parsed
    unparsed = [(d["instance_id"], o["raw"])
                for d in docs for o in d["facts"]["operations"] if not o["parsed"]]
    assert unparsed == []


# ---------------------------------------------------------------------------
# hand-checked round trips
# ---------------------------------------------------------------------------

def test_round_trip_sign_and_trade(by_id):
    d = by_id["comp_0#000"]
    assert d["facts"]["teams"]["A"]["salary"] == "160000000"
    assert d["facts"]["teams"]["B"]["salary"] == "120000000"

    pa = d["facts"]["players"]["A"]
    assert pa["draft"] == {"round": "1", "pick": "3", "team": "C",
                           "year": "2016", "age_at_draft": "19"}
    assert pa["contract"]["years"] == "4"
    assert pa["contract"]["first_year_salary"] == "20000000"
    assert pa["contract"]["annual_change_pct"] == "5"
    assert pa["contract"]["annual_change_direction"] == "increase"
    assert pa["contract"]["signed_with_team"] == "A"
    assert pa["contract"]["signed_during"] == {"kind": "moratorium_period",
                                               "year": "2020"}
    assert pa["awards"] == [{"cap_year": "2023-24", "award": "all_nba_second_team"}]

    pc = d["facts"]["players"]["C"]
    assert pc["contract"]["salary_kind"] == "minimum"
    assert pc["contract"]["minimum_salary_phrase"] == "minimum applicable player salary"

    op = d["facts"]["operations"][0]
    assert op["type"] == "sign_and_trade"
    assert op["label"] == "A"
    assert op["team"] == "A" and op["player"] == "A"
    assert op["contract"]["years"] == "3"
    assert op["contract"]["first_year_salary"] == "35000000"
    assert op["contract"]["first_cap_year"] == "2024-2025"
    # "trades Player A with Player C and D to Team B for Player B"
    assert op["trade"]["from_team"] == "A" and op["trade"]["to_team"] == "B"
    assert op["trade"]["sends"] == [
        {"kind": "player", "player": "A"},
        {"kind": "player", "player": "C"},
        {"kind": "player", "player": "D"},
    ]
    assert op["trade"]["receives"] == [{"kind": "player", "player": "B"}]

    assert d["gold"]["answer"] is True
    assert d["gold"]["illegal_operation"] == "A"
    assert d["gold"]["problematic_team"] == "A"
    assert len(d["gold"]["relevant_rules"]) == 11


def test_round_trip_explicit_year_schedule(by_id):
    """Per-year overrides plus a stated total (comp_1#085 operation B)."""
    d = by_id["comp_1#085"]
    op = [o for o in d["facts"]["operations"] if o["label"] == "B"][0]
    assert op["type"] == "offer_sheet"
    c = op["contract"]
    assert c["first_year_salary"] == "9258000"
    assert c["year_salary_overrides"] == [
        {"which_year": "2", "salary": "9721000"},
        {"which_year": "3", "salary": "10279000"},
        {"which_year": "4", "salary": "17742000"},
    ]
    assert c["stated_total_salary"] == "40000000"
    assert c["stated_total_years"] == "4"


def test_round_trip_percent_of_cap(by_id):
    d = by_id["comp_0#054"]
    op = [o for o in d["facts"]["operations"] if o["label"] == "B"][0]
    c = op["contract"]
    assert c["salary_kind"] == "percent_of_salary_cap"
    assert c["percent_of_salary_cap"] == "9.12"
    assert c["annual_change_pct"] == "5"
    assert c["annual_change_applies_to"] == "first_two_salary_cap_years"
    assert c["year_salary_overrides"] == [
        {"which_year": "3", "salary": "25000000"},
        {"which_year": "4", "salary": "26000000"},
    ]


def test_round_trip_draft_picks_and_exceptions(by_id):
    """Team-level draft-pick inventory, TPE and bi-annual usage."""
    hits = 0
    for iid, d in by_id.items():
        for letter, team in d["facts"]["teams"].items():
            dp = team.get("draft_picks")
            if dp and dp["own_first_round_missing_years"] and \
                    dp["acquired_first_round_picks"]:
                assert dp["own_first_round_years_ahead"] == "7"
                for y in dp["own_first_round_missing_years"]:
                    assert re.fullmatch(r"[0-9]{4}", y)
                for a in dp["acquired_first_round_picks"]:
                    assert re.fullmatch(r"[A-Z]", a["from_team"])
                    assert re.fullmatch(r"[0-9]{4}", a["year"])
                hits += 1
    assert hits > 0


def test_decrease_is_a_negative_decimal_string(by_id):
    found = []
    for d in by_id.values():
        for o in d["facts"]["operations"]:
            c = o.get("contract", {})
            if c.get("annual_change_direction") == "decrease":
                found.append(c["annual_change_pct"])
    assert found, "corpus contains '% decrease per year' operations"
    for v in found:
        assert v.startswith("-")
        assert DECIMAL_RE.match(v)


def test_three_team_trades_are_flagged_not_guessed(parsed, by_id):
    _, _, caveats = parsed
    flagged = {iid for iid, c in caveats.items()
               if "three_team_simultaneous_trade" in c}
    assert flagged == {"comp_1#001", "comp_1#002", "comp_1#003", "comp_2#000"}
    for iid in flagged:
        op = [o for o in by_id[iid]["facts"]["operations"]
              if "additional_legs" in o][0]
        assert op["trade"]["third_team_asset_binding"] == "unresolved"
        assert op["trade"]["receives_clause_raw"]
        assert op["additional_legs"]


def test_operation_types_are_a_closed_set(by_id):
    allowed = {"sign", "sign_and_trade", "multi_sign", "trade",
               "qualifying_offer", "offer_sheet", "match_offer_sheet"}
    seen = {o["type"] for d in by_id.values() for o in d["facts"]["operations"]}
    assert seen <= allowed
    assert "unparsed" not in seen


def test_every_referenced_player_and_team_has_a_slot(by_id):
    for iid, d in by_id.items():
        players, teams = d["facts"]["players"], d["facts"]["teams"]
        for o in d["facts"]["operations"]:
            if o.get("player"):
                assert o["player"] in players, (iid, o["player"])
            if o.get("team"):
                assert o["team"] in teams, (iid, o["team"])
            for leg in [o.get("trade")] + o.get("additional_legs", []):
                if not leg:
                    continue
                for side in ("sends", "receives"):
                    for a in leg[side]:
                        if a["kind"] == "player":
                            assert a["player"] in players, (iid, a)


# ---------------------------------------------------------------------------
# JPS decimal-string discipline
# ---------------------------------------------------------------------------

def _walk(node, prefix=""):
    yield prefix, node
    if isinstance(node, dict):
        for k, v in node.items():
            token = str(k).replace("~", "~0").replace("/", "~1")
            yield from _walk(v, prefix + "/" + token)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk(v, prefix + "/" + str(i))


def test_no_json_numbers_anywhere_in_facts(parsed):
    docs, _, _ = parsed
    offenders = []
    for d in docs:
        for ptr, value in _walk(d["facts"], "/facts"):
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                offenders.append((d["instance_id"], ptr, value))
    assert offenders == [], offenders[:10]


def test_numeric_fields_are_jps_decimal_strings(parsed):
    docs, _, _ = parsed
    offenders = []
    checked = 0
    for d in docs:
        for ptr, value in _walk(d["facts"], "/facts"):
            key = ptr.rsplit("/", 1)[-1]
            if key not in NUMERIC_KEYS:
                continue
            if value is None:
                continue
            checked += 1
            if not isinstance(value, str) or not DECIMAL_RE.match(value):
                offenders.append((d["instance_id"], ptr, value))
    assert checked > 1000, "expected thousands of numeric fields, got %d" % checked
    assert offenders == [], offenders[:10]


def test_parser_own_validator_agrees(parsed):
    docs, _, _ = parsed
    for d in docs:
        assert parse_nba.check_decimal_strings(d) == []


def test_money_helper_rejects_non_decimals():
    assert parse_nba.money("$160,000,000") == "160000000"
    assert parse_nba.num("21th") == "21"
    assert parse_nba.num("5.5") == "5.5"
    with pytest.raises(ValueError):
        parse_nba.money("$1,60o,000")


# ---------------------------------------------------------------------------
# RFC 6901 addressability
# ---------------------------------------------------------------------------

def resolve_pointer(doc, pointer):
    """Minimal RFC 6901 resolver (stdlib only)."""
    if pointer == "":
        return doc
    if not pointer.startswith("/"):
        raise ValueError("pointer must start with '/': %r" % pointer)
    node = doc
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(node, list):
            if not re.fullmatch(r"0|[1-9][0-9]*", token):
                raise KeyError(pointer)
            node = node[int(token)]
        elif isinstance(node, dict):
            node = node[token]
        else:
            raise KeyError(pointer)
    return node


def test_every_fact_is_addressable_by_json_pointer(parsed):
    docs, _, _ = parsed
    total = 0
    for d in docs:
        for ptr, value in _walk(d, ""):
            resolved = resolve_pointer(d, ptr)
            assert resolved is value or resolved == value, ptr
            total += 1
    assert total > 25000


def test_no_key_needs_pointer_escaping_beyond_rfc6901(parsed):
    """Keys are plain identifiers / single letters, so pointers stay readable."""
    docs, _, _ = parsed
    for d in docs:
        for ptr, value in _walk(d["facts"], "/facts"):
            if isinstance(value, dict):
                for k in value:
                    assert "/" not in k and "~" not in k, (d["instance_id"], k)


def test_known_pointers_resolve(by_id):
    d = by_id["comp_0#000"]
    assert resolve_pointer(d, "/facts/teams/A/salary") == "160000000"
    assert resolve_pointer(d, "/facts/players/A/draft/pick") == "3"
    assert resolve_pointer(d, "/facts/operations/0/type") == "sign_and_trade"
    assert resolve_pointer(
        d, "/facts/operations/0/trade/sends/1/player") == "C"
    assert resolve_pointer(d, "/facts/derived") == {}


# ---------------------------------------------------------------------------
# determinism
# ---------------------------------------------------------------------------

def test_parsing_twice_is_byte_identical():
    first, res1, cav1 = parse_nba.parse_checkout(CHECKOUT)
    second, res2, cav2 = parse_nba.parse_checkout(CHECKOUT)
    blob1 = "".join(parse_nba.dumps(d) for d in first)
    blob2 = "".join(parse_nba.dumps(d) for d in second)
    assert blob1 == blob2
    assert json.dumps(res1, sort_keys=True) == json.dumps(res2, sort_keys=True)
    assert cav1 == cav2


def test_serialisation_is_stable_and_sorted(parsed):
    docs, _, _ = parsed
    blob = parse_nba.dumps(docs[0])
    assert blob == parse_nba.dumps(json.loads(blob))
    assert blob.endswith("\n")


def test_instance_ids_are_zero_padded_and_ordered(parsed):
    docs, _, _ = parsed
    ids = [d["instance_id"] for d in docs]
    assert ids[0] == "comp_0#000"
    assert ids[80] == "comp_0#080"
    assert ids[81] == "comp_1#000"
    for iid in ids:
        assert re.fullmatch(r"comp_[012]#[0-9]{3}", iid)


# ---------------------------------------------------------------------------
# normalisation table
# ---------------------------------------------------------------------------

def test_typo_table_is_narrow():
    """Every typo fix must actually fire, and none may be a broad rewrite."""
    raws = []
    base = os.path.join(CHECKOUT, "nba", "annotated_problems")
    for name in parse_nba.COMP_FILES:
        with open(os.path.join(base, name), encoding="utf-8") as fh:
            for r in json.load(fh):
                raws += (r["team_situations"] + r["player_situations"]
                         + r["operations"])
    for pattern, _repl in parse_nba.TYPO_FIXES:
        hits = sum(1 for s in raws if re.search(pattern, " ".join(s.split())))
        assert hits > 0, "dead typo rule: %r" % pattern
        assert hits <= 10, "suspiciously broad typo rule %r (%d hits)" % (pattern, hits)


def test_normalise_is_idempotent(parsed):
    docs, _, _ = parsed
    for d in docs[:30]:
        for section in ("team_situations", "player_situations", "operations"):
            for s in d["provenance"]["raw"][section]:
                once = parse_nba.normalise(s)
                assert parse_nba.normalise(once) == once
