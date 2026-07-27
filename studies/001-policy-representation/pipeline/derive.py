#!/usr/bin/env python3
"""Deterministic derived-fact preprocessor for study 001 (`facts.derived`).

WHAT THIS DOES
--------------
Reads facts documents emitted by ``parse_nba.py`` (whose ``facts.derived`` is
``{}`` by construction) and fills ``facts.derived`` with the 124 fields that
``packs/nba-transaction-legality.json`` reads through ``/facts/derived/*``
pointers.  The field list, presence discipline and per-field definitions are the
contract published in ``packs/COVERAGE.md`` section 4; the arithmetic is drawn
from ``rulearena/checkout/nba/reference_rules.txt`` (the CBA excerpt) and from
the dollar stipulations that the RuleArena benchmark itself puts at the top of
every prompt (``rulearena/checkout/nba/auto_test.py``, ``prompt_template``).

The same enriched document is handed to all three arms, so no arm gets an
arithmetic advantage.  This is the study's disclosed scope limit: JPS 0.1.0-draft
compares facts, it does not compute them, so every quantity a rule must
order-compare is computed here, once, in the open.

WHY THIS FILE IS ALSO A FINDING
-------------------------------
Section 4 of ``COVERAGE.md`` asks for more than arithmetic.  Fields such as
``uses-non-taxpayer-mid-level-exception`` require deciding *which Salary Cap
Exception a transaction invokes*, and RuleArena's prose never states one.  That
decision is legal characterisation, not computation, and it is performed here by
an explicit, numbered waterfall (see ``READINGS`` below and ``DERIVED.md``).
Arm B's behaviour is therefore partly determined by this file; that is reported
rather than hidden.

WHAT THIS DELIBERATELY DOES NOT DO
----------------------------------
* It does not invent unavailable constants.  The Minimum Player Salary /
  Minimum Annual Salary schedule is not in the CBA excerpt and is not in the
  benchmark's stipulation block, so every quantity that needs it is **omitted**,
  which makes the reading rule ``unknown`` and escalates.  ``DERIVED.md`` lists
  each such field.
* It does not decide legality.  It emits no verdict, never reads ``gold``, and
  its output is identical for the answerable and redacted twins of an instance
  except where the deleted fact actually feeds a computation.
* It does not repair the parser's two documented ambiguities (unstated trade
  destination; unresolved three-team asset binding).  Quantities that depend on
  them are omitted, which escalates.
* It does not mutate anything other than ``facts.derived``.  Adding a top-level
  member would change what ``redact.py``'s render policy has to exclude.

WHERE THIS SITS IN THE PIPELINE -- IT RUNS TWICE, ON PURPOSE
------------------------------------------------------------
::

    parse_nba.py  ->  out/facts            (facts.derived == {})
    derive.py     ->  out/facts            pass 1
    redact.py     ->  out/twins            deletes one raw fact per redacted twin
    derive.py     ->  out/twins            pass 2, per twin

Pass 1 exists because ``redact.py``'s guard G4 needs a populated
``facts.derived`` to notice that a published derived quantity already supersedes
the raw fact it is about to delete.

**Pass 2 is not optional.**  The pack reads ``/facts/derived/*`` and nothing
else.  If ``facts.derived`` is carried over from the answerable document, then
deleting a raw fact changes nothing the pack can see, both twins evaluate
identically, and arm B's escalation measurement is meaningless.  Recomputing per
twin makes the deletion bite: the quantity that depended on the deleted fact
becomes uncomputable, the field is omitted, the rule reading it is ``unknown``,
and the instance escalates -- which is the behaviour the study is measuring.

CLI
---
    python derive.py [--facts DIR] [--out DIR] [--report FILE] [--strict]

``--facts`` and ``--out`` both default to ``pipeline/out/facts``: the normal
pipeline rewrites the parser's output in place.  The transform is idempotent --
any pre-existing ``facts.derived`` is discarded and recomputed -- so running it
twice is a no-op and two runs are byte-identical.  ``index.json`` and
``manifest.json`` are passed through untouched.

Python 3.10+, standard library only, no network.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal, ROUND_HALF_EVEN, getcontext
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

getcontext().prec = 40

CONTRACT_VERSION = "facts/v1"

# --------------------------------------------------------------------------- #
# 1. Constants
# --------------------------------------------------------------------------- #
# BENCHMARK STIPULATIONS.  Quoted verbatim from the assumption block that
# RuleArena prepends to every NBA prompt (nba/auto_test.py, prompt_template).
# These are dollar values the CBA excerpt does not contain; the benchmark
# supplies them to the model, so the preprocessor is entitled to them too.
CAP_2023_24 = Decimal("136000000")          # "Salary Cap for the prior (2023-24) ... $136,000,000"
AVG_PLAYER_SALARY_2023_24 = Decimal("9700000")   # "Average Player Salary for the prior ... $9,700,000"
CAP = Decimal("140588000")                  # "Salary Cap for the current (2024-25) ... $140,588,000"
LUXURY_TAX = Decimal("170814000")           # "Luxury Tax is $170,814,000"
FIRST_APRON = Decimal("178132000")          # "First Apron Level is $178,132,000"
SECOND_APRON = Decimal("188931000")         # "Second Apron Level is $188,931,000"

# The current Salary Cap Year under test.  Every operation in the corpus is
# stated to occur in, or immediately before, 2024-25.
CURRENT_YEAR = 2024

# CBA-DERIVED EXCEPTION AMOUNTS.  Each is a percentage or formula stated in the
# excerpt, applied to the stipulated Salary Cap above.
NTMLE_AMOUNT = (Decimal("9.12") / 100) * CAP        # Art. VII 6(e)(1): 9.12% of the Cap
BAE_AMOUNT = (Decimal("3.32") / 100) * CAP          # Art. VII 6(d)(1): 3.32% of the Cap
ROOM_MLE_AMOUNT = (Decimal("5.678") / 100) * CAP    # Art. VII 6(g)(1): 5.678% of the Cap
TMLE_AMOUNT = Decimal("5000000") * (CAP / CAP_2023_24)  # Art. VII 6(f)(1) table
TPE_ALLOWANCE = Decimal("250000")                   # Art. VII 6(j)(1)(i)-(v)

# UNAVAILABLE CONSTANTS.  Named here so the gaps are greppable; see DERIVED.md.
MINIMUM_PLAYER_SALARY = None      # Art. II 6 scale: not in the excerpt, not stipulated.
MINIMUM_ANNUAL_SALARY = None      # Same.
ESTIMATED_AVERAGE_PLAYER_SALARY = AVG_PLAYER_SALARY_2023_24  # 4(d)(1) uses the prior year's figure.

# Maximum Annual Salary percentages, Art. II 7(a).
MAX_PCT_UNDER_7 = Decimal("0.25")
MAX_PCT_7_TO_9 = Decimal("0.30")
MAX_PCT_10_PLUS = Decimal("0.35")
MAX_PCT_5TH_YEAR_HIGHER = Decimal("0.30")
MAX_PCT_DESIGNATED_VETERAN = Decimal("0.35")
MAX_PRIOR_SALARY_MULTIPLE = Decimal("1.05")   # 105% limb of 7(a)(i)-(iii)

# Free Agent Amount multipliers, Art. VII 4(d)(1)-(3).
HOLD_QVFA = Decimal("1.50")
HOLD_QVFA_BELOW_AVG = Decimal("1.90")
HOLD_EQVFA = Decimal("1.30")
HOLD_NQVFA = Decimal("1.20")

# Veteran Free Agent Exception limbs, Art. VII 6(b).
EQVFA_PRIOR_MULTIPLE = Decimal("1.75")        # 6(b)(3)(i)(A)
EQVFA_AVG_MULTIPLE = Decimal("1.05")          # 6(b)(3)(i)(B)
NQVFA_PRIOR_MULTIPLE = Decimal("1.20")        # 6(b)(2)(i)

# Higher Max Criteria awards, Art. II 7(a)(i)(A)-(B).  All-Defensive selections
# are deliberately absent: the criterion is Defensive Player of the Year.
HIGHER_MAX_AWARDS = frozenset({
    "all_nba_first_team", "all_nba_second_team", "all_nba_third_team",
    "defensive_player_of_the_year", "mvp",
})
MVP_AWARDS = frozenset({"mvp"})

# Transaction Restrictions Table rows A-F (Art. VII 2(e)(4)), used by the
# 2(e)(2)(iii)(B) "already used the Taxpayer MLE" test.
ROW_A_TO_F_EXCEPTIONS = frozenset({
    "bi_annual", "non_taxpayer_mid_level", "sign_and_trade_acquisition",
    "expanded_tpe", "standard_tpe",
})

FREE_AGENCY_ORDER = {"non_qualifying": 0, "early_qualifying": 1, "qualifying": 2}

# Aggregation window, Art. VII 6(j)(4)(ii): December 15 through the trade
# deadline.  The corpus states dates only as (month, year); the deadline for
# 2024-25 falls in February, so December/January/early-February are inside.
INSIDE_AGGREGATION_WINDOW_MONTHS = {"dec", "december", "jan", "january"}

READINGS = """\
R1  Years of Service = 2024 - draft year (seasons completed through 2023-24).
R2  A player's age during 2024-25 = age at draft + (2024 - draft year).
R3  Annual increases are linear on the first-year Salary, per Art. VII 5(a)
    ("... by no more than N% of the Salary for the first Salary Cap Year").
R4  Free-agency class is read off the prior Contract's coverage of the three
    preceding Seasons: 3+ -> Qualifying, 2 -> Early Qualifying, 1 -> Non-
    Qualifying.  A stated trade changes the Prior Team but not the class
    (Art. I (t), (yy) both permit changing Teams by trade).
