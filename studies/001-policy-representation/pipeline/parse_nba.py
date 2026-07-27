#!/usr/bin/env python3
"""Deterministic facts parser for the RuleArena NBA slice.

WHAT THIS DOES
--------------
Reads the 216 human-annotated NBA problems from a read-only RuleArena checkout
(``nba/annotated_problems/comp_{0,1,2}.json``) and converts their templated
English prose -- ``team_situations``, ``player_situations``, ``operations`` --
into the study's facts-document contract (v1), one JSON file per instance plus
an ``index.json`` manifest.

The extraction path is pure regex/grammar: a hand-written recursive-descent-ish
scanner built from anchored regular expressions.  There is NO language model,
no heuristic similarity matching, no probabilistic tagging, and no network
access anywhere in this file.  That is the point: the study compares three ways
of *representing policy*, so the *facts* handed to all three arms must be
produced by a mechanism that cannot itself be accused of doing the reasoning.

Every numeric or monetary value that any rule might ORDER-COMPARE is emitted as
a JSON **string** matching the JPS decimal grammar ``-?(0|[1-9][0-9]*)(\\.[0-9]+)?``
because the JPS evaluator yields ``unknown`` for ordered comparison of JSON
numbers.  Booleans stay booleans.  Every fact is addressable by RFC 6901 JSON
Pointer (no key contains ``/`` or ``~``; arrays are indexed).

Nothing is ever silently dropped.  Any sentence -- or any fragment of a
sentence -- that the grammar does not fully consume is recorded verbatim as an
explicit residue entry carrying its instance id, section, and text, and the
instance is marked ``parsed_fully: false``.

WHAT THIS DELIBERATELY DOES NOT DO
----------------------------------
* It does not compute anything.  ``facts.derived`` is emitted as ``{}`` and is
  owned by a separate deterministic preprocessor (``derive.py``, not this file).
  No salary escalation, no cap/apron comparison, no minimum-scale lookup, no
  years-of-service arithmetic, no "salary after this signing".
* It does not interpret the CBA.  It does not decide legality, does not touch
  ``relevant_rules`` beyond copying them into ``gold`` verbatim, and encodes no
  rule semantics.
* It does not repair the benchmark.  Source typos are normalised only through a
  small, closed, fully-enumerated table (see ``TYPO_FIXES``) that rewrites
  misspellings into their obvious template form; it never invents, infers, or
  fills in missing values.
* It does not resolve the one genuine structural ambiguity in the corpus (the
  three-team "Simultaneously in this trade" sentences).  Those are parsed under
  a stated reading and flagged with a machine-readable ``caveats`` entry.

CLI
---
    python parse_nba.py --checkout <rulearena/checkout> --out <dir> [--strict]

``--strict`` exits non-zero if any residue was recorded.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

CONTRACT_VERSION = "facts/v1"
SOURCE_COMMIT = "3b9e2256294644beca66732babc5e1055855a576"
COMP_FILES = ("comp_0.json", "comp_1.json", "comp_2.json")

DECIMAL_RE = re.compile(r"-?(0|[1-9][0-9]*)(\.[0-9]+)?\Z")


# ---------------------------------------------------------------------------
# normalisation
# ---------------------------------------------------------------------------

# Closed, exhaustive table of source-text misspellings.  Each entry is an
# anchored-as-tightly-as-possible regex that rewrites a typo into the template
# form it obviously intends.  Nothing here changes any VALUE -- only spelling,
# a doubled noun, and two dropped words.  Every entry, its blast radius, and the
# sentences it touches are enumerated in PARSE-COVERAGE.md.
TYPO_FIXES: Tuple[Tuple[str, str], ...] = (
    (r"\bcontrct\b", "contract"),                       # 3 sentences
    (r"\bproving annual salary\b", "providing annual salary"),   # 3
    (r"\btraeds\b", "trades"),                          # 2
    (r"\bsignes with\b", "signs with"),                 # 2
    (r"\bminimal annual salary\b", "minimum annual salary"),     # 1
    (r"execute the transaction in in ", "execute the transaction in "),  # 1
    # "Player A and signed a 3-year contract ..." -- stray leading conjunction.
    # Anchored at sentence start so the *legitimate* combined form
    # "... when he was 20 years old and signed a ..." is untouched.
    (r"\A(Player [A-Z]) and signed a ", r"\1 signed a "),        # 2
    # "signs a contract 2-year contract with" -- doubled noun
    (r"signs a contract ([0-9]+-year contract)", r"signs a \1"),  # 3
    # "in the first Salary year (2024-2025)" -- dropped "Cap"
    (r"in the first Salary year \(", "in the first Salary Cap Year ("),  # 6
    # "for its first-round 2028" -- dropped "draft pick in"
    (r"for its (first|second)-round ([0-9]{4})",
     r"for its \1-round draft pick in \2"),             # 1
)

_TYPO_FIXES_COMPILED = tuple((re.compile(p), r) for p, r in TYPO_FIXES)


def normalise(text: str) -> str:
    """Collapse whitespace, fix known typos, strip the sentence terminator."""
    out = " ".join(text.split())
    for pat, repl in _TYPO_FIXES_COMPILED:
        out = pat.sub(repl, out)
    return out.rstrip(" .;")


def money(raw: str) -> str:
    """'$160,000,000' or '160,000,000' -> JPS decimal string '160000000'."""
    digits = raw.replace("$", "").replace(",", "").strip()
    if not DECIMAL_RE.match(digits):
        raise ValueError("not a JPS decimal: %r" % raw)
    return digits


def num(raw: str) -> str:
    """'21th' / '007' / '5.5' -> JPS decimal string."""
    s = re.sub(r"(st|nd|rd|th)\Z", "", raw.strip())
    s = s.replace(",", "")
    if re.fullmatch(r"0[0-9]+", s):
        s = s.lstrip("0") or "0"
    if not DECIMAL_RE.match(s):
        raise ValueError("not a JPS decimal: %r" % raw)
    return s


# ---------------------------------------------------------------------------
# generic anchored scanner
# ---------------------------------------------------------------------------

class Scanner:
    """Consumes ``text`` left-to-right with anchored regexes.

    A production is (name, compiled_regex, handler).  ``run`` repeatedly tries
    every production at the cursor, longest match wins (ties -> first listed),
    then consumes a separator.  Whatever is left over is the residue.
    """

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0

    def rest(self) -> str:
        return self.text[self.pos:]

    def try_match(self, pattern: "re.Pattern[str]") -> Optional["re.Match[str]"]:
        m = pattern.match(self.text, self.pos)
        if m:
            self.pos = m.end()
        return m

    def eat(self, pattern: "re.Pattern[str]") -> bool:
        return self.try_match(pattern) is not None

    def done(self) -> bool:
        return self.pos >= len(self.text)


def scan_list(text: str, productions, sep_re) -> Tuple[List[Any], str]:
    """Parse a separator-joined list.  Returns (items, unconsumed_residue)."""
    sc = Scanner(text)
    items: List[Any] = []
    while not sc.done():
        best = None
        for pat, handler in productions:
            m = pat.match(sc.text, sc.pos)
            if m and (best is None or m.end() > best[0].end()):
                best = (m, handler)
        if best is None:
            break
        m, handler = best
        sc.pos = m.end()
        produced = handler(m)
        if produced is not None:
            if isinstance(produced, list):
                items.extend(produced)
            else:
                items.append(produced)
        if sc.done():
            break
        if not sc.eat(sep_re):
            break
    return items, sc.rest()


# ---------------------------------------------------------------------------
# team situations
# ---------------------------------------------------------------------------

TEAM_PATTERNS: List[Tuple[str, "re.Pattern[str]"]] = [
    # T1
    ("team_salary",
     re.compile(r"\ATeam ([A-Z]) has a team salary of \$([0-9]+(?:,[0-9]{3})*)\Z")),
    # T2 / T3 / T4 / T5 / T6 / T7
    ("team_draft_picks",
     re.compile(
         r"\ATeam ([A-Z]) has all its first-round draft picks in the following "
         r"([0-9]+) years"
         r"(?: except ((?:[0-9]{4})(?: and [0-9]{4})*))?"
         r"(?: and Team ([A-Z])'s first-round draft picks? in "
         r"((?:[0-9]{4})(?: and [0-9]{4})*))?\Z")),
    # T8 -- "Team A, Team B, and Team C have all their ..."
    ("team_draft_picks_multi",
     re.compile(
         r"\A((?:Team [A-Z], )+(?:and )?Team [A-Z]) have all their "
         r"first-round draft picks in the following ([0-9]+) years\Z")),
    # T9
    ("team_roster_signings",
     re.compile(r"\ATeam ([A-Z]) signs ([0-9]+) players before the new season\Z")),
    # T10
    ("team_traded_player_exception",
     re.compile(r"\ATeam ([A-Z]) got a \$([0-9]+(?:,[0-9]{3})*) Traded Player Exception "
                r"during ([0-9]{4}-[0-9]{2,4}) Salary Cap Year\Z")),
    # T11
    ("team_bi_annual_exception_used",
     re.compile(r"\ATeam ([A-Z]) used its bi-annual exception to sign a player "
                r"in the ([0-9]{4}-[0-9]{2,4}) Salary Cap Year\Z")),
]

YEAR_LIST_RE = re.compile(r"[0-9]{4}")


def team_slot(teams: Dict[str, Dict[str, Any]], letter: str) -> Dict[str, Any]:
    return teams.setdefault(letter, {})


def parse_team_situation(sentence: str, teams: Dict[str, Dict[str, Any]]) -> Optional[str]:
    """Returns the variant name on success, or None (caller records residue)."""
    text = normalise(sentence)
    if not text:
        return "empty"
    for name, pat in TEAM_PATTERNS:
        m = pat.match(text)
        if not m:
            continue
        if name == "team_salary":
            team_slot(teams, m.group(1))["salary"] = money(m.group(2))
        elif name == "team_draft_picks":
            slot = team_slot(teams, m.group(1)).setdefault("draft_picks", {})
            slot["own_first_round_years_ahead"] = num(m.group(2))
            slot["own_first_round_missing_years"] = (
                YEAR_LIST_RE.findall(m.group(3)) if m.group(3) else [])
            acquired = slot.setdefault("acquired_first_round_picks", [])
            if m.group(4):
                for yr in YEAR_LIST_RE.findall(m.group(5)):
                    acquired.append({"from_team": m.group(4), "year": yr})
        elif name == "team_draft_picks_multi":
            for letter in re.findall(r"Team ([A-Z])", m.group(1)):
                slot = team_slot(teams, letter).setdefault("draft_picks", {})
                slot["own_first_round_years_ahead"] = num(m.group(2))
                slot["own_first_round_missing_years"] = []
                slot.setdefault("acquired_first_round_picks", [])
        elif name == "team_roster_signings":
            team_slot(teams, m.group(1))["players_signed_before_new_season"] = num(m.group(2))
        elif name == "team_traded_player_exception":
            team_slot(teams, m.group(1)).setdefault("traded_player_exceptions", []).append(
                {"amount": money(m.group(2)), "cap_year": m.group(3)})
        elif name == "team_bi_annual_exception_used":
            team_slot(teams, m.group(1))["bi_annual_exception_used_cap_year"] = m.group(2)
        return name
    return None


# ---------------------------------------------------------------------------
# contract salary specifications (shared by player_situations and operations)
# ---------------------------------------------------------------------------

CAP_YEAR = r"[0-9]{4}-[0-9]{2,4}"

# S1  explicit first-year amount, optionally anchored to a named cap year
S_EXPLICIT = re.compile(
    r"(?:an )?(?:annual )?salary (?:of )?\$([0-9]+(?:,[0-9]{3})*)"
    r"(?: in the first (?:Salary )?Cap Year(?: \((%s)\))?)?" % CAP_YEAR)
# S1b bare "$N in the first Salary Cap Year (...)" -- dropped "annual salary"
S_EXPLICIT_BARE = re.compile(
    r"\$([0-9]+(?:,[0-9]{3})*)(?: in the first (?:Salary )?Cap Year(?: \((%s)\))?)?" % CAP_YEAR)
# S2  percentage of the Salary Cap
S_PCT_OF_CAP = re.compile(
    r"(?:annual )?salary equal to ([0-9]+(?:\.[0-9]+)?)% (?:of the|\xd7|x) Salary Cap"
    r"(?: in the first( two)? Salary Cap Years?(?: \((" + CAP_YEAR + r")\))?)?")
# S3  non-taxpayer mid-level exception
S_MLE = re.compile(
    r"(?:annual )?salary equal to the non-taxpayer mid-level exception"
    r"(?: in the first two Salary Cap Years \((%s), (%s)\))?" % (CAP_YEAR, CAP_YEAR))
# S4  minimum-salary bases (all spellings)
S_MINIMUM = re.compile(
    r"(?:a |the )?minimum(?: applicable)?(?: player| annual)? salary"
    r"(?: in the first (?:Salary )?Cap Year(?: \((%s)\))?)?"
    r"(?: plus \$([0-9]+(?:,[0-9]{3})*))?" % CAP_YEAR)
# S5  escalator
S_ESCALATOR = re.compile(
    r"([0-9]+(?:\.[0-9]+)?)% (increase|decrease) per year"
    r"( for the first two Salary Cap Years)?")
# S6  explicit per-year override
S_YEAR_OVERRIDE = re.compile(
    r"(?:salary )?\$([0-9]+(?:,[0-9]{3})*) (?:for|in) the (second|third|fourth|last) "
    r"(?:Salary Cap Year|Salary year|Salary Year|Year)")
# S7  redundant total
S_TOTAL = re.compile(r"totally \$([0-9]+(?:,[0-9]{3})*) for ([a-z]+) years")
# S8  bi-annual exception marker (player_situations parenthetical)
S_BIANNUAL = re.compile(r"(?:with )?bi-annual exception")
# S9  contract option markers (player_situations parenthetical)
S_OPTION = re.compile(
    r"(?:with )?(?:the )?(last|second|first|third)"
    r"(?: (two|three))? years? (?:is|are|being) (?:a )?(player|team) options?")

ORDINAL_WORD = {"first": "1", "second": "2", "third": "3", "fourth": "4"}
COUNT_WORD = {"two": "2", "three": "3", "four": "4"}

SALARY_SEP = re.compile(r",? and |, |,? with ")


def _spec_productions(spec: Dict[str, Any]):
    """Productions for the salary-specification scanner; they mutate ``spec``."""

    def base_explicit(m):
        spec["salary_kind"] = "explicit"
        spec["first_year_salary"] = money(m.group(1))
        if m.lastindex and m.group(2):
            spec["first_cap_year"] = m.group(2)
        return None

    def base_pct(m):
        spec["salary_kind"] = "percent_of_salary_cap"
        spec["percent_of_salary_cap"] = num(m.group(1))
        if m.group(2):
            spec["percent_applies_to_first_two_cap_years"] = True
        if m.group(3):
            spec["first_cap_year"] = m.group(3)
        return None

    def base_mle(m):
        spec["salary_kind"] = "non_taxpayer_mid_level_exception"
        if m.group(1):
            spec["first_cap_year"] = m.group(1)
            spec["mle_cap_years"] = [m.group(1), m.group(2)]
        return None

    def base_min(m):
        spec["salary_kind"] = "minimum"
        # The corpus uses "minimum applicable player salary", "minimum salary",
        # "minimum annual salary" and "the minimum salary" interchangeably.  We
        # do not decide whether they mean the same CBA quantity; the literal
        # phrase is preserved so a downstream consumer can.
        spec["minimum_salary_phrase"] = m.group(0).strip()
        if m.group(1):
            spec["first_cap_year"] = m.group(1)
        if m.group(2):
            spec["minimum_plus_amount"] = money(m.group(2))
        return None

    def escalator(m):
        pct = num(m.group(1))
        spec["annual_change_direction"] = m.group(2)
        spec["annual_change_pct"] = ("-" + pct) if m.group(2) == "decrease" else pct
        spec["annual_change_applies_to"] = (
            "first_two_salary_cap_years" if m.group(3) else "all_years")
        return None

    def override(m):
        spec.setdefault("year_salary_overrides", []).append(
            {"which_year": ORDINAL_WORD.get(m.group(2), m.group(2)),
             "salary": money(m.group(1))})
        return None

    def total(m):
        spec["stated_total_salary"] = money(m.group(1))
        spec["stated_total_years"] = COUNT_WORD.get(m.group(2), m.group(2))
        return None

    def biannual(m):
        spec["bi_annual_exception"] = True
        return None

    def option(m):
        which = m.group(1)
        count = m.group(2)
        spec.setdefault("options", []).append({
            "option_holder": m.group(3),
            "which_years": (which + "_" + count + "_years") if count else (which + "_year"),
        })
        return None

    return [
        (S_ESCALATOR, escalator),
        (S_YEAR_OVERRIDE, override),
        (S_TOTAL, total),
        (S_BIANNUAL, biannual),
        (S_OPTION, option),
        (S_PCT_OF_CAP, base_pct),
        (S_MLE, base_mle),
        (S_MINIMUM, base_min),
        (S_EXPLICIT, base_explicit),
        (S_EXPLICIT_BARE, base_explicit),
    ]


def parse_salary_spec(text: str) -> Tuple[Dict[str, Any], str]:
    """Parse a salary specification.  Returns (spec, residue)."""
    spec: Dict[str, Any] = {}
    _, residue = scan_list(text.strip(), _spec_productions(spec), SALARY_SEP)
    if "salary_kind" not in spec:
        spec["salary_kind"] = "unspecified"
    return spec, residue


# ---------------------------------------------------------------------------
# player situations
# ---------------------------------------------------------------------------

DRAFT_RE = re.compile(
    r"\APlayer ([A-Z]) was the ([0-9]+(?:st|nd|rd|th)) (first|second)-round pick "
    r"of Team ([A-Z]) in ([0-9]{4}) NBA draft when he was ([0-9]+) years old")

# "signed a N-year contract (SPEC) with Team X during YYYY Moratorium Period"
# "signed a N-year contract with Team X (SPEC) during YYYY Moratorium Period"
# "signed a N-year contract with Team X providing SPEC during YYYY Moratorium Period"
# "signed a N-year contract with Team X providing SPEC in YYYY Cap Year"
# "signed a N-year contract with Team X providing SPEC"
SIGNED_A = re.compile(
    r"signed a ([0-9]+)-year contract \(([^)]*)\) with Team ([A-Z])"
    r"(?: during ([0-9]{4}) Moratorium Period| in ([0-9]{4}) Cap Year)?\Z")
SIGNED_B = re.compile(
    r"signed a ([0-9]+)-year contract with Team ([A-Z]) \(([^)]*)\)"
    r"(?: during ([0-9]{4}) Moratorium Period| in ([0-9]{4}) Cap Year)?\Z")
SIGNED_C = re.compile(
    r"signed a ([0-9]+)-year contract with Team ([A-Z]) providing (.*?)"
    r"(?: during ([0-9]{4}) Moratorium Period| in ([0-9]{4}) Cap Year)?\Z")

AWARD_RE = re.compile(
    r"\AIn (%s) Salary Cap Year Player ([A-Z]) was named to (?:the )?"
    r"All-NBA (Defending )?(First|Second|Third|first|second|third) [Tt]eam\Z" % CAP_YEAR)

OPTION_DECLINE_RE = re.compile(
    r"\APlayer ([A-Z]) just decided not to exercise (?:the|his) player option"
    r"( and tested free market)?\Z")

TRADED_SIMPLE_RE = re.compile(
    r"\APlayer ([A-Z]) was traded to Team ([A-Z]) during (?:the )?(%s) Regular Season\Z"
    % CAP_YEAR)
TRADED_BY_FOR_RE = re.compile(
    r"\APlayer ([A-Z]) was traded by Team ([A-Z]) to Team ([A-Z]) for Player ([A-Z]) "
    r"during (?:the )?(?:(%s) Regular Season|([0-9]{4}) Moratorium Period)\Z" % CAP_YEAR)
TRADED_WITH_RE = re.compile(
    r"\APlayer ([A-Z]) was traded with Player ([A-Z]) by Team ([A-Z]) to Team ([A-Z]) "
    r"for Player ([A-Z]) during (?:the )?(%s) Regular Season\Z" % CAP_YEAR)

AWARD_SLUG = {
    ("", "first"): "all_nba_first_team",
    ("", "second"): "all_nba_second_team",
    ("", "third"): "all_nba_third_team",
    ("Defending ", "first"): "all_nba_defensive_first_team",
    ("Defending ", "second"): "all_nba_defensive_second_team",
    ("Defending ", "third"): "all_nba_defensive_third_team",
}


def player_slot(players: Dict[str, Dict[str, Any]], letter: str) -> Dict[str, Any]:
    return players.setdefault(letter, {})


def _attach_contract(slot: Dict[str, Any], years: str, team: str, spec_text: str,
                     moratorium: Optional[str], cap_year: Optional[str]) -> str:
    spec, residue = parse_salary_spec(spec_text)
    contract: Dict[str, Any] = {"years": num(years), "signed_with_team": team}
    contract.update(spec)
    if moratorium:
        contract["signed_during"] = {"kind": "moratorium_period", "year": moratorium}
    elif cap_year:
        contract["signed_during"] = {"kind": "cap_year", "year": cap_year}
    slot["contract"] = contract
    return residue


def parse_player_situation(sentence: str,
                           players: Dict[str, Dict[str, Any]]) -> Tuple[Optional[str], str]:
    """Returns (variant_name_or_None, residue)."""
    text = normalise(sentence)
    if not text:
        return "empty", ""

    m = AWARD_RE.match(text)
    if m:
        slot = player_slot(players, m.group(2))
        slot.setdefault("awards", []).append({
            "cap_year": m.group(1),
            "award": AWARD_SLUG[(m.group(3) or "", m.group(4).lower())],
        })
        return "player_award", ""

    m = OPTION_DECLINE_RE.match(text)
    if m:
        slot = player_slot(players, m.group(1))
        slot["player_option_declined"] = True
        slot["tested_free_market"] = bool(m.group(2))
        return "player_option_declined", ""

    m = TRADED_WITH_RE.match(text)
    if m:
        for letter in (m.group(1), m.group(2)):
            player_slot(players, letter).setdefault("transactions", []).append({
                "type": "traded",
                "from_team": m.group(3), "to_team": m.group(4),
                "counterparty_players": [m.group(5)],
                "during": {"kind": "regular_season", "cap_year": m.group(6)},
            })
        player_slot(players, m.group(5)).setdefault("transactions", []).append({
            "type": "traded",
            "from_team": m.group(4), "to_team": m.group(3),
            "counterparty_players": [m.group(1), m.group(2)],
            "during": {"kind": "regular_season", "cap_year": m.group(6)},
        })
        return "player_traded_with_for", ""

    m = TRADED_SIMPLE_RE.match(text)
    if m:
        player_slot(players, m.group(1)).setdefault("transactions", []).append({
            "type": "traded", "to_team": m.group(2),
            "during": {"kind": "regular_season", "cap_year": m.group(3)},
        })
        return "player_traded_to", ""

    m = TRADED_BY_FOR_RE.match(text)
    if m:
        during = ({"kind": "regular_season", "cap_year": m.group(5)} if m.group(5)
                  else {"kind": "moratorium_period", "year": m.group(6)})
        player_slot(players, m.group(1)).setdefault("transactions", []).append({
            "type": "traded", "from_team": m.group(2), "to_team": m.group(3),
            "counterparty_players": [m.group(4)], "during": during})
        player_slot(players, m.group(4)).setdefault("transactions", []).append({
            "type": "traded", "from_team": m.group(3), "to_team": m.group(2),
            "counterparty_players": [m.group(1)], "during": during})
        return "player_traded_by_for", ""

    m = DRAFT_RE.match(text)
    if m:
        slot = player_slot(players, m.group(1))
        slot["draft"] = {
            "round": "1" if m.group(3) == "first" else "2",
            "pick": num(m.group(2)),
            "team": m.group(4),
            "year": m.group(5),
            "age_at_draft": num(m.group(6)),
        }
        tail = text[m.end():].strip()
        if not tail:
            return "player_draft", ""
        # combined "... years old and signed a N-year contract ..."
        tail = re.sub(r"\A(and )?", "", tail)
        variant, residue = _parse_signed_clause(tail, slot)
        if variant is None:
            return None, tail
        return "player_draft+" + variant, residue

    if text.startswith("Player "):
        letter = text[7]
        tail = text[8:].strip()
        if re.fullmatch(r"[A-Z]", letter) and tail.startswith("signed a "):
            slot = player_slot(players, letter)
            variant, residue = _parse_signed_clause(tail, slot)
            if variant is not None:
                return variant, residue
    return None, text


def _parse_signed_clause(tail: str, slot: Dict[str, Any]) -> Tuple[Optional[str], str]:
    m = SIGNED_A.match(tail)
    if m:
        return "player_contract_paren_before_team", _attach_contract(
            slot, m.group(1), m.group(3), m.group(2), m.group(4), m.group(5))
    m = SIGNED_B.match(tail)
    if m:
        return "player_contract_paren_after_team", _attach_contract(
            slot, m.group(1), m.group(2), m.group(3), m.group(4), m.group(5))
    m = SIGNED_C.match(tail)
    if m:
        return "player_contract_providing", _attach_contract(
            slot, m.group(1), m.group(2), m.group(3), m.group(4), m.group(5))
    return None, tail


# ---------------------------------------------------------------------------
# operations
# ---------------------------------------------------------------------------

A_PLAYER = re.compile(r"(?:[Pp]layer )?([A-Z])(?: in [Tt]eam ([A-Z]))?(?![a-z'])")
A_OWN_PICKS = re.compile(
    r"its (first|second)-round draft picks? in ((?:[0-9]{4})(?: and [0-9]{4})*)")
A_OWN_PICK_NOYEAR = re.compile(r"its (first|second)-round draft pick(?! in)")
# bare continuation: "its first-round draft pick in 2026 and second-round draft
# pick in 2028" -- the second conjunct drops the "its"
A_BARE_PICKS = re.compile(
    r"(first|second)-round draft picks? in ((?:[0-9]{4})(?: and [0-9]{4})*)")
A_TEAM_PICKS = re.compile(
    r"Team ([A-Z])'s (first|second)-round draft picks? in "
    r"((?:[0-9]{4})(?: and [0-9]{4})*)")
A_CASH = re.compile(r"\$([0-9]+(?:,[0-9]{3})*)")

ASSET_SEP = re.compile(r", and |,? and |, | with ")


def _asset_productions():
    def own_picks(m):
        return [{"kind": "draft_pick", "round": "1" if m.group(1) == "first" else "2",
                 "year": y, "owner": "self"} for y in YEAR_LIST_RE.findall(m.group(2))]

    def own_pick_noyear(m):
        return {"kind": "draft_pick", "round": "1" if m.group(1) == "first" else "2",
                "year": None, "owner": "self"}

    def team_picks(m):
        return [{"kind": "draft_pick", "round": "1" if m.group(2) == "first" else "2",
                 "year": y, "owner": m.group(1)} for y in YEAR_LIST_RE.findall(m.group(3))]

    def cash(m):
        return {"kind": "cash", "amount": money(m.group(1))}

    def player(m):
        a: Dict[str, Any] = {"kind": "player", "player": m.group(1)}
        if m.group(2):
            a["current_team"] = m.group(2)
        return a

    return [
        (A_OWN_PICKS, own_picks),
        (A_TEAM_PICKS, team_picks),
        (A_BARE_PICKS, own_picks),
        (A_OWN_PICK_NOYEAR, own_pick_noyear),
        (A_CASH, cash),
        (A_PLAYER, player),
    ]


def parse_assets(text: str) -> Tuple[List[Dict[str, Any]], str]:
    return scan_list(text.strip(), _asset_productions(), ASSET_SEP)


TIMING_RE = re.compile(
    r"(?: (?:in|on) (?:the )?"
    r"(January|February|March|April|May|June|July|August|September|October|November|December"
    r"|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    r"(?: of)?(?: ([0-9]{1,2}(?:st|nd|rd|th))?,?)?(?: ([0-9]{4}))?)\Z")


def strip_timing(text: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    m = TIMING_RE.search(text)
    if not m:
        return text, None
    timing: Dict[str, Any] = {"month": m.group(1)}
    if m.group(2):
        timing["day"] = num(m.group(2))
    if m.group(3):
        timing["year"] = m.group(3)
    timing["raw"] = m.group(0).strip()
    return text[:m.start()], timing


TRADE_CLAUSE = re.compile(
    r"\A(?:immediately |subsequently )?trades (.+?)"
    r"(?: to [Tt]eam ([A-Z]))? for (.+)\Z")
# one-directional leg with no consideration named, e.g. the second sentence of a
# three-team "Simultaneously in this trade, Team B trades X to Team C" operation
TRADE_CLAUSE_ONEWAY = re.compile(
    r"\A(?:immediately |subsequently )?trades (.+?) to [Tt]eam ([A-Z])\Z")

# "Team A signs a 3-year contract with Player A providing <spec>"
SIGN_CLAUSE_PROVIDING = re.compile(
    r"\A[Tt]eam ([A-Z]) signs a ([0-9]+)-year contract with [Pp]layer ([A-Z]) "
    r"providing (.+)\Z")
# "Team A signs a 3-year contract with Player A (<spec>)"
SIGN_CLAUSE_PAREN = re.compile(
    r"\A[Tt]eam ([A-Z]) signs a ([0-9]+)-year contract with [Pp]layer ([A-Z]) "
    r"\((.+)\)\Z")
# "Team A signs with Player A with a 3-year contract providing <spec>"
SIGN_CLAUSE_WITH = re.compile(
    r"\A[Tt]eam ([A-Z]) signs with [Pp]layer ([A-Z]) with a ([0-9]+)-year contract "
    r"providing (.+)\Z")

QUALIFYING_RE = re.compile(
    r"\A[Tt]eam ([A-Z]) provides a qualifying offer for [Pp]layer ([A-Z])\Z")
OFFER_SHEET_A = re.compile(
    r"\A[Tt]eam ([A-Z]) provides an offer sheet for [Pp]layer ([A-Z])"
    r"(?: in a ([0-9]+)-year contract)? providing (.+)\Z")
OFFER_SHEET_B = re.compile(
    r"\A[Tt]eam ([A-Z]) provides [Pp]layer ([A-Z]) with an offer sheet - "
    r"a ([0-9]+)-year contract providing (.+)\Z")
MATCH_RE = re.compile(
    r"\A[Tt]eam ([A-Z]) matches the offer(?: sheet)?"
    r"(?: (?:from|by) [Tt]eam ([A-Z])| for [Pp]layer ([A-Z]))?\Z")

SIMULTANEOUS_SPLIT = re.compile(r"\. Simultaneously in this trade, ")
EXECUTE_TAIL = re.compile(r", execute the transaction (in .+)\Z")


def _contract_from_spec(years: Optional[str], spec_text: str) -> Tuple[Dict[str, Any], str]:
    spec, residue = parse_salary_spec(spec_text)
    contract: Dict[str, Any] = {}
    if years:
        contract["years"] = num(years)
    contract.update(spec)
    return contract, residue


def _parse_sign_clause(clause: str) -> Optional[Tuple[Dict[str, Any], str]]:
    for pat in (SIGN_CLAUSE_PAREN, SIGN_CLAUSE_PROVIDING):
        m = pat.match(clause)
        if m:
            contract, residue = _contract_from_spec(m.group(2), m.group(4))
            return {"team": m.group(1), "player": m.group(3),
                    "contract": contract}, residue
    m = SIGN_CLAUSE_WITH.match(clause)
    if m:
        contract, residue = _contract_from_spec(m.group(3), m.group(4))
        return {"team": m.group(1), "player": m.group(2),
                "contract": contract}, residue
    return None


def _parse_trade_clause(clause: str, default_from: Optional[str]
                        ) -> Optional[Tuple[Dict[str, Any], str, List[str]]]:
    """Parse '<Team X> [immediately|subsequently] trades A to Team Y for B'."""
    caveats: List[str] = []
    m = re.match(r"\A[Tt]eam ([A-Z]) (.*)\Z", clause)
    if m and re.match(r"\A(?:immediately |subsequently )?trades ", m.group(2)):
        from_team, body = m.group(1), m.group(2)
    elif re.match(r"\A(?:immediately |subsequently )?trades ", clause):
        from_team, body = default_from, clause
    else:
        return None
    tm = TRADE_CLAUSE.match(body)
    if tm:
        sends_text, to_team, receives_text = tm.group(1), tm.group(2), tm.group(3)
    else:
        ow = TRADE_CLAUSE_ONEWAY.match(body)
        if not ow:
            return None
        sends_text, to_team, receives_text = ow.group(1), ow.group(2), ""

    # three-team form: "... for <assets> to Team C".  Which of the listed assets
    # the trailing "to Team C" governs is NOT determined by the surface syntax;
    # see PARSE-COVERAGE.md, "Documented ambiguity #1".  We keep the whole list
    # in ``receives``, record the third team, preserve the clause verbatim, and
    # flag it.  We do not guess.
    third_party = None
    receives_clause_raw = receives_text
    m3 = re.match(r"\A(.*?) to [Tt]eam ([A-Z])\Z", receives_text)
    if m3:
        receives_text, third_party = m3.group(1), m3.group(2)
        caveats.append("three_team_trade_destination_binding")

    sends, r1 = parse_assets(sends_text)
    receives, r2 = parse_assets(receives_text) if receives_text else ([], "")
    trade: Dict[str, Any] = {
        "from_team": from_team, "to_team": to_team,
        "sends": sends, "receives": receives,
    }
    if third_party:
        trade["third_team"] = third_party
        trade["receives_clause_raw"] = receives_clause_raw
        trade["third_team_asset_binding"] = "unresolved"
    if to_team is None:
        caveats.append("trade_destination_team_not_stated")
    residue = " | ".join(x for x in (r1, r2) if x)
    return trade, residue, caveats


def parse_operation(raw: str) -> Dict[str, Any]:
    """Parse one operation string into a structured record.

    Always returns a record; ``parsed`` is False and ``residue`` is populated
    when the grammar could not fully consume the text.
    """
    m = re.match(r"\A\s*([A-Z])\.\s*(.*)\Z", raw.strip(), re.S)
    if not m:
        return {"label": None, "type": "unparsed", "parsed": False,
                "residue": raw.strip(), "raw": raw}
    label, body = m.group(1), normalise(m.group(2))
    op: Dict[str, Any] = {"label": label, "raw": raw}
    caveats: List[str] = []
    residues: List[str] = []

    # trailing "execute the transaction in January of 2025"
    et = EXECUTE_TAIL.search(body)
    execute_timing = None
    if et:
        body = body[:et.start()]
        _, execute_timing = strip_timing(" " + et.group(1))

    # three-team simultaneous trades
    legs_text = SIMULTANEOUS_SPLIT.split(body)
    head = legs_text[0]
    extra_legs = legs_text[1:]

    # simple, non-trade forms first
    for pat, kind in ((QUALIFYING_RE, "qualifying_offer"),):
        mm = pat.match(head)
        if mm and not extra_legs:
            op.update({"type": kind, "team": mm.group(1), "player": mm.group(2),
                       "parsed": True})
            return op

    mm = MATCH_RE.match(head)
    if mm and not extra_legs:
        op.update({"type": "match_offer_sheet", "team": mm.group(1),
                   "from_team": mm.group(2), "player": mm.group(3), "parsed": True})
        return op

    for pat in (OFFER_SHEET_B, OFFER_SHEET_A):
        mm = pat.match(head)
        if mm and not extra_legs:
            contract, res = _contract_from_spec(mm.group(3), mm.group(4))
            op.update({"type": "offer_sheet", "team": mm.group(1),
                       "player": mm.group(2), "contract": contract})
            if res:
                residues.append(res)
            op["parsed"] = not residues
            if residues:
                op["residue"] = " | ".join(residues)
            return op

    # sign / sign-and-trade / multi-sign / trade
    head_body, timing = strip_timing(head)

    sign_and_trade = re.match(
        r"\A(.*?),? and ((?:immediately |subsequently )trades .*)\Z", head_body)
    multi_sign = re.match(
        r"\A(.*?) and (signs (?:a [0-9]+-year contract with|with) .*)\Z", head_body)

    if sign_and_trade:
        signed = _parse_sign_clause(sign_and_trade.group(1))
        if signed is not None:
            sign_rec, res = signed
            traded = _parse_trade_clause(sign_and_trade.group(2), sign_rec["team"])
            if traded is not None:
                trade, tres, tcav = traded
                op.update({"type": "sign_and_trade", "team": sign_rec["team"],
                           "player": sign_rec["player"],
                           "contract": sign_rec["contract"], "trade": trade})
                caveats.extend(tcav)
                for r in (res, tres):
                    if r:
                        residues.append(r)
                if extra_legs:
                    op["additional_legs"] = []
                    for leg in extra_legs:
                        parsed_leg = _parse_trade_clause(leg, None)
                        if parsed_leg is None:
                            residues.append(leg)
                        else:
                            lt, lres, lcav = parsed_leg
                            op["additional_legs"].append(lt)
                            caveats.extend(lcav)
                            if lres:
                                residues.append(lres)
                    caveats.append("three_team_simultaneous_trade")
                if timing:
                    op["timing"] = timing
                if execute_timing:
                    op["timing"] = execute_timing
                op["parsed"] = not residues
                if residues:
                    op["residue"] = " | ".join(residues)
                if caveats:
                    op["caveats"] = sorted(set(caveats))
                return op

    if multi_sign and not extra_legs:
        first = _parse_sign_clause(multi_sign.group(1))
        team = first[0]["team"] if first else None
        second = _parse_sign_clause("Team %s %s" % (team, multi_sign.group(2))) if team else None
        if first is not None and second is not None:
            signings = []
            for rec, res in (first, second):
                signings.append({"team": rec["team"], "player": rec["player"],
                                 "contract": rec["contract"]})
                if res:
                    residues.append(res)
            op.update({"type": "multi_sign", "team": team, "signings": signings})
            op["parsed"] = not residues
            if residues:
                op["residue"] = " | ".join(residues)
            return op

    signed = _parse_sign_clause(head_body)
    if signed is not None and not extra_legs:
        sign_rec, res = signed
        op.update({"type": "sign", "team": sign_rec["team"],
                   "player": sign_rec["player"], "contract": sign_rec["contract"]})
        if res:
            residues.append(res)
        if timing:
            op["timing"] = timing
        if execute_timing:
            op["timing"] = execute_timing
        op["parsed"] = not residues
        if residues:
            op["residue"] = " | ".join(residues)
        return op

    traded = _parse_trade_clause(head_body, None)
    if traded is not None:
        trade, tres, tcav = traded
        op.update({"type": "trade", "trade": trade})
        caveats.extend(tcav)
        if tres:
            residues.append(tres)
        if extra_legs:
            op["additional_legs"] = []
            for leg in extra_legs:
                parsed_leg = _parse_trade_clause(leg, None)
                if parsed_leg is None:
                    residues.append(leg)
                else:
                    lt, lres, lcav = parsed_leg
                    op["additional_legs"].append(lt)
                    caveats.extend(lcav)
                    if lres:
                        residues.append(lres)
            caveats.append("three_team_simultaneous_trade")
        if timing:
            op["timing"] = timing
        op["parsed"] = not residues
        if residues:
            op["residue"] = " | ".join(residues)
        if caveats:
            op["caveats"] = sorted(set(caveats))
        return op

    op.update({"type": "unparsed", "parsed": False, "residue": body})
    return op


# ---------------------------------------------------------------------------
# instance assembly
# ---------------------------------------------------------------------------

def build_instance(record: Dict[str, Any], comp_file: str, index: int
                   ) -> Tuple[Dict[str, Any], List[Dict[str, str]], List[str]]:
    instance_id = "%s#%03d" % (comp_file[:-len(".json")], index)
    teams: Dict[str, Dict[str, Any]] = {}
    players: Dict[str, Dict[str, Any]] = {}
    residues: List[Dict[str, str]] = []
    caveats: List[str] = []

    for sentence in record.get("team_situations", []):
        variant = parse_team_situation(sentence, teams)
        if variant is None:
            residues.append({"instance_id": instance_id, "section": "team_situations",
                             "text": sentence, "unconsumed": normalise(sentence)})

    for sentence in record.get("player_situations", []):
        variant, residue = parse_player_situation(sentence, players)
        if variant is None or residue:
            residues.append({"instance_id": instance_id, "section": "player_situations",
                             "text": sentence, "unconsumed": residue or normalise(sentence)})

    operations = []
    for raw in record.get("operations", []):
        op = parse_operation(raw)
        operations.append(op)
        if not op.get("parsed"):
            residues.append({"instance_id": instance_id, "section": "operations",
                             "text": raw, "unconsumed": op.get("residue", "")})
        caveats.extend(op.get("caveats", []))

    # teams named only inside operations/player situations still get a slot so
    # that every referenced team is JSON-Pointer addressable.
    for letter in _referenced_teams(record):
        teams.setdefault(letter, {})
    for letter in _referenced_players(record):
        players.setdefault(letter, {})

    doc = {
        "contract_version": CONTRACT_VERSION,
        "instance_id": instance_id,
        "facts": {
            "teams": teams,
            "players": players,
            "operations": operations,
            "derived": {},
        },
        "gold": {
            "answer": record["answer"],
            "illegal_operation": record.get("illegal_operation"),
            "problematic_team": record.get("problematic_team"),
            "relevant_rules": list(record.get("relevant_rules", [])),
        },
        "provenance": {
            "source": "rulearena",
            "commit": SOURCE_COMMIT,
            "file": comp_file,
            "index": index,
            # Copied verbatim from the benchmark.  These are UNRELIABLE -- they
            # disagree with the prose in 21/216 instances (operations), 8/216
            # (teams) and 3/216 (players).  Kept for traceability only; never
            # use them to validate a parse.  See PARSE-COVERAGE.md.
            "source_declared_counts": {
                "n_teams": record.get("n_teams"),
                "n_players": record.get("n_players"),
                "n_operations": record.get("n_operations"),
            },
            "raw": {
                "team_situations": list(record.get("team_situations", [])),
                "player_situations": list(record.get("player_situations", [])),
                "operations": list(record.get("operations", [])),
            },
        },
    }
    return doc, residues, sorted(set(caveats))


def _referenced_teams(record: Dict[str, Any]) -> List[str]:
    blob = " ".join(record.get("team_situations", []) + record.get("player_situations", [])
                    + record.get("operations", []))
    return sorted(set(re.findall(r"[Tt]eam ([A-Z])\b", blob)))


def _referenced_players(record: Dict[str, Any]) -> List[str]:
    blob = " ".join(record.get("player_situations", []) + record.get("operations", []))
    return sorted(set(re.findall(r"[Pp]layer ([A-Z])\b", blob)))


# ---------------------------------------------------------------------------
# validation helpers (also used by tests)
# ---------------------------------------------------------------------------

DECIMAL_STRING_KEYS = {
    "salary", "amount", "first_year_salary", "annual_change_pct", "years",
    "pick", "age_at_draft", "own_first_round_years_ahead", "minimum_plus_amount",
    "players_signed_before_new_season", "percent_of_salary_cap",
    "stated_total_salary", "stated_total_years", "day",
}


def iter_pointers(node: Any, prefix: str = ""):
    """Yield (json_pointer, value) for every node, per RFC 6901."""
    yield prefix or "", node
    if isinstance(node, dict):
        for k, v in node.items():
            token = str(k).replace("~", "~0").replace("/", "~1")
            yield from iter_pointers(v, prefix + "/" + token)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from iter_pointers(v, prefix + "/" + str(i))


def check_decimal_strings(doc: Dict[str, Any]) -> List[str]:
    """Return pointers whose value violates the decimal-string requirement."""
    problems = []
    for ptr, value in iter_pointers(doc.get("facts", {}), "/facts"):
        key = ptr.rsplit("/", 1)[-1]
        if key in DECIMAL_STRING_KEYS and value is not None:
            if not isinstance(value, str) or not DECIMAL_RE.match(value):
                problems.append("%s = %r" % (ptr, value))
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            problems.append("%s is a JSON number (%r)" % (ptr, value))
    return problems


def dumps(doc: Dict[str, Any]) -> str:
    return json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------

def parse_checkout(checkout: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]],
                                           Dict[str, List[str]]]:
    docs: List[Dict[str, Any]] = []
    residues: List[Dict[str, str]] = []
    caveat_map: Dict[str, List[str]] = {}
    base = os.path.join(checkout, "nba", "annotated_problems")
    for comp_file in COMP_FILES:
        with open(os.path.join(base, comp_file), "r", encoding="utf-8") as fh:
            records = json.load(fh)
        for index, record in enumerate(records):
            doc, res, cav = build_instance(record, comp_file, index)
            docs.append(doc)
            residues.extend(res)
            if cav:
                caveat_map[doc["instance_id"]] = cav
    return docs, residues, caveat_map


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--checkout", required=True, help="RuleArena checkout root (read-only)")
    ap.add_argument("--out", required=True, help="output directory for facts documents")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero if any residue was recorded")
    args = ap.parse_args(argv)

    docs, residues, caveat_map = parse_checkout(args.checkout)
    os.makedirs(args.out, exist_ok=True)

    residue_by_instance: Dict[str, int] = {}
    for r in residues:
        residue_by_instance[r["instance_id"]] = residue_by_instance.get(r["instance_id"], 0) + 1

    manifest_entries = []
    schema_problems: List[str] = []
    for doc in docs:
        iid = doc["instance_id"]
        path = os.path.join(args.out, iid.replace("#", "_") + ".json")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(dumps(doc))
        schema_problems.extend("%s %s" % (iid, p) for p in check_decimal_strings(doc))
        manifest_entries.append({
            "instance_id": iid,
            "file": os.path.basename(path),
            "parsed_fully": residue_by_instance.get(iid, 0) == 0,
            "residue_count": residue_by_instance.get(iid, 0),
            "caveats": caveat_map.get(iid, []),
            "n_teams": len(doc["facts"]["teams"]),
            "n_players": len(doc["facts"]["players"]),
            "n_operations": len(doc["facts"]["operations"]),
        })

    manifest = {
        "contract_version": CONTRACT_VERSION,
        "source": {"repo": "rulearena", "commit": SOURCE_COMMIT, "slice": "nba"},
        "total_instances": len(docs),
        "fully_parsed": sum(1 for e in manifest_entries if e["parsed_fully"]),
        "instances_with_caveats": sum(1 for e in manifest_entries if e["caveats"]),
        "residue_count": len(residues),
        "residues": residues,
        "instances": manifest_entries,
    }
    with open(os.path.join(args.out, "index.json"), "w", encoding="utf-8") as fh:
        fh.write(dumps(manifest))

    total = len(docs)
    full = manifest["fully_parsed"]
    pct = (100.0 * full / total) if total else 0.0
    ops_total = sum(e["n_operations"] for e in manifest_entries)
    ops_parsed = sum(1 for d in docs for o in d["facts"]["operations"] if o.get("parsed"))

    print("=" * 72)
    print("RuleArena NBA -> facts/v1   (deterministic regex parser, no LLM)")
    print("=" * 72)
    print("instances            : %d" % total)
    print("fully parsed         : %d  (%.1f%%)" % (full, pct))
    print("with caveats         : %d  (parsed, documented ambiguity)" %
          manifest["instances_with_caveats"])
    print("residues             : %d" % len(residues))
    print("operations           : %d parsed / %d total (%.1f%%)" %
          (ops_parsed, ops_total, 100.0 * ops_parsed / ops_total if ops_total else 0.0))
    print("decimal-string issues: %d" % len(schema_problems))
    for p in schema_problems[:10]:
        print("    ! " + p)
    print("-" * 72)
    print("guaranteed fields (present whenever the source states them):")
    for line in GUARANTEED_FIELDS:
        print("    " + line)
    print("-" * 72)
    print("facts.derived is EMPTY by design; derive.py owns it.")
    print("output: %s" % os.path.abspath(args.out))
    if residues:
        print("residue detail is in index.json -> .residues")
    print("=" * 72)

    if args.strict and (residues or schema_problems):
        return 1
    return 0


GUARANTEED_FIELDS = [
    "facts.teams.<T>.salary",
    "facts.teams.<T>.draft_picks.{own_first_round_years_ahead,"
    "own_first_round_missing_years,acquired_first_round_picks[]}",
    "facts.teams.<T>.players_signed_before_new_season",
    "facts.teams.<T>.traded_player_exceptions[].{amount,cap_year}",
    "facts.teams.<T>.bi_annual_exception_used_cap_year",
    "facts.players.<P>.draft.{round,pick,team,year,age_at_draft}",
    "facts.players.<P>.contract.{years,signed_with_team,salary_kind,"
    "first_year_salary,minimum_salary_phrase,annual_change_pct,"
    "annual_change_direction,annual_change_applies_to,signed_during,options[],"
    "bi_annual_exception}",
    "facts.players.<P>.awards[].{cap_year,award}",
    "facts.players.<P>.player_option_declined / tested_free_market",
    "facts.players.<P>.transactions[].{type,from_team,to_team,"
    "counterparty_players,during}",
    "facts.operations[].{label,type,parsed,raw}",
    "facts.operations[].type in {sign,sign_and_trade,multi_sign,trade,"
    "qualifying_offer,offer_sheet,match_offer_sheet,unparsed}",
    "facts.operations[].contract.{years,salary_kind,first_year_salary,"
    "first_cap_year,annual_change_pct,annual_change_direction,"
    "annual_change_applies_to,year_salary_overrides[],percent_of_salary_cap,"
    "minimum_plus_amount,stated_total_salary}",
    "facts.operations[].trade.{from_team,to_team,sends[],receives[]} "
    "+ {third_team,receives_clause_raw,third_team_asset_binding} when 3-team",
    "facts.operations[].additional_legs[]  (three-team simultaneous trades)",
    "facts.operations[].signings[]         (multi_sign only)",
    "facts.operations[].timing.{month,day,year,raw}",
    "facts.operations[].caveats[]          (documented ambiguities; see "
    "PARSE-COVERAGE.md)",
    "facts.derived = {}   (owned by derive.py)",
]


if __name__ == "__main__":
    sys.exit(main())