R5  Exception selection for a signing, in order: (a) the player's Prior Team
    re-signing its own Veteran Free Agent claims the lowest Veteran Free Agent
    Exception tier whose 6(b) limb covers the stated first-year amount; (b) a
    Contract stated at the minimum uses the Minimum Player Salary Exception;
    (c) a team with Room covering the amount uses Room, not an Exception;
    (d) a team below the Cap with insufficient Room uses the Room Mid-Level;
    (e) a team above the First Apron uses the Taxpayer Mid-Level; (f) otherwise
    the Non-Taxpayer Mid-Level.  The Bi-annual Exception is claimed only where
    the facts say so explicitly.
R6  A transaction counts as "without an Exception" when no tier in R5 can
    accommodate it: the acquiring team is at or above the Cap, the player is not
    its own free agent, the Contract is not at the minimum, and the amount
    exceeds the applicable Mid-Level limit.
R7  Traded Player Exception variant, per acquiring team: Room TPE if the team is
    below the Cap and incoming fits Room + $250,000; Aggregated Standard if it
    sends two or more players; Expanded if incoming exceeds 100% of outgoing
    plus $250,000; otherwise Standard.
R8  A team carries a Free Agent Amount hold for each of its own Veteran Free
    Agents named in the instance who is not signed by anyone in the instance's
    operations (Art. VII 4(d)).
R9  Where a trade's destination team is not stated, or a three-team asset
    binding is unresolved, every quantity that depends on it is omitted.
R10 An operation with no stated date occurs in the 2024 offseason, which is
    outside the December 15-to-deadline aggregation window.
"""


# --------------------------------------------------------------------------- #
# 2. Small helpers
# --------------------------------------------------------------------------- #
def dec_str(x: Decimal) -> str:
    """Render a Decimal in the JPS 2.2 decimal grammar -?(0|[1-9][0-9]*)(\\.[0-9]+)?."""
    q = x.quantize(Decimal("0.000000000001"), rounding=ROUND_HALF_EVEN)
    s = format(q, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    if s in ("", "-", "-0"):
        s = "0"
    if s.startswith("-0") and not s.startswith("-0."):
        s = "-" + s[2:].lstrip("0") or "0"
    return s


_DEC_RE = re.compile(r"-?(0|[1-9][0-9]*)(\.[0-9]+)?\Z")


def is_jps_decimal(s: Any) -> bool:
    return isinstance(s, str) and bool(_DEC_RE.match(s))


def D(v: Any) -> Optional[Decimal]:
    """Parse a facts-document decimal string.  ``None`` when absent or unusable."""
    if v is None:
        return None
    if isinstance(v, Decimal):
        return v
    if isinstance(v, str) and _DEC_RE.match(v):
        return Decimal(v)
    return None


def ratio(num: Optional[Decimal], den: Optional[Decimal]) -> Optional[Decimal]:
    if num is None or den is None or den == 0:
        return None
    return num / den


def year_of(cap_year: Optional[str]) -> Optional[int]:
    """'2024-2025' / '2024-25' -> 2024."""
    if not isinstance(cap_year, str):
        return None
    m = re.match(r"(\d{4})", cap_year)
    return int(m.group(1)) if m else None


def maxopt(values: Iterable[Optional[Decimal]]) -> Optional[Decimal]:
    """Maximum, or ``None`` if any contributor is unknown (an unknown could be the max)."""
    vals = list(values)
    if not vals or any(v is None for v in vals):
        return None
    return max(v for v in vals if v is not None)  # type: ignore[misc]


def minopt(values: Iterable[Optional[Decimal]]) -> Optional[Decimal]:
    vals = list(values)
    if not vals or any(v is None for v in vals):
        return None
    return min(v for v in vals if v is not None)  # type: ignore[misc]


def sumopt(values: Iterable[Optional[Decimal]]) -> Optional[Decimal]:
    total = Decimal(0)
    for v in values:
        if v is None:
            return None
        total += v
    return total


# --------------------------------------------------------------------------- #
# 3. Contract salary schedules
# --------------------------------------------------------------------------- #
def contract_seasons(c: Dict[str, Any]) -> Optional[int]:
    for key in ("years", "stated_total_years"):
        v = c.get(key)
        if isinstance(v, str) and v.isdigit():
            return int(v)
    ovr = c.get("year_salary_overrides") or []
    numeric = [int(o["which_year"]) for o in ovr
               if isinstance(o.get("which_year"), str) and o["which_year"].isdigit()]
    return max(numeric) if numeric else None


def contract_first_year_amount(c: Dict[str, Any]) -> Optional[Decimal]:
    """First-Salary-Cap-Year Salary plus Unlikely Bonuses.  ``None`` when unavailable."""
    kind = c.get("salary_kind")
    if kind == "explicit":
        return D(c.get("first_year_salary"))
    if kind == "percent_of_salary_cap":
        pct = D(c.get("percent_of_salary_cap"))
        return None if pct is None else (pct / 100) * CAP
    if kind == "non_taxpayer_mid_level_exception":
        return NTMLE_AMOUNT
    if kind == "minimum":
        # Minimum Player Salary is not supplied by the CBA excerpt or by the
        # benchmark's stipulation block.  See DERIVED.md, gap G-MIN.
        return None
    return D(c.get("first_year_salary"))


def contract_schedule(c: Dict[str, Any]) -> Optional[List[Decimal]]:
    """Per-Season Salaries for a Contract, or ``None`` if any Season is unknown."""
    n = contract_seasons(c)
    if not n or n <= 0:
        return None
    base = contract_first_year_amount(c)
    pct = D(c.get("annual_change_pct"))
    direction = c.get("annual_change_direction")
    applies = c.get("annual_change_applies_to")
    sched: List[Optional[Decimal]] = [None] * n

    if base is not None:
        sign = Decimal(-1) if direction == "decrease" else Decimal(1)
        step = (pct / 100) * base * sign if pct is not None else Decimal(0)
        if c.get("percent_applies_to_first_two_cap_years"):
            # "9.12% x Salary Cap in the first two Salary Cap Years"
            for k in range(min(2, n)):
                sched[k] = base
        elif applies == "first_two_salary_cap_years":
            for k in range(min(2, n)):
                sched[k] = base + step * k
        else:
            for k in range(n):
                sched[k] = base + step * k

    for o in c.get("year_salary_overrides") or []:
        which = o.get("which_year")
        idx: Optional[int]
        if which == "last":
            idx = n - 1
        elif isinstance(which, str) and which.isdigit():
            idx = int(which) - 1
        else:
            idx = None
        if idx is not None and 0 <= idx < n:
            sched[idx] = D(o.get("salary"))

    if any(s is None for s in sched):
        return None
    return [s for s in sched if s is not None]


# --------------------------------------------------------------------------- #
# 4. Player view
# --------------------------------------------------------------------------- #
class PlayerView:
    """Everything the derivations need about one player, computed once."""

    __slots__ = (
        "label", "raw", "draft_year", "draft_round", "draft_team", "yos", "age",
        "prior_team", "prior_first_year", "prior_seasons", "prior_schedule",
        "prior_salary", "current_salary", "under_contract", "fa_class",
        "higher_max", "minimum_contract", "has_option",
    )

    def __init__(self, label: str, raw: Dict[str, Any]) -> None:
        self.label = label
        self.raw = raw
        draft = raw.get("draft") or {}
        dy = draft.get("year")
        self.draft_year = int(dy) if isinstance(dy, str) and dy.isdigit() else None
        self.draft_round = draft.get("round")
        self.draft_team = draft.get("team")
        age_at_draft = draft.get("age_at_draft")

        # R1 / R2
        self.yos = (CURRENT_YEAR - self.draft_year) if self.draft_year is not None else None
        self.age = (
            int(age_at_draft) + (CURRENT_YEAR - self.draft_year)
            if isinstance(age_at_draft, str) and age_at_draft.isdigit()
            and self.draft_year is not None else None
        )

        c = raw.get("contract") or {}
        self.minimum_contract = c.get("salary_kind") == "minimum"
        self.has_option = bool(c.get("options"))
        signed = c.get("signed_during") or {}
        sy = signed.get("year")
        self.prior_first_year = int(sy) if isinstance(sy, str) and sy.isdigit() else None
        self.prior_seasons = contract_seasons(c)
        self.prior_schedule = contract_schedule(c)

        # Prior Team: the team he last played for.  A stated trade moves him.
        team = c.get("signed_with_team")
        for tx in raw.get("transactions") or []:
            if tx.get("type") == "traded" and tx.get("to_team"):
                team = tx["to_team"]
        self.prior_team = team

        last_covered = (
            self.prior_first_year + self.prior_seasons - 1
            if self.prior_first_year is not None and self.prior_seasons else None
        )
        self.under_contract = (last_covered is not None and last_covered >= CURRENT_YEAR)

        self.prior_salary = None
        self.current_salary = None
        if self.prior_schedule and self.prior_seasons:
            self.prior_salary = self.prior_schedule[self.prior_seasons - 1]
            if self.under_contract and self.prior_first_year is not None:
                k = CURRENT_YEAR - self.prior_first_year
                if 0 <= k < len(self.prior_schedule):
                    self.current_salary = self.prior_schedule[k]

        # R4: free-agency class, only meaningful for a player out of contract.
        self.fa_class = None
        if not self.under_contract and self.prior_first_year is not None and self.prior_seasons:
            covered = sum(
                1 for y in (CURRENT_YEAR - 3, CURRENT_YEAR - 2, CURRENT_YEAR - 1)
                if self.prior_first_year <= y <= self.prior_first_year + self.prior_seasons - 1
            )
            if covered >= 3:
                self.fa_class = "qualifying"
            elif covered == 2:
                self.fa_class = "early_qualifying"
            elif covered == 1:
                self.fa_class = "non_qualifying"

        self.higher_max = self._higher_max(raw.get("awards") or [])

    @staticmethod
    def _higher_max(awards: Sequence[Dict[str, Any]]) -> bool:
        """Art. II 7(a)(i)(A)-(B), evaluated over the three preceding Seasons."""
        recent = {CURRENT_YEAR - 1: "2023-24", CURRENT_YEAR - 2: "2022-23", CURRENT_YEAR - 3: "2021-22"}
        hits: Dict[int, List[str]] = {y: [] for y in recent}
        for a in awards:
            name = a.get("award")
            cy = year_of(a.get("cap_year"))
            if name in HIGHER_MAX_AWARDS and cy in hits:
                hits[cy].append(name)
        if hits.get(CURRENT_YEAR - 1):
            return True                                  # immediately preceding Season
        if sum(1 for y in hits if hits[y]) >= 2:
            return True                                  # two of the preceding three
        for y in hits:
            if any(n in MVP_AWARDS for n in hits[y]):
                return True                              # MVP in one of the preceding three
        return False

    def max_annual_salary(self) -> Optional[Decimal]:
        """Maximum Annual Salary under Art. II 7(a) for this player."""
        if self.yos is None:
            return None
        if self.yos < 7:
            pct = MAX_PCT_5TH_YEAR_HIGHER if (self.yos == 4 and self.higher_max) else MAX_PCT_UNDER_7
        elif self.yos < 10:
            pct = MAX_PCT_7_TO_9
        else:
            pct = MAX_PCT_10_PLUS
        cap_limb = pct * CAP
        if self.prior_salary is None:
            return cap_limb
        return max(cap_limb, MAX_PRIOR_SALARY_MULTIPLE * self.prior_salary)

    def free_agent_amount(self) -> Optional[Decimal]:
        """Free Agent Amount (cap hold), Art. VII 4(d)(1)-(3)."""
        if self.fa_class is None or self.prior_salary is None:
            return None
        if self.fa_class == "qualifying":
            mult = (HOLD_QVFA if self.prior_salary >= ESTIMATED_AVERAGE_PLAYER_SALARY
                    else HOLD_QVFA_BELOW_AVG)
        elif self.fa_class == "early_qualifying":
            mult = HOLD_EQVFA
        else:
            mult = HOLD_NQVFA
        return mult * self.prior_salary


# --------------------------------------------------------------------------- #
# 5. Normalised events
# --------------------------------------------------------------------------- #
class Signing:
    """One new Player Contract or Offer Sheet proposed by an operation."""

    __slots__ = ("op_index", "label", "team", "player", "contract", "kind",
                 "schedule", "amount", "seasons", "exception", "claimed_tier")

    def __init__(self, op_index: int, label: str, team: Optional[str],
                 player: Optional[str], contract: Dict[str, Any], kind: str) -> None:
        self.op_index = op_index
        self.label = label
        self.team = team
        self.player = player
        self.contract = contract
        self.kind = kind                    # sign | sign_and_trade | offer_sheet
        self.schedule = contract_schedule(contract)
        self.amount = contract_first_year_amount(contract)
        self.seasons = contract_seasons(contract)
        self.exception: Optional[str] = None
        self.claimed_tier: Optional[str] = None


class TradeLeg:
    """One team's side of one trade operation."""

    __slots__ = ("op_index", "label", "team", "incoming_players", "outgoing_players",
                 "cash_in", "cash_out", "picks_in", "picks_out", "sign_and_trade",
                 "signed_player", "unresolved")

    def __init__(self, op_index: int, label: str, team: Optional[str]) -> None:
        self.op_index = op_index
        self.label = label
        self.team = team
        self.incoming_players: List[str] = []
        self.outgoing_players: List[str] = []
        self.cash_in = Decimal(0)
        self.cash_out = Decimal(0)
        self.picks_in: List[Dict[str, Any]] = []
        self.picks_out: List[Dict[str, Any]] = []
        self.sign_and_trade = False
        self.signed_player: Optional[str] = None
        self.unresolved = False


def collect_signings(ops: Sequence[Dict[str, Any]]) -> List[Signing]:
    out: List[Signing] = []
    for i, op in enumerate(ops):
        t = op.get("type")
        if t in ("sign", "sign_and_trade", "offer_sheet") and op.get("contract"):
            out.append(Signing(i, op.get("label", "?"), op.get("team"),
                               op.get("player"), op["contract"], t))
        elif t == "multi_sign":
            for s in op.get("signings") or []:
                if s.get("contract"):
                    out.append(Signing(i, op.get("label", "?"), s.get("team") or op.get("team"),
                                       s.get("player"), s["contract"], "sign"))
    return out


def collect_trade_legs(ops: Sequence[Dict[str, Any]]) -> List[TradeLeg]:
    """One leg per (operation, team).  R9: an unstated destination marks the leg unresolved."""
    legs: List[TradeLeg] = []
    for i, op in enumerate(ops):
        tr = op.get("trade")
        if not tr:
            continue
        frm, to = tr.get("from_team"), tr.get("to_team")
        unresolved = (to is None) or (tr.get("third_team_asset_binding") == "unresolved")
        a = TradeLeg(i, op.get("label", "?"), frm)
        b = TradeLeg(i, op.get("label", "?"), to)
        a.unresolved = b.unresolved = unresolved
        if op.get("type") == "sign_and_trade":
            a.sign_and_trade = b.sign_and_trade = True
            a.signed_player = b.signed_player = op.get("player")
        for asset in tr.get("sends") or []:
            _place(asset, out_leg=a, in_leg=b)
        for asset in tr.get("receives") or []:
            _place(asset, out_leg=b, in_leg=a)
        legs.append(a)
        legs.append(b)
    return legs


def _place(asset: Dict[str, Any], out_leg: TradeLeg, in_leg: TradeLeg) -> None:
    kind = asset.get("kind")
    if kind == "player" and asset.get("player"):
        out_leg.outgoing_players.append(asset["player"])
        in_leg.incoming_players.append(asset["player"])
    elif kind == "cash":
        amt = D(asset.get("amount")) or Decimal(0)
        out_leg.cash_out += amt
        in_leg.cash_in += amt
    elif kind == "draft_pick":
        out_leg.picks_out.append(asset)
        in_leg.picks_in.append(asset)


# --------------------------------------------------------------------------- #
# 6. The derivation
# --------------------------------------------------------------------------- #
class Derivation:
    def __init__(self, doc: Dict[str, Any]) -> None:
        self.doc = doc
        self.instance_id = doc.get("instance_id", "?")
        facts = doc.get("facts") or {}
        self.teams_raw: Dict[str, Any] = facts.get("teams") or {}
        self.ops: List[Dict[str, Any]] = facts.get("operations") or []
        self.players = {k: PlayerView(k, v) for k, v in (facts.get("players") or {}).items()}
        self.signings = collect_signings(self.ops)
        self.legs = collect_trade_legs(self.ops)
        self.pre: Dict[str, Optional[Decimal]] = {
            t: D((v or {}).get("salary")) for t, v in self.teams_raw.items()
        }
        self.notes: List[str] = []
        self.d: Dict[str, Any] = {}

    # ---- emission helpers -------------------------------------------------
    def b(self, name: str, value: bool) -> None:
        self.d[name] = bool(value)

    def n(self, name: str, value: Optional[Decimal]) -> None:
        """Emit a decimal string, or omit (-> unknown -> escalate) when unavailable."""
        if value is None:
            self.notes.append(name)
            return
        self.d[name] = dec_str(value)

    def i(self, name: str, value: Optional[int]) -> None:
        if value is None:
            self.notes.append(name)
            return
        self.d[name] = dec_str(Decimal(value))

    # ---- team-salary machinery -------------------------------------------
    def room(self, team: Optional[str]) -> Optional[Decimal]:
        pre = self.pre.get(team) if team else None
        return None if pre is None else CAP - pre

    def signed_players(self) -> set:
        return {s.player for s in self.signings if s.player and s.kind != "offer_sheet"}

    def holds(self) -> Dict[str, List[Tuple[str, Decimal]]]:
        """R8.  team -> [(player, Free Agent Amount)] for unsigned own free agents."""
        signed = self.signed_players()
        out: Dict[str, List[Tuple[str, Decimal]]] = {}
        for label, p in sorted(self.players.items()):
            if p.under_contract or p.fa_class is None or p.prior_team is None:
                continue
            if label in signed:
                continue
            amt = p.free_agent_amount()
            if amt is None:
                continue
            out.setdefault(p.prior_team, []).append((label, amt))
        return out

    def post_salaries(self, exclude_hold_classes: Sequence[str] = (),
                      include_holds: bool = True,
                      over38_reattribution: bool = False) -> Dict[str, Optional[Decimal]]:
        """Team Salary immediately after all operations, per team."""
        out: Dict[str, Optional[Decimal]] = dict(self.pre)

        def bump(team: Optional[str], delta: Optional[Decimal]) -> None:
            if team is None:
                return
            if team not in out:
                out[team] = None
                return
            if out[team] is None:
                return
            if delta is None:
                out[team] = None
                return
            out[team] = out[team] + delta  # type: ignore[operator]

        for s in self.signings:
            if s.kind == "offer_sheet":
                continue                      # not yet a Contract on anyone's books
            amt = s.amount
            if over38_reattribution and s.schedule is not None:
                amt = over38_first_year_after_reattribution(s, self.players.get(s.player or ""))
            bump(s.team, amt)

        for leg in self.legs:
            if leg.team is None:
                continue
            if leg.unresolved:
                out[leg.team] = None
                continue
            for p in leg.incoming_players:
                bump(leg.team, self.moving_salary(p))
            for p in leg.outgoing_players:
                sal = self.moving_salary(p)
                bump(leg.team, None if sal is None else -sal)

        if include_holds:
            for team, hs in self.holds().items():
                for label, amt in hs:
                    cls = self.players[label].fa_class
                    if cls in exclude_hold_classes:
                        continue
                    bump(team, amt)
        return out

    def moving_salary(self, player: Optional[str]) -> Optional[Decimal]:
        """Salary that travels with a player in a trade: his new Contract if he was
        just signed and traded, otherwise his 2024-25 Salary."""
        if not player:
            return None
        for s in self.signings:
            if s.player == player and s.kind == "sign_and_trade":
                return s.amount
        p = self.players.get(player)
        if p is None:
            return None
        return p.current_salary

    # ---- exception selection (R5/R6) -------------------------------------
    def assign_exceptions(self) -> None:
        for s in self.signings:
            p = self.players.get(s.player or "")
            team = s.team
            amt = s.amount
            pre = self.pre.get(team) if team else None
            room = self.room(team)

            if s.contract.get("bi_annual_exception") or (
                    team and (self.teams_raw.get(team) or {}).get("bi_annual_exception_used_cap_year")):
                s.exception = "bi_annual"
                continue

            # Art. VII 6(i) is available to any Team for any player, including a
            # Team's own free agent, so it is tested before the 6(b) tiers.
            if s.contract.get("salary_kind") == "minimum":
                s.exception = "minimum_player_salary"
                continue

            own_free_agent = (
                p is not None and not p.under_contract and p.fa_class is not None
                and p.prior_team == team and s.kind != "offer_sheet"
            )

            if own_free_agent and (room is None or amt is None or room < amt):
                tier = self.claimed_veteran_tier(p, amt)  # type: ignore[arg-type]
                s.claimed_tier = tier
                s.exception = {
                    "qualifying": "qualifying_veteran_free_agent",
                    "early_qualifying": "early_qualifying_veteran_free_agent",
                    "non_qualifying": "non_qualifying_veteran_free_agent",
                }[tier]
                continue

            if s.kind == "offer_sheet":
                # An Offer Sheet is not yet an Exception use; Art. XI 5(d) governs it.
                continue

            if room is not None and amt is not None and room >= amt:
                s.exception = "room"          # Art. VII 2(b)(2): acting with Room
                continue

            if pre is not None and pre < CAP:
                s.exception = "room_mid_level"
            elif pre is not None and pre > FIRST_APRON:
                s.exception = "taxpayer_mid_level"
            else:
                s.exception = "non_taxpayer_mid_level"

    @staticmethod
    def claimed_veteran_tier(p: PlayerView, amt: Optional[Decimal]) -> str:
        """R5(a): the lowest 6(b) tier whose limb covers the stated amount."""
        if amt is None:
            return p.fa_class or "qualifying"
        if p.prior_salary is not None and amt <= NQVFA_PRIOR_MULTIPLE * p.prior_salary:
            return "non_qualifying"
        early_limb = EQVFA_AVG_MULTIPLE * AVG_PLAYER_SALARY_2023_24
        if p.prior_salary is not None:
            early_limb = max(early_limb, EQVFA_PRIOR_MULTIPLE * p.prior_salary)
        if amt <= early_limb:
            return "early_qualifying"
        return "qualifying"

    def exception_limit(self, name: Optional[str]) -> Optional[Decimal]:
        return {
            "non_taxpayer_mid_level": NTMLE_AMOUNT,
            "taxpayer_mid_level": TMLE_AMOUNT,
            "room_mid_level": ROOM_MLE_AMOUNT,
            "bi_annual": BAE_AMOUNT,
        }.get(name or "")

    def without_exception_teams(self) -> List[str]:
        """R6."""
        teams: List[str] = []
        for s in self.signings:
            if s.kind == "offer_sheet" or s.team is None:
                continue
            limit = self.exception_limit(s.exception)
            if limit is None or s.amount is None:
                continue
            if s.amount > limit and s.team not in teams:
                teams.append(s.team)
        return teams

    def uses(self, name: str) -> bool:
        return any(s.exception == name for s in self.signings)

    def signings_using(self, name: str) -> List[Signing]:
        return [s for s in self.signings if s.exception == name]

    def teams_using(self, name: str) -> List[str]:
        seen: List[str] = []
        for s in self.signings_using(name):
            if s.team and s.team not in seen:
                seen.append(s.team)
        return seen

    # ---- traded player exceptions (R7) ------------------------------------
    def tpe_legs(self) -> List[Tuple[TradeLeg, str, Optional[Decimal], Optional[Decimal]]]:
        """(leg, variant, incoming, outgoing) for every acquiring leg that needs a TPE."""
        out = []
        for leg in self.legs:
            if leg.team is None or leg.unresolved or not leg.incoming_players:
                continue
            pre = self.pre.get(leg.team)
            incoming = sumopt(self.moving_salary(p) for p in leg.incoming_players)
            outgoing = sumopt(self.moving_salary(p) for p in leg.outgoing_players)
            room = None if pre is None else CAP - pre
            if room is not None and room > 0 and incoming is not None and incoming <= room + TPE_ALLOWANCE:
                variant = "room_tpe"
            elif len(leg.outgoing_players) >= 2:
                variant = "aggregated_tpe"
            elif (incoming is not None and outgoing is not None
                  and incoming > outgoing + TPE_ALLOWANCE):
                variant = "expanded_tpe"
            else:
                variant = "standard_tpe"
            out.append((leg, variant, incoming, outgoing))
        return out

    # ---- main -------------------------------------------------------------
    def run(self) -> Dict[str, Any]:
        self.assign_exceptions()
        post = self.post_salaries()
        post_no_holds = self.post_salaries(include_holds=False)
        tpes = self.tpe_legs()
        holds = self.holds()

        def post_of(team: Optional[str]) -> Optional[Decimal]:
            return post.get(team) if team else None

        # -- 4.1 always-present booleans (39) -------------------------------
        self.b("contains-provision-outside-pack-scope",
               any(op.get("parsed") is False or op.get("type") == "unparsed" for op in self.ops))

        we_teams = self.without_exception_teams()
        self.b("any-transaction-without-exception", bool(we_teams))

        for flag, name in (
            ("uses-qualifying-veteran-free-agent-exception", "qualifying_veteran_free_agent"),
            ("uses-early-qualifying-veteran-free-agent-exception", "early_qualifying_veteran_free_agent"),
            ("uses-non-qualifying-veteran-free-agent-exception", "non_qualifying_veteran_free_agent"),
            ("uses-non-taxpayer-mid-level-exception", "non_taxpayer_mid_level"),
            ("uses-taxpayer-mid-level-exception", "taxpayer_mid_level"),
            ("uses-bi-annual-exception", "bi_annual"),
            ("uses-room-mid-level-exception", "room_mid_level"),
            ("uses-minimum-player-salary-exception", "minimum_player_salary"),
        ):
            self.b(flag, self.uses(name))

        variants = {v for _, v, _, _ in tpes}
        self.b("uses-standard-traded-player-exception", "standard_tpe" in variants)
        self.b("uses-aggregated-standard-traded-player-exception", "aggregated_tpe" in variants)
        self.b("uses-expanded-traded-player-exception", "expanded_tpe" in variants)
        self.b("uses-room-traded-player-exception", "room_tpe" in variants)
        self.b("uses-any-traded-player-exception", bool(variants))

        st_signings = [s for s in self.signings if s.kind == "sign_and_trade"]
        includes_st = bool(st_signings)
        self.b("includes-sign-and-trade", includes_st)
        self.b("acquires-player-under-sign-and-trade-contract", includes_st)
        # Row J: the assignor holds a TPE in respect of the signed-and-traded
        # Contract and uses it to acquire a player in the same operation.
        self.b("uses-traded-player-exception-for-signed-and-traded-contract",
               any(leg.sign_and_trade and leg.incoming_players and not leg.unresolved
                   and leg.team is not None
                   and any(s.team == leg.team for s in st_signings)
                   for leg in self.legs))

        cash_legs = [l for l in self.legs if l.cash_in or l.cash_out]
        self.b("includes-cash-in-trade", bool(cash_legs))
        self.b("pays-cash-in-trade", any(l.cash_out for l in self.legs))

        pick_legs = [l for l in self.legs
                     if any(a.get("round") == "1" for a in l.picks_in + l.picks_out)]
        self.b("includes-first-round-pick-trade", bool(pick_legs))

        traded_recent = self.recently_signed_traded()
        self.b("includes-trade-of-recently-signed-free-agent-contract", bool(traded_recent))

        tiers = self.service_tiers()
        self.b("has-new-contract-service-under-7", bool(tiers["under_7"]))
        self.b("has-new-contract-service-7-to-9", bool(tiers["7_to_9"]))
        self.b("has-new-contract-service-10-or-more", bool(tiers["10_plus"]))
        self.b("has-fifth-year-eligible-contract", bool(tiers["fifth_year"]))
        self.b("has-designated-veteran-player-contract", bool(tiers["designated"]))

        qvfa_prior = [s for s in self.signings if self.is_qvfa_prior_team(s)]
        standard_len = [s for s in self.signings if s.kind != "offer_sheet" and s not in qvfa_prior]
        self.b("has-standard-length-new-contract", bool(standard_len))
        self.b("has-qualifying-veteran-free-agent-prior-team-contract", bool(qvfa_prior))

        five_pct, eight_pct = self.change_groups()
        self.b("has-contract-governed-by-5-percent-limit", bool(five_pct))
        self.b("has-contract-governed-by-8-percent-limit", bool(eight_pct))

        over38 = [s for s in self.signings if self.is_over_38(s)]
        self.b("over-38-contract-present", bool(over38))
        o38_qvfa = [s for s in over38 if s.seasons == 5 and self.is_qvfa_prior_team(s)
                    and (self.players.get(s.player or "") is not None)
                    and (self.players[s.player].age in (34, 35, 36))]  # type: ignore[index]
        self.b("over-38-qualifying-veteran-free-agent-age-35-or-36-five-seasons", bool(o38_qvfa))

        hold_classes = {self.players[l].fa_class for hs in holds.values() for l, _ in hs}
        self.b("qualifying-veteran-free-agent-hold-included", "qualifying" in hold_classes)
        self.b("early-qualifying-veteran-free-agent-hold-included", "early_qualifying" in hold_classes)
        self.b("non-qualifying-veteran-free-agent-hold-included", "non_qualifying" in hold_classes)

        offer_sheets = [s for s in self.signings if s.kind == "offer_sheet"]
        rfa_offer_sheets = [s for s in offer_sheets
                            if (p := self.players.get(s.player or "")) is not None
                            and p.yos in (1, 2)]
        self.b("offer-sheet-restricted-free-agent-service-1-or-2", bool(rfa_offer_sheets))

        deemed = self.deemed_taxpayer_mle(post_no_holds)
        self.b("non-taxpayer-mid-level-deemed-taxpayer-mid-level", deemed)

        st_deem = self.sign_and_trade_deeming(st_signings)
        self.b("sign-and-trade-qualifying-free-agent-deeming-applies", bool(st_deem))

        # -- 4.2 conditional booleans (18) ----------------------------------
        if self.d["has-fifth-year-eligible-contract"]:
            self.b("fifth-year-eligible-meets-higher-max-criteria",
                   any(self.players[s.player].higher_max for s in tiers["fifth_year"]  # type: ignore[index]
                       if s.player in self.players))

        for flag, name, cls in (
            ("qualifying-veteran-free-agent-exception-available",
             "qualifying_veteran_free_agent", "qualifying"),
            ("early-qualifying-veteran-free-agent-exception-available",
             "early_qualifying_veteran_free_agent", "early_qualifying"),
            ("non-qualifying-veteran-free-agent-exception-available",
             "non_qualifying_veteran_free_agent", "non_qualifying"),
        ):
            if self.uses(name):
                ok = True
                for s in self.signings_using(name):
                    p = self.players.get(s.player or "")
                    if p is None or p.fa_class is None:
                        ok = False
                        break
                    if FREE_AGENCY_ORDER[p.fa_class] < FREE_AGENCY_ORDER[cls]:
                        ok = False
                        break
                self.b(flag, ok)

        if self.d["uses-minimum-player-salary-exception"]:
            self.b("minimum-player-salary-exception-salary-equals-minimum",
                   all(s.contract.get("salary_kind") == "minimum"
                       and not s.contract.get("minimum_plus_amount")
                       for s in self.signings_using("minimum_player_salary")))

        if self.d["uses-taxpayer-mid-level-exception"]:
            self.b("taxpayer-mid-level-used-before-row-a-to-f-transaction",
                   self.tmle_before_row_a_to_f())

        agg_legs = [(l, v, i, o) for (l, v, i, o) in tpes if v == "aggregated_tpe"]
        if self.d["uses-aggregated-standard-traded-player-exception"]:
            self.b("aggregation-outside-december-15-to-trade-deadline",
                   any(self.outside_aggregation_window(self.ops[l.op_index]) for l, _, _, _ in agg_legs))
            self.b("aggregation-replacement-count-less-than-traded-count",
                   any(len(l.incoming_players) < len(l.outgoing_players) for l, _, _, _ in agg_legs))

        if includes_st:
            self.b("sign-and-trade-uses-non-taxpayer-or-room-mid-level-exception",
                   any(s.exception in ("non_taxpayer_mid_level", "room_mid_level") for s in st_signings))
            assignee_rooms = []
            for s in st_signings:
                dest = self.sign_and_trade_destination(s)
                r = self.room(dest)
                assignee_rooms.append(
                    None if (r is None or s.amount is None) else (r >= s.amount))
            self.b("sign-and-trade-assignee-team-has-room",
                   all(x is True for x in assignee_rooms) if assignee_rooms else False)
            self.b("sign-and-trade-fifth-year-eligible-met-higher-max-criteria",
                   any((p := self.players.get(s.player or "")) is not None
                       and p.yos == 4 and p.higher_max for s in st_signings))

        if self.d["includes-first-round-pick-trade"]:
            self.b("first-round-pick-sold-for-cash", self.pick_sold_for_cash())
            self.b("first-round-pick-trade-leaves-consecutive-drafts-without-pick",
                   self.stepien_gap())

        if self.d["includes-trade-of-recently-signed-free-agent-contract"]:
            self.b("free-agent-contract-trade-is-initial-sign-and-trade",
                   all(kind == "sign_and_trade" for _, kind, _ in traded_recent))
            self.b("free-agent-contract-trade-before-december-15",
                   any(self.before_december_15(self.ops[oi]) for _, _, oi in traded_recent))

        if self.d["offer-sheet-restricted-free-agent-service-1-or-2"]:
            self.offer_sheet_fields(rfa_offer_sheets)

        # -- 4.3 conditional decimal strings (67) ---------------------------
        if we_teams:
            self.n("ratio-max-post-transaction-team-salary-to-cap-no-exception",
                   ratio(maxopt(post_of(t) for t in we_teams), CAP))

        if any(self.d[k] for k in ("qualifying-veteran-free-agent-hold-included",
                                   "early-qualifying-veteran-free-agent-hold-included",
                                   "non-qualifying-veteran-free-agent-hold-included")):
            self.n("ratio-post-transaction-team-salary-to-cap",
                   ratio(maxopt(post[t] for t in sorted(holds)), CAP))
        for flag, field, cls in (
            ("qualifying-veteran-free-agent-hold-included",
             "ratio-post-transaction-team-salary-excluding-qualifying-veteran-free-agent-holds-to-cap",
             "qualifying"),
            ("early-qualifying-veteran-free-agent-hold-included",
             "ratio-post-transaction-team-salary-excluding-early-qualifying-veteran-free-agent-holds-to-cap",
             "early_qualifying"),
            ("non-qualifying-veteran-free-agent-hold-included",
             "ratio-post-transaction-team-salary-excluding-non-qualifying-veteran-free-agent-holds-to-cap",
             "non_qualifying"),
        ):
            if self.d.get(flag):
                excl = self.post_salaries(exclude_hold_classes=(cls,))
                self.n(field, ratio(maxopt(excl[t] for t in sorted(holds)), CAP))

        if over38:
            with_re = self.post_salaries(include_holds=False, over38_reattribution=True)
            o38_teams = sorted({s.team for s in over38 if s.team})
            self.n("ratio-post-signing-team-salary-with-over-38-reattribution-to-cap",
                   ratio(maxopt(with_re.get(t) for t in o38_teams), CAP))
            self.n("ratio-post-signing-team-salary-without-over-38-reattribution-to-cap",
                   ratio(maxopt(post_no_holds.get(t) for t in o38_teams), CAP))

        for key, field_cap, field_prior in (
            ("under_7", "ratio-max-first-year-salary-to-cap-service-under-7",
             "ratio-max-first-year-salary-to-prior-salary-service-under-7"),
            ("7_to_9", "ratio-max-first-year-salary-to-cap-service-7-to-9",
             "ratio-max-first-year-salary-to-prior-salary-service-7-to-9"),
            ("10_plus", "ratio-max-first-year-salary-to-cap-service-10-or-more",
             "ratio-max-first-year-salary-to-prior-salary-service-10-or-more"),
        ):
            group = tiers[key]
            if not group:
                continue
            self.n(field_cap, ratio(maxopt(s.amount for s in group), CAP))
            self.n(field_prior, self.max_ratio_to_prior(group))

        if tiers["fifth_year"]:
            g = tiers["fifth_year"]
            self.n("ratio-fifth-year-eligible-first-year-salary-to-cap",
                   ratio(maxopt(s.amount for s in g), CAP))
            self.n("ratio-fifth-year-eligible-first-year-salary-to-prior-salary",
                   self.max_ratio_to_prior(g))
            self.i("fifth-year-eligible-contract-seasons",
                   max((s.seasons for s in g if s.seasons), default=None))

        if tiers["designated"]:
            g = tiers["designated"]
            self.n("ratio-designated-veteran-first-year-salary-to-cap",
                   ratio(maxopt(s.amount for s in g), CAP))
            self.n("ratio-designated-veteran-first-year-salary-to-prior-salary",
                   self.max_ratio_to_prior(g))

        if five_pct:
            self.n("max-annual-change-as-fraction-of-first-year-salary-5-percent-group",
                   maxopt(self.annual_change(s) for s in five_pct))
        if eight_pct:
            self.n("max-annual-change-as-fraction-of-first-year-salary-8-percent-group",
                   maxopt(self.annual_change(s) for s in eight_pct))

        if standard_len:
            self.i("max-contract-seasons-standard",
                   max((s.seasons for s in standard_len if s.seasons), default=None))
        if qvfa_prior:
            self.i("max-contract-seasons-qualifying-veteran-free-agent-prior-team",
                   max((s.seasons for s in qvfa_prior if s.seasons), default=None))
        for name, field in (
            ("non_taxpayer_mid_level", "max-contract-seasons-non-taxpayer-mid-level"),
            ("taxpayer_mid_level", "max-contract-seasons-taxpayer-mid-level"),
            ("bi_annual", "max-contract-seasons-bi-annual"),
            ("room_mid_level", "max-contract-seasons-room-mid-level"),
            ("minimum_player_salary", "max-contract-seasons-minimum-player-salary"),
        ):
            g = self.signings_using(name)
            if g:
                self.i(field, max((s.seasons for s in g if s.seasons), default=None))
        eq = self.signings_using("early_qualifying_veteran_free_agent")
        if eq:
            self.i("min-contract-seasons-early-qualifying-veteran-free-agent",
                   min((s.seasons for s in eq if s.seasons), default=None))

        self.veteran_free_agent_amounts()
        self.exception_amount_ratios(post_no_holds)
        self.apron_ratios(post_no_holds, tpes, st_signings, deemed, cash_legs)
        self.tpe_amounts(tpes, agg_legs, st_deem)

        if cash_legs:
            per_team: Dict[str, Decimal] = {}
            for l in self.legs:
                if l.team is None:
                    continue
                per_team[l.team] = max(per_team.get(l.team, Decimal(0)), l.cash_out, l.cash_in)
            self.n("ratio-aggregate-cash-paid-or-received-to-cap",
                   ratio(max(per_team.values()) if per_team else None, CAP))

        if includes_st:
            seasons = [s.seasons for s in st_signings if s.seasons]
            self.i("sign-and-trade-min-contract-seasons", min(seasons) if seasons else None)
            self.i("sign-and-trade-max-contract-seasons", max(seasons) if seasons else None)
            self.n("ratio-sign-and-trade-first-year-salary-to-cap",
                   ratio(maxopt(s.amount for s in st_signings), CAP))

        if traded_recent:
            self.n("free-agent-contract-months-elapsed-at-trade",
                   minopt(self.months_elapsed(self.ops[oi]) for _, _, oi in traded_recent))

        return self.d

    # ---- component computations -------------------------------------------
    def max_ratio_to_prior(self, group: Sequence[Signing]) -> Optional[Decimal]:
        vals = []
        for s in group:
            p = self.players.get(s.player or "")
            if p is None or p.prior_salary is None or p.prior_salary == 0 or s.amount is None:
                return None
            vals.append(s.amount / p.prior_salary)
        return max(vals) if vals else None

    def annual_change(self, s: Signing) -> Optional[Decimal]:
        """max_y |Salary(y) - Salary(y-1)| / Salary(first year)."""
        if s.schedule is None or len(s.schedule) < 2 or s.schedule[0] == 0:
            return None
        return max(abs(s.schedule[k] - s.schedule[k - 1]) / s.schedule[0]
                   for k in range(1, len(s.schedule)))

    def is_qvfa_prior_team(self, s: Signing) -> bool:
        p = self.players.get(s.player or "")
        return (s.kind != "offer_sheet" and p is not None
                and p.fa_class == "qualifying" and p.prior_team == s.team)

    def service_tiers(self) -> Dict[str, List[Signing]]:
        out: Dict[str, List[Signing]] = {
            "under_7": [], "7_to_9": [], "10_plus": [], "fifth_year": [], "designated": []}
        for s in self.signings:
            p = self.players.get(s.player or "")
            if p is None or p.yos is None:
                continue
            fifth = (p.yos == 4 and p.prior_team == s.team and s.kind != "offer_sheet")
            designated = (p.yos in (8, 9) and p.prior_team == s.team
                          and p.draft_team == p.prior_team and p.higher_max
                          and s.kind != "offer_sheet")
            if fifth:
                out["fifth_year"].append(s)
            if designated:
                out["designated"].append(s)
            if p.yos < 7 and not fifth:
                out["under_7"].append(s)
            elif 7 <= p.yos < 10 and not designated:
                out["7_to_9"].append(s)
            elif p.yos >= 10:
                out["10_plus"].append(s)
        return out

    def change_groups(self) -> Tuple[List[Signing], List[Signing]]:
        """Art. VII 5(a)(1) (5%) and 5(a)(2) (8%) groups."""
        five: List[Signing] = []
        eight: List[Signing] = []
        carve_out = {"bi_annual", "non_taxpayer_mid_level", "taxpayer_mid_level",
                     "room_mid_level"}
        for s in self.signings:
            p = self.players.get(s.player or "")
            bird = (p is not None and p.prior_team == s.team
                    and p.fa_class in ("qualifying", "early_qualifying")
                    and s.kind != "offer_sheet")
            if bird and s.exception not in carve_out and s.kind != "sign_and_trade":
                eight.append(s)
            else:
                five.append(s)
        return five, eight

    def is_over_38(self, s: Signing) -> bool:
        """Art. VII 3(a)(2): four or more Seasons, one commencing at/after age 38."""
        p = self.players.get(s.player or "")
        if p is None or p.age is None or not s.seasons or s.seasons < 4:
            return False
        return (p.age + s.seasons - 1) >= 38

    def deemed_taxpayer_mle(self, post_no_holds: Dict[str, Optional[Decimal]]) -> bool:
        """Art. VII 6(f)(5)."""
        for team in self.teams_using("non_taxpayer_mid_level"):
            group = [s for s in self.signings_using("non_taxpayer_mid_level") if s.team == team]
            if any(s.seasons is None or s.seasons > 2 for s in group):
                continue
            total = sumopt(s.amount for s in group)
            if total is None or total > TMLE_AMOUNT:
                continue
            after = post_no_holds.get(team)
            if after is not None and after > FIRST_APRON:
                return True
        return False

    def tmle_before_row_a_to_f(self) -> bool:
        """Art. VII 2(e)(2)(iii)(B): Taxpayer MLE used, then a row A-F transaction."""
        for team in self.teams_using("taxpayer_mid_level"):
            first = min(s.op_index for s in self.signings_using("taxpayer_mid_level")
                        if s.team == team)
            for s in self.signings:
                if s.team == team and s.op_index > first and s.exception in ROW_A_TO_F_EXCEPTIONS:
                    return True
            for leg, variant, _, _ in self.tpe_legs():
                if leg.team == team and leg.op_index > first and variant in (
                        "standard_tpe", "expanded_tpe"):
                    return True
        return False

    def sign_and_trade_destination(self, s: Signing) -> Optional[str]:
        op = self.ops[s.op_index]
        tr = op.get("trade") or {}
        if tr.get("third_team_asset_binding") == "unresolved":
            return None
        return tr.get("to_team")

    def sign_and_trade_deeming(self, st_signings: Sequence[Signing]) -> List[Signing]:
        """Art. VII 6(j)(5): all three conditions."""
        out = []
        for s in st_signings:
            p = self.players.get(s.player or "")
            if p is None or p.prior_team != s.team:
                continue
            if p.fa_class not in ("qualifying", "early_qualifying"):
                continue
            pre = self.pre.get(s.team or "")
            if pre is None or s.amount is None:
                continue
            if pre + s.amount <= CAP:
                continue
            if p.prior_salary is None:
                continue
            if s.amount <= NQVFA_PRIOR_MULTIPLE * p.prior_salary:
                continue
            out.append(s)
        return out

    def recently_signed_traded(self) -> List[Tuple[str, str, int]]:
        """(player, kind, op_index) for Contracts signed by a Free Agent this Cap Year
        and traded in the same instance."""
        out = []
        for s in self.signings:
            if s.kind == "offer_sheet" or not s.player:
                continue
            if s.kind == "sign_and_trade":
                out.append((s.player, "sign_and_trade", s.op_index))
                continue
            for leg in self.legs:
                if leg.op_index > s.op_index and s.player in leg.outgoing_players:
                    out.append((s.player, "trade", leg.op_index))
                    break
        return out

    def pick_sold_for_cash(self) -> bool:
        for leg in self.legs:
            if any(a.get("round") == "1" for a in leg.picks_out) and leg.cash_in > 0 \
                    and not leg.incoming_players:
                return True
        return False

    def stepien_gap(self) -> bool:
        """By-Laws 7.03: two consecutive future Drafts without a first round pick."""
        for team, raw in sorted(self.teams_raw.items()):
            dp = (raw or {}).get("draft_picks")
            if not dp:
                continue
            ahead = dp.get("own_first_round_years_ahead")
            if not (isinstance(ahead, str) and ahead.isdigit()):
                continue
            years = {CURRENT_YEAR + 1 + k for k in range(int(ahead))}
            for y in dp.get("own_first_round_missing_years") or []:
                years.discard(int(y))
            extra = {int(a["year"]) for a in dp.get("acquired_first_round_picks") or []
                     if str(a.get("year", "")).isdigit()}
            for leg in self.legs:
                if leg.team != team:
                    continue
                for a in leg.picks_out:
                    if a.get("round") == "1" and str(a.get("year", "")).isdigit():
                        y = int(a["year"])
                        if y in extra:
                            extra.discard(y)
                        else:
                            years.discard(y)
                for a in leg.picks_in:
                    if a.get("round") == "1" and str(a.get("year", "")).isdigit():
                        extra.add(int(a["year"]))
            have = years | extra
            horizon = range(CURRENT_YEAR + 1, CURRENT_YEAR + 1 + int(ahead))
            for y in horizon:
                if y not in have and (y + 1) not in have and (y + 1) in horizon:
                    return True
        return False

    def outside_aggregation_window(self, op: Dict[str, Any]) -> bool:
        """R10."""
        timing = op.get("timing") or {}
        month = (timing.get("month") or "").lower()
        if not month:
            return True
        return month[:3] not in {m[:3] for m in INSIDE_AGGREGATION_WINDOW_MONTHS}

    def before_december_15(self, op: Dict[str, Any]) -> bool:
        timing = op.get("timing") or {}
        month = (timing.get("month") or "").lower()[:3]
        year = timing.get("year")
        if not month:
            return True                      # R10: offseason, before December 15
        if year and year.isdigit() and int(year) > CURRENT_YEAR:
            return False
        order = ["jan", "feb", "mar", "apr", "may", "jun",
                 "jul", "aug", "sep", "oct", "nov", "dec"]
        if month not in order:
            return True
        if month == "dec":
            day = timing.get("day")
            return not (day and day.isdigit() and int(day) >= 15)
        return order.index(month) < order.index("dec")

    def months_elapsed(self, op: Dict[str, Any]) -> Optional[Decimal]:
        """Whole and fractional months from the 2024 Moratorium Period (July 1) to the trade."""
        timing = op.get("timing") or {}
        month = (timing.get("month") or "").lower()[:3]
        year = timing.get("year")
        if not month:
            return Decimal(0)                # "immediately"
        order = ["jan", "feb", "mar", "apr", "may", "jun",
                 "jul", "aug", "sep", "oct", "nov", "dec"]
        if month not in order:
            return None
        y = int(year) if year and year.isdigit() else CURRENT_YEAR
        months = (y - CURRENT_YEAR) * 12 + (order.index(month) - order.index("jul"))
        day = timing.get("day")
        frac = Decimal(int(day) - 1) / 30 if day and day.isdigit() else Decimal(0)
        return Decimal(max(months, 0)) + frac

    def offer_sheet_fields(self, sheets: Sequence[Signing]) -> None:
        """Art. XI 5(d)."""
        first_two: List[Optional[Decimal]] = []
        third: List[Optional[Decimal]] = []
        fourth_change: List[Optional[Decimal]] = []
        averages: List[Optional[Decimal]] = []
        third_max_ref: Optional[Decimal] = None
        at_max_first_two = False
        at_max_third = False

        for s in sheets:
            sch = s.schedule
            if sch is None:
                first_two.append(None)
                third.append(None)
                averages.append(None)
                continue
            first_two.append(max(sch[:2]) if len(sch) >= 2 else sch[0])
            p = self.players.get(s.player or "")
            # 5(d)(ii): the maximum absent 5(d)(i), assuming years 1-2 at the
            # Art. II 7(a) maximum and 5% annual increases on that base.
            base_max = (p.max_annual_salary() if p is not None else None)
            if base_max is not None:
                third_max_ref = base_max * Decimal("1.10")
            if len(sch) >= 3:
                third.append(sch[2])
                if third_max_ref is not None and sch[2] >= third_max_ref:
                    at_max_third = True
            if len(sch) >= 4 and sch[2] != 0:
                fourth_change.append(abs(sch[3] - sch[2]) / sch[2])
            averages.append(sum(sch) / Decimal(len(sch)))
            if first_two[-1] is not None and first_two[-1] >= NTMLE_AMOUNT:
                at_max_first_two = True

        self.b("offer-sheet-first-two-years-at-maximum-allowable", at_max_first_two)
        self.b("offer-sheet-third-year-at-maximum-allowable", at_max_third)
        self.b("offer-sheet-uses-third-year-maximum", at_max_third)

        self.n("ratio-offer-sheet-max-first-two-year-salary-to-non-taxpayer-mid-level-amount",
               ratio(maxopt(first_two), NTMLE_AMOUNT))
        if third:
            self.n("ratio-offer-sheet-third-year-salary-to-maximum-allowable",
                   ratio(maxopt(third), third_max_ref))
        if fourth_change:
            self.n("ratio-offer-sheet-fourth-year-change-to-third-year-salary",
                   maxopt(fourth_change))
        rooms = [self.room(s.team) for s in sheets]
        avg = maxopt(averages)
        rm = minopt([r for r in rooms]) if rooms and all(r is not None for r in rooms) else None
        if rm is not None and rm <= 0:
            rm = None                       # ratio undefined; omit per section 4 preamble
        self.n("ratio-offer-sheet-average-salary-to-new-team-room", ratio(avg, rm))

    def veteran_free_agent_amounts(self) -> None:
        q = self.signings_using("qualifying_veteran_free_agent")
        if q:
            vals: List[Optional[Decimal]] = []
            for s in q:
                p = self.players.get(s.player or "")
                vals.append(ratio(s.amount, p.max_annual_salary() if p else None))
            self.n("ratio-qualifying-veteran-free-agent-first-year-salary-to-maximum-annual-salary",
                   maxopt(vals))

        e = self.signings_using("early_qualifying_veteran_free_agent")
        if e:
            self.n("ratio-early-qualifying-veteran-free-agent-first-year-salary-to-prior-salary",
                   self.max_ratio_to_prior(e))
            self.n("ratio-early-qualifying-veteran-free-agent-first-year-salary-to-average-player-salary",
                   ratio(maxopt(s.amount for s in e), AVG_PLAYER_SALARY_2023_24))

        nq = self.signings_using("non_qualifying_veteran_free_agent")
        if nq:
            self.n("ratio-non-qualifying-veteran-free-agent-first-year-salary-to-prior-salary",
                   self.max_ratio_to_prior(nq))
            # Needs the Minimum Annual Salary schedule; see DERIVED.md gap G-MIN.
            self.n("ratio-non-qualifying-veteran-free-agent-first-year-salary-to-minimum-annual-salary",
                   None)

    def exception_amount_ratios(self, post_no_holds: Dict[str, Optional[Decimal]]) -> None:
        for name, field, denom in (
            ("non_taxpayer_mid_level",
             "ratio-non-taxpayer-mid-level-aggregate-first-year-salary-to-cap", CAP),
            ("bi_annual", "ratio-bi-annual-aggregate-first-year-salary-to-cap", CAP),
            ("room_mid_level", "ratio-room-mid-level-aggregate-first-year-salary-to-cap", CAP),
            ("taxpayer_mid_level",
             "ratio-taxpayer-mid-level-aggregate-first-year-salary-to-taxpayer-mid-level-amount",
             TMLE_AMOUNT),
        ):
            group = self.signings_using(name)
            if not group:
                continue
            per_team: Dict[str, List[Optional[Decimal]]] = {}
            for s in group:
                per_team.setdefault(s.team or "?", []).append(s.amount)
            totals = [sumopt(v) for v in per_team.values()]
            self.n(field, ratio(maxopt(totals), denom))

        if self.uses("taxpayer_mid_level"):
            teams = self.teams_using("taxpayer_mid_level")
            self.n("ratio-post-taxpayer-mid-level-team-salary-to-first-apron",
                   ratio(maxopt(post_no_holds.get(t) for t in teams), FIRST_APRON))

    def apron_ratios(self, post: Dict[str, Optional[Decimal]],
                     tpes: Sequence[Tuple[TradeLeg, str, Optional[Decimal], Optional[Decimal]]],
                     st_signings: Sequence[Signing], deemed: bool,
                     cash_legs: Sequence[TradeLeg]) -> None:
        def teams_post(teams: Sequence[Optional[str]], denom: Decimal) -> Optional[Decimal]:
            ts = [t for t in teams if t]
            if not ts:
                return None
            return ratio(maxopt(post.get(t) for t in ts), denom)

        if self.uses("bi_annual"):
            self.n("ratio-post-bi-annual-transaction-team-salary-to-first-apron",
                   teams_post(self.teams_using("bi_annual"), FIRST_APRON))
        if self.uses("non_taxpayer_mid_level"):
            self.n("ratio-post-non-taxpayer-mid-level-transaction-team-salary-to-first-apron",
                   teams_post(self.teams_using("non_taxpayer_mid_level"), FIRST_APRON))
        if self.d.get("acquires-player-under-sign-and-trade-contract"):
            self.n("ratio-post-sign-and-trade-acquisition-team-salary-to-first-apron",
                   teams_post([self.sign_and_trade_destination(s) for s in st_signings],
                              FIRST_APRON))
        if self.d.get("uses-expanded-traded-player-exception"):
            self.n("ratio-post-expanded-traded-player-exception-transaction-team-salary-to-first-apron",
                   teams_post([l.team for l, v, _, _ in tpes if v == "expanded_tpe"], FIRST_APRON))
        if self.d.get("uses-aggregated-standard-traded-player-exception"):
            self.n("ratio-post-aggregated-traded-player-exception-transaction-team-salary-to-second-apron",
                   teams_post([l.team for l, v, _, _ in tpes if v == "aggregated_tpe"], SECOND_APRON))
        if self.d.get("pays-cash-in-trade"):
            self.n("ratio-post-cash-trade-team-salary-to-second-apron",
                   teams_post([l.team for l in self.legs if l.cash_out], SECOND_APRON))
        if self.d.get("uses-traded-player-exception-for-signed-and-traded-contract"):
            self.n("ratio-post-sign-and-trade-traded-player-exception-team-salary-to-second-apron",
                   teams_post([l.team for l in self.legs
                               if l.sign_and_trade and l.incoming_players and not l.unresolved],
                              SECOND_APRON))
        if self.uses("taxpayer_mid_level"):
            self.n("ratio-post-taxpayer-mid-level-transaction-team-salary-to-second-apron",
                   teams_post(self.teams_using("taxpayer_mid_level"), SECOND_APRON))
        if deemed:
            self.n("ratio-post-deemed-taxpayer-mid-level-transaction-team-salary-to-second-apron",
                   teams_post(self.teams_using("non_taxpayer_mid_level"), SECOND_APRON))

    def tpe_amounts(self, tpes: Sequence[Tuple[TradeLeg, str, Optional[Decimal], Optional[Decimal]]],
                    agg_legs: Sequence[Tuple[TradeLeg, str, Optional[Decimal], Optional[Decimal]]],
                    st_deem: Sequence[Signing]) -> None:
        excesses: List[Optional[Decimal]] = []

        def excess(variant: str, base_fn) -> Optional[Decimal]:
            vals = []
            for leg, v, inc, outg in tpes:
                if v != variant:
                    continue
                base = base_fn(leg, inc, outg)
                if inc is None or base is None:
                    return None
                vals.append(inc - base)
            return max(vals) if vals else None

        if self.d.get("uses-standard-traded-player-exception"):
            val = excess("standard_tpe", lambda l, i, o: o)
            self.n("standard-traded-player-exception-incoming-excess-over-base-limit", val)
            excesses.append(val)
        if self.d.get("uses-aggregated-standard-traded-player-exception"):
            val = excess("aggregated_tpe", lambda l, i, o: o)
            self.n("aggregated-traded-player-exception-incoming-excess-over-base-limit", val)
            excesses.append(val)
            counts = [len(l.outgoing_players) for l, _, _, _ in agg_legs]
            self.i("aggregated-traded-player-count", max(counts) if counts else None)
            mins = [sum(1 for p in l.outgoing_players
                        if (pv := self.players.get(p)) is not None and pv.minimum_contract)
                    for l, _, _, _ in agg_legs]
            self.i("minimum-traded-player-count", max(mins) if mins else None)
        if self.d.get("uses-room-traded-player-exception"):
            val = excess("room_tpe", lambda l, i, o: self.room(l.team))
            self.n("room-traded-player-exception-incoming-excess-over-base-limit", val)
            excesses.append(val)
        if self.d.get("uses-expanded-traded-player-exception"):
            v125 = excess("expanded_tpe", lambda l, i, o: None if o is None else o * Decimal("1.25"))
            v200 = excess("expanded_tpe", lambda l, i, o: None if o is None else o * Decimal(2))
            v100 = excess("expanded_tpe", lambda l, i, o: o)
            self.n("expanded-traded-player-exception-incoming-excess-over-125-percent-outgoing", v125)
            self.n("expanded-traded-player-exception-incoming-excess-over-200-percent-outgoing", v200)
            self.n("expanded-traded-player-exception-incoming-excess-over-outgoing-in-2023-24-dollars",
                   None if v100 is None else v100 * (CAP_2023_24 / CAP))
            excesses.append(v125)
        if self.d.get("uses-any-traded-player-exception"):
            self.n("traded-player-exception-incoming-excess-over-base-limit-max", maxopt(excesses))
            legs = [l.team for l, _, _, _ in tpes]
            post = self.post_salaries(include_holds=False)
            self.n("ratio-post-trade-team-salary-to-first-apron",
                   ratio(maxopt(post.get(t) for t in legs if t), FIRST_APRON))

        if st_deem:
            vals: List[Optional[Decimal]] = []
            for s in st_deem:
                p = self.players.get(s.player or "")
                leg = next((l for l in self.legs
                            if l.op_index == s.op_index and l.team == s.team), None)
                if leg is None or p is None or s.amount is None:
                    vals.append(None)
                    continue
                incoming = sumopt(self.moving_salary(x) for x in leg.incoming_players)
                deemed_out = max(p.prior_salary or Decimal(0), s.amount / 2)
                vals.append(None if incoming is None else incoming - deemed_out)
            self.n("sign-and-trade-deemed-traded-player-exception-incoming-excess-over-base-limit",
                   maxopt(vals))


def over38_first_year_after_reattribution(s: Signing, p: Optional[PlayerView]) -> Optional[Decimal]:
    """Art. VII 3(a)(2) pro-rata re-attribution, expressed as the first Season's
    Salary after later Seasons are pushed back onto the earlier ones."""
    if s.schedule is None or p is None or p.age is None or not s.seasons or s.seasons < 4:
        return s.amount
    if (p.age + s.seasons - 1) < 38:
        return s.amount
    first_after_38 = max(0, 38 - p.age)
    cut = max(3, first_after_38)             # "the fourth Salary Cap Year ... whichever is later"
    if cut >= len(s.schedule):
        return s.amount
    prior = s.schedule[:cut]
    total_prior = sum(prior)
    reattributed = sum(s.schedule[cut:])
    if total_prior == 0:
        return s.amount
    return prior[0] + reattributed * (prior[0] / total_prior)


# --------------------------------------------------------------------------- #
# 7. Driver
# --------------------------------------------------------------------------- #
ALWAYS_PRESENT = (
    "contains-provision-outside-pack-scope",
    "any-transaction-without-exception",
    "uses-qualifying-veteran-free-agent-exception",
    "uses-early-qualifying-veteran-free-agent-exception",
    "uses-non-qualifying-veteran-free-agent-exception",
    "uses-non-taxpayer-mid-level-exception",
    "uses-taxpayer-mid-level-exception",
    "uses-bi-annual-exception",
    "uses-room-mid-level-exception",
    "uses-minimum-player-salary-exception",
    "uses-standard-traded-player-exception",
    "uses-aggregated-standard-traded-player-exception",
    "uses-expanded-traded-player-exception",
    "uses-room-traded-player-exception",
    "uses-any-traded-player-exception",
    "uses-traded-player-exception-for-signed-and-traded-contract",
    "includes-sign-and-trade",
    "acquires-player-under-sign-and-trade-contract",
    "includes-cash-in-trade",
    "pays-cash-in-trade",
    "includes-first-round-pick-trade",
    "includes-trade-of-recently-signed-free-agent-contract",
    "has-new-contract-service-under-7",
    "has-new-contract-service-7-to-9",
    "has-new-contract-service-10-or-more",
    "has-fifth-year-eligible-contract",
    "has-designated-veteran-player-contract",
    "has-standard-length-new-contract",
    "has-qualifying-veteran-free-agent-prior-team-contract",
    "has-contract-governed-by-5-percent-limit",
    "has-contract-governed-by-8-percent-limit",
    "over-38-contract-present",
    "over-38-qualifying-veteran-free-agent-age-35-or-36-five-seasons",
    "qualifying-veteran-free-agent-hold-included",
    "early-qualifying-veteran-free-agent-hold-included",
    "non-qualifying-veteran-free-agent-hold-included",
    "offer-sheet-restricted-free-agent-service-1-or-2",
    "non-taxpayer-mid-level-deemed-taxpayer-mid-level",
    "sign-and-trade-qualifying-free-agent-deeming-applies",
)


def derive(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Compute ``facts.derived`` for one facts document.  Pure; does not mutate ``doc``."""
    return Derivation(doc).run()


def derive_with_notes(doc: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    d = Derivation(doc)
    out = d.run()
    return out, sorted(set(d.notes))


SIDECARS = ("index.json", "manifest.json")


def run(facts_dir: Path, out_dir: Path, report_path: Optional[Path]) -> Dict[str, Any]:
    files = sorted(p for p in facts_dir.glob("*.json") if p.name not in SIDECARS)
    out_dir.mkdir(parents=True, exist_ok=True)
    per_instance = []
    field_counts: Dict[str, int] = {}
    omission_counts: Dict[str, int] = {}
    bad_types: List[str] = []

    for path in files:
        doc = json.loads(path.read_text(encoding="utf-8"))
        derived, notes = derive_with_notes(doc)
        for k, v in derived.items():
            field_counts[k] = field_counts.get(k, 0) + 1
            if not isinstance(v, bool) and not is_jps_decimal(v):
                bad_types.append(f"{doc.get('instance_id')}::{k}={v!r}")
        for k in notes:
            omission_counts[k] = omission_counts.get(k, 0) + 1
        missing = [k for k in ALWAYS_PRESENT if k not in derived]
        doc.setdefault("facts", {})["derived"] = derived
        (out_dir / path.name).write_text(
            json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8")
        per_instance.append({
            "instance_id": doc.get("instance_id"),
            "fields": len(derived),
            "omitted": notes,
            "missing_always_present": missing,
        })

    if out_dir.resolve() != facts_dir.resolve():
        for name in SIDECARS:
            src = facts_dir / name
            if src.exists():
                (out_dir / name).write_text(src.read_text(encoding="utf-8"),
                                            encoding="utf-8")

    report = {
        "schema": "jps-study-001-derive-report/1",
        "instances": len(files),
        "constants": {
            "salary_cap_2024_25": dec_str(CAP),
            "salary_cap_2023_24": dec_str(CAP_2023_24),
            "average_player_salary_2023_24": dec_str(AVG_PLAYER_SALARY_2023_24),
            "luxury_tax": dec_str(LUXURY_TAX),
            "first_apron": dec_str(FIRST_APRON),
            "second_apron": dec_str(SECOND_APRON),
            "non_taxpayer_mid_level_amount": dec_str(NTMLE_AMOUNT),
            "taxpayer_mid_level_amount": dec_str(TMLE_AMOUNT),
            "bi_annual_amount": dec_str(BAE_AMOUNT),
            "room_mid_level_amount": dec_str(ROOM_MLE_AMOUNT),
            "minimum_player_salary": None,
            "minimum_annual_salary": None,
        },
        "field_presence": dict(sorted(field_counts.items())),
        "omission_counts": dict(sorted(omission_counts.items())),
        "non_conforming_values": bad_types,
        "instances_missing_always_present": [
            r for r in per_instance if r["missing_always_present"]],
        "per_instance": per_instance,
    }
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                               encoding="utf-8")
    return report


def main(argv: Optional[Sequence[str]] = None) -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--facts", type=Path, default=here / "out" / "facts",
                    help="directory of facts documents from parse_nba.py")
    ap.add_argument("--out", type=Path, default=None,
                    help="output directory (default: same as --facts, i.e. in place)")
    ap.add_argument("--report", type=Path, default=here / "out" / "derive-report.json")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero if any always-present field is missing or "
                         "any emitted value violates the JPS decimal grammar")
    ap.add_argument("--readings", action="store_true", help="print the numbered readings and exit")
    args = ap.parse_args(argv)

    if args.readings:
        sys.stdout.write(READINGS)
        return 0

    out_dir = args.out or args.facts
    report = run(args.facts, out_dir, args.report)

    print("=" * 72)
    print("facts.derived preprocessor  (deterministic, stdlib only, no network)")
    print("=" * 72)
    print(f"instances               : {report['instances']}")
    print(f"distinct fields emitted : {len(report['field_presence'])} of 124 in the contract")
    always = sum(1 for k in ALWAYS_PRESENT if report["field_presence"].get(k) == report["instances"])
    print(f"always-present complete : {always}/39")
    print(f"omitted-field events    : {sum(report['omission_counts'].values())}"
          f" across {len(report['omission_counts'])} distinct fields")
    print(f"non-conforming values   : {len(report['non_conforming_values'])}")
    print("-" * 72)
    print("most-omitted fields (omitted => unknown => escalate):")
    for k, v in sorted(report["omission_counts"].items(), key=lambda kv: (-kv[1], kv[0]))[:12]:
        print(f"  {v:4d}  {k}")
    print("-" * 72)
    print(f"output : {out_dir}")
    print(f"report : {args.report}")

    if args.strict and (report["non_conforming_values"]
                        or report["instances_missing_always_present"]):
        print("STRICT: contract violations present", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
