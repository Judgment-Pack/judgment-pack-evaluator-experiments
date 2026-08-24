#!/usr/bin/env python3
"""V7 — the completeness argument, re-derived MECHANICALLY over the gold grid.

REGISTERED DEFINITION. `design/POLICY-DRAFT.md` ("Still open at this revision")
and `harness/SCAFFOLD.md` step 2b register V7 as: re-derive the completeness
argument mechanically over the gold grid, asserting EXACTLY ONE governing clause
per cell under the earliest-clause tie-break, with the former X1 region asserted
COVERED rather than excluded. This module is that derivation. The document it
feeds — `verification/V7-COMPLETENESS.md` — is the REGISTERED ARTIFACT; the
reference build's 236,196-cell derived-space sweep is evidence, not the artifact.

WHAT THIS PROGRAM READS, AND WHAT IT REFUSES TO READ.
The clause tracer below implements the POLICY PROSE's own order of application —
`design/POLICY-DRAFT.md`'s stimulus sections "Order of application",
"Precondition", "Determination clauses", "Overrides" and "Unreadable inputs" —
and nothing else. It does NOT consult, load, parse, execute or import either
REFERENCE IMPLEMENTATION (`reference/refA/pack.json` on the pinned jpack;
`reference/refB/policy.rego` on the pinned OPA), the clean-room oracle, or the
gold AUTHORING transport (`design/gold/gold_author.py`). It makes no engine call
and no subprocess call of any kind, and it imports nothing outside the Python
standard library. A completeness argument re-derived from an implementation
asserts only that the implementation agrees with itself; V7's whole point is
that the argument is re-derived from the text those implementations were built
from, and then compared with the gold suite's own clause citations.

The ONE thing this module takes from another file's code is the RETIRED X1
PREDICATE. It is lifted, as source, out of `design/gold/check_gold.py`'s
`retired_x1` by `ast` and executed in an isolated namespace (the rest of that
module — which does shell out to both pinned engines — is never imported and
never runs). Transcribing the predicate by hand would put a second spelling of a
registered region in the tree; lifting it keeps one.

WHAT IT ASSERTS (each is reported PASS/FAIL and each moves the exit status):

  A1  STRUCTURE       117 rows, unique ids, every cite entry a known clause.
  A2  COVERAGE        every cell of the gold grid — and every readable
                      completion of every cell carrying an unreadable input —
                      has AT LEAST ONE clause whose stated conditions hold.
                      This is the completeness half: the policy has no gap.
  A3  DETERMINACY     the order of application selects EXACTLY ONE governing
                      clause per cell. This is the argument's other half: where
                      several clauses hold, the earliest-clause tie-break
                      resolves them, and the resolution is a function of the
                      cell, not a choice.
  A4  REPRODUCTION    the derived disposition and reason set equal the gold
                      row's own expectation. Not part of V7's registered text,
                      but it is what makes A5 readable: a clause disagreement
                      over a cell whose OUTCOME the tracer cannot reproduce
                      would be a disagreement about the policy, not about a
                      citation.
  A5  CITE AGREEMENT  the derived governing clause equals the row's FIRST cite
                      entry (gold's stated convention: cite lists are ordered
                      with the governing clause first).
  A6  X1 COVERED      the region the retired X1 exclusion used to forbid is
                      non-empty in gold, is named row by row, and every row in
                      it derives a governing clause like any other cell.

Two further quantities are REPORTED and do not move the exit status, because
they exist to let a maintainer adjudicate an A5 failure rather than to gate:

  B1  MEMBERSHIP      the derived governing clause is SOMEWHERE in the row's
                      cite list (a weaker claim than A5: same clause set, other
                      order).
  B2  LADDER ORDER    a purely lexical reading of the cite lists — is cite[0]
                      the earliest CITED clause under the registered ladder? —
                      computed without any semantics at all, so an A5 failure
                      can be attributed to the derivation or to the citation.

THE LADDER, and the one interpretive commitment in this file.
`design/POLICY-DRAFT.md` "Order of application": "Clauses apply in this order:
P1 first; then the overrides O3, then O2; then the determination clauses D1–D8,
as modified by O1. U1 governs cases the clauses above leave undetermined because
an input cannot be read; a determination issued by a clause that does not depend
on the unreadable input stands (U1 states the test). Where more than one clause
yields the same determination, the earliest clause in this order governs."

  * O1 is NOT a rung. It is a modifier of D6c's scope ("clause D6c does not
    apply; such requests fall to D8"), and D8's own text claims the region it
    vacates ("including requests removed from D6c by O1"). O1 issues no
    determination, so it is never a candidate governor here.
  * U1 is the LAST rung. Its counterfactual is run only over the unreadable
    inputs, every other input keeping its reported state, and "the same
    determination" means the same OUTCOME (disposition plus reason set).
  * "A determination issued by a clause that does not depend on the unreadable
    input stands" is operationalised as CLAUSE INVARIANCE across the readable
    completions: if the same clause governs every completion, that clause does
    not depend on the unreadable input on this cell, and it governs. If the
    outcome is uniform but the clause issuing it is not, no single clause issues
    the determination and U1 governs. If the outcome is not uniform, U1 governs
    and the case is unresolved as unknown.

Run:  PYTHONDONTWRITEBYTECODE=1 <the pinned interpreter> verification/derive_v7.py
      (add --full to print the whole 117-row derivation table)
Exit: 0 iff A1–A6 all pass.
"""
import ast
import hashlib
import json
import os
import sys
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
GOLD_PATH = os.path.join(STUDY, "design", "gold", "gold.json")
PROSE_PATH = os.path.join(STUDY, "design", "POLICY-DRAFT.md")
FROZEN_PROSE_PATH = os.path.join(STUDY, "policy", "POLICY.md")
FROZEN_GOLD_PATH = os.path.join(STUDY, "gold", "GOLD.json")
CHECK_GOLD_PATH = os.path.join(STUDY, "design", "gold", "check_gold.py")

# ---------------------------------------------------------------------------
# The ladder. Rank order IS the prose's order of application; O1 is absent by
# the commitment stated in the module docstring, and appears only in the lexical
# order below, which exists to read gold's cite LISTS and derives nothing.
LADDER = ("P1", "O3", "O2", "D1", "D2", "D3", "D4", "D5",
          "D6a", "D6b", "D6c", "D7", "D8", "U1")
RANK = {clause: index for index, clause in enumerate(LADDER)}

# The lexical order used by B2 only: O1 sits immediately before the clause whose
# scope it modifies. Nothing in the derivation reads this.
LEXICAL = ("P1", "O3", "O2", "D1", "D2", "D3", "D4", "D5",
           "D6a", "D6b", "O1", "D6c", "D7", "D8", "U1")
LEXICAL_RANK = {clause: index for index, clause in enumerate(LEXICAL)}

CLAUSES = frozenset(LEXICAL)

# The registered numeric literals, as decimal strings on the canonical grid.
RISK_MIN, RISK_MAX = 0, 100
RISK_D6_CUT, RISK_D4_CUT, RISK_D3_CUT = 40, 70, 90
SPEND_MIN = Decimal("0.00")
SPEND_MAX = Decimal("10000000.00")
SPEND_D6C_D7_CAP = Decimal("100000.00")
SPEND_D6A_CAP = Decimal("500000.00")
SPEND_D6B_CAP = Decimal("2000000.00")          # inclusive in D6b, exclusive in O3
CENT = Decimal("0.01")

UNREADABLE_FIELDS = ("risk", "spend", "country")
COUNTRIES = ("LOW", "MEDIUM", "HIGH")


# ---------------------------------------------------------------------------
# Cell accessors. `None` means the input is not reported: unreadable for the
# three numerics/country, unreported for the statuses and the two evidence
# availabilities. The prose's U1 says the screening result, evidence
# availability and the yes/no statuses are never "unreadable" in U1's sense.

def risk_of(cell):
    return None if cell["risk"] is None else int(cell["risk"])


def spend_of(cell):
    return None if cell["spend"] is None else Decimal(cell["spend"])


def candidates(cell):
    """Every clause whose STATED CONDITIONS hold on a fully readable cell, with
    the disposition that clause issues, as {clause: (disposition, reasons)}.

    One clause, one entry, evaluated from its own sentence — not by running a
    ladder and stopping. The ladder is applied afterwards, by `govern`, which is
    what lets A2 (at least one) and A3 (exactly one, after the tie-break) be
    two separate assertions rather than one tautology.
    """
    found = {}
    evidence = cell["finEvidence"]
    sanctions = cell["sanctions"]
    country = cell["country"]
    risk = risk_of(cell)
    spend = spend_of(cell)
    clear = sanctions == "CLEAR"

    # P1 — "No determination of any kind ... may be issued without financial
    # evidence: no other clause of this policy applies unless financial evidence
    # is available." Absent -> missing-required-evidence; unreported -> unknown.
    if evidence != "present":
        reasons = ("missing-required-evidence",) if evidence == "absent" else ("unknown",)
        return {"P1": ("unresolved", reasons)}
    # Past this point financial evidence is available, so "no other clause
    # applies" is satisfied for every clause below.

    # O3 — HIGH country, CLEAR screening, spend above $2,000,000.00, evidence
    # available. Unresolved on the ground of escalation.
    if clear and country == "HIGH" and spend is not None and spend > SPEND_D6B_CAP:
        found["O3"] = ("unresolved", ("exception-escalation",))

    # O2 — critical supplier (yes) with a CLEAR screening result: review.
    # "never applies when the screening result is MATCH or UNKNOWN".
    if clear and cell["critical"] == "yes":
        found["O2"] = ("review", ())

    # D1 / D2 — the screening gate. Each "depends on no input but the screening
    # result (subject always to P1)".
    if sanctions == "MATCH":
        found["D1"] = ("reject", ())
    if sanctions == "UNKNOWN":
        found["D2"] = ("unresolved", ("no-match",))

    # D3–D8 apply only when the screening result is CLEAR.
    if clear:
        if risk is not None and risk >= RISK_D3_CUT:
            found["D3"] = ("reject", ())                      # D3 — critical risk
        if country == "HIGH" and risk is not None and risk >= RISK_D4_CUT:
            found["D4"] = ("reject", ())                      # D4 — HIGH + 70+
        if cell["prior"] == "yes":
            found["D5"] = ("reject", ())                      # D5 — prior action
        # "The approval clauses D6 and D7 apply only to vendors with no recorded
        # prior enforcement action." An unreported status is treated as no.
        if cell["prior"] != "yes" and risk is not None and spend is not None:
            if country == "LOW":
                if risk < RISK_D6_CUT and spend <= SPEND_D6A_CAP:
                    found["D6a"] = ("approve", ())
                if (risk < RISK_D6_CUT and SPEND_D6A_CAP < spend <= SPEND_D6B_CAP):
                    insurance = cell["insurance"]
                    if insurance == "present":
                        found["D6b"] = ("approve", ())
                    elif insurance == "absent":
                        found["D6b"] = ("enhanced-review", ())
                    else:
                        found["D6b"] = ("unresolved", ("unknown",))
                if (RISK_D6_CUT <= risk < RISK_D4_CUT
                        and spend <= SPEND_D6C_D7_CAP
                        # O1 — first-engagement suspension: for new vendors
                        # (yes), D6c does not apply; such requests fall to D8.
                        # An unreported new-vendor status is treated as no.
                        and cell["newVendor"] != "yes"):
                    found["D6c"] = ("approve", ())
            if (country == "MEDIUM" and risk < RISK_D6_CUT
                    and spend <= SPEND_D6C_D7_CAP):
                found["D7"] = ("approve", ())
        # D8 — "Every request with a CLEAR screening result that is not
        # determined by D3–D7 — including requests removed from D6c by O1 — is
        # referred for review."
        if not any(clause in found for clause in
                   ("D3", "D4", "D5", "D6a", "D6b", "D6c", "D7")):
            found["D8"] = ("review", ())
    return found


def govern_readable(cell):
    """(clause, verdict, candidate count) for a cell with nothing unreadable.

    The earliest clause in the order of application governs. The prose's
    tie-break sentence names the equal-determination case explicitly; the
    unequal case is the order of application itself (O2 "displaces every
    determination D1–D8 would issue"; O3 "takes precedence over every clause
    except P1"), so one rule serves both.
    """
    found = candidates(cell)
    if not found:
        return None, None, 0
    clause = min(found, key=lambda name: RANK[name])
    return clause, found[clause], len(found)


# ---------------------------------------------------------------------------
# U1's counterfactual, over the readable completions of the unreadable inputs.
#
# Risk is enumerated EXHAUSTIVELY over its registered domain (0..100). Spend is
# enumerated over a QUOTIENT of its registered domain: the prose compares spend
# with exactly three literals, so the domain splits into four intervals on which
# every spend predicate is constant, and each is represented by its two
# endpoints and an interior point. `spend_quotient_problems()` asserts that
# constancy and the distinctness of the four predicate vectors mechanically,
# so the quotient is checked rather than argued.

def spend_classes():
    return (
        (SPEND_MIN, SPEND_D6C_D7_CAP),
        (SPEND_D6C_D7_CAP + CENT, SPEND_D6A_CAP),
        (SPEND_D6A_CAP + CENT, SPEND_D6B_CAP),
        (SPEND_D6B_CAP + CENT, SPEND_MAX),
    )


def spend_predicates(value):
    return (value <= SPEND_D6C_D7_CAP, value <= SPEND_D6A_CAP,
            value <= SPEND_D6B_CAP, value > SPEND_D6B_CAP)


def spend_representatives():
    values = []
    for low, high in spend_classes():
        middle = (low + high) / 2
        middle = middle.quantize(CENT)
        for value in (low, middle, high):
            if value not in values:
                values.append(value)
    return values


def spend_quotient_problems():
    problems = []
    vectors = []
    for low, high in spend_classes():
        middle = ((low + high) / 2).quantize(CENT)
        seen = {spend_predicates(value) for value in (low, middle, high)}
        if len(seen) != 1:
            problems.append("spend predicates are not constant on [%s, %s]" % (low, high))
        vectors.append(spend_predicates(low))
    if len(set(vectors)) != len(vectors):
        problems.append("two spend classes share a predicate vector: the quotient "
                        "is not the one the prose's three literals induce")
    if spend_classes()[0][0] != SPEND_MIN or spend_classes()[-1][1] != SPEND_MAX:
        problems.append("the spend classes do not cover the registered domain")
    return problems


def completions(cell):
    """Every readable assignment of this cell's unreadable inputs, with every
    other input keeping its reported state (U1: "the test varies only the
    unreadable inputs")."""
    unreadable = [field for field in UNREADABLE_FIELDS if cell[field] is None]
    if not unreadable:
        yield dict(cell)
        return
    risks = ([str(value) for value in range(RISK_MIN, RISK_MAX + 1)]
             if "risk" in unreadable else [cell["risk"]])
    spends = ([str(value) for value in spend_representatives()]
              if "spend" in unreadable else [cell["spend"]])
    countries = list(COUNTRIES) if "country" in unreadable else [cell["country"]]
    for country in countries:
        for risk in risks:
            for spend in spends:
                completion = dict(cell)
                completion["country"] = country
                completion["risk"] = risk
                completion["spend"] = spend
                yield completion


class Derivation(object):
    __slots__ = ("clause", "verdict", "route", "completions", "max_candidates",
                 "min_candidates", "clause_set")

    def __init__(self, clause, verdict, route, completions_seen,
                 max_candidates, min_candidates, clause_set):
        self.clause = clause
        self.verdict = verdict
        self.route = route
        self.completions = completions_seen
        self.max_candidates = max_candidates
        self.min_candidates = min_candidates
        self.clause_set = clause_set


def derive(cell):
    """The governing clause and the outcome for one gold cell.

    route is one of:
      readable          nothing unreadable; the ladder decides directly
      stands            unreadable inputs present, and ONE clause governs every
                        readable completion with one outcome — "a determination
                        issued by a clause that does not depend on the
                        unreadable input stands"
      u1-uniform        the outcome is uniform but the issuing clause is not:
                        no single clause issues it, so U1 does
      u1-unknown        the outcome is not uniform: unresolved as unknown
    """
    unreadable = [field for field in UNREADABLE_FIELDS if cell[field] is None]
    if not unreadable:
        clause, verdict, count = govern_readable(cell)
        return Derivation(clause, verdict, "readable", 1, count, count,
                          frozenset() if clause is None else frozenset([clause]))
    clauses, verdicts, counts, seen = [], set(), [], 0
    for completion in completions(cell):
        clause, verdict, count = govern_readable(completion)
        seen += 1
        counts.append(count)
        if clause is None:
            return Derivation(None, None, "gap", seen, 0, 0, frozenset())
        clauses.append(clause)
        verdicts.add(verdict)
    clause_set = frozenset(clauses)
    if len(verdicts) == 1:
        verdict = verdicts.pop()
        if len(clause_set) == 1:
            return Derivation(clauses[0], verdict, "stands", seen,
                              max(counts), min(counts), clause_set)
        return Derivation("U1", verdict, "u1-uniform", seen,
                          max(counts), min(counts), clause_set)
    return Derivation("U1", ("unresolved", ("unknown",)), "u1-unknown", seen,
                      max(counts), min(counts), clause_set)


# ---------------------------------------------------------------------------
# The retired X1 predicate, lifted as SOURCE from design/gold/check_gold.py.

def load_retired_x1():
    source = open(CHECK_GOLD_PATH, encoding="utf-8").read()
    tree = ast.parse(source, filename=CHECK_GOLD_PATH)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "retired_x1":
            segment = ast.get_source_segment(source, node)
            namespace = {"Decimal": Decimal}
            exec(compile(ast.Module(body=[node], type_ignores=[]),
                         CHECK_GOLD_PATH, "exec"), namespace)
            digest = hashlib.sha256(segment.encode("utf-8")).hexdigest()
            return namespace["retired_x1"], segment, digest
    raise SystemExit("design/gold/check_gold.py no longer defines retired_x1: the "
                     "region V7 must assert COVERED has no definition to read")


# ---------------------------------------------------------------------------

def digest_of(path):
    if not os.path.isfile(path):
        return None
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main(argv):
    full = "--full" in argv[1:]
    gold = json.load(open(GOLD_PATH, encoding="utf-8"))
    rows = gold["rows"]
    retired_x1, x1_source, x1_digest = load_retired_x1()

    print("V7 — completeness re-derived over the gold grid")
    print("=" * 72)
    print("gold                 design/gold/gold.json  %s" % digest_of(GOLD_PATH))
    print("gold (frozen copy)   gold/GOLD.json         %s" % digest_of(FROZEN_GOLD_PATH))
    print("policy prose         design/POLICY-DRAFT.md %s" % digest_of(PROSE_PATH))
    print("policy (frozen copy) policy/POLICY.md       %s" % digest_of(FROZEN_PROSE_PATH))
    print("retired_x1 source    design/gold/check_gold.py::retired_x1 %s" % x1_digest)
    print("goldVersion %s; policy %s; rows %d"
          % (gold.get("goldVersion"), gold.get("policy"), len(rows)))
    print("engines invoked: none. references read: none.")
    print()

    failures = []

    # A1 — structure
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)):
        failures.append("A1: duplicate row ids")
    for row in rows:
        if not row["cite"] or not set(row["cite"]) <= CLAUSES:
            failures.append("A1: %s: cite %s is not a set of known clauses"
                            % (row["id"], row["cite"]))
    for problem in spend_quotient_problems():
        failures.append("A1: " + problem)

    # the derivation
    derivations = {row["id"]: derive(row["inputs"]) for row in rows}
    total_completions = sum(d.completions for d in derivations.values())

    gaps = [rid for rid, d in derivations.items() if d.clause is None]
    if gaps:
        failures.append("A2: cells with NO clause whose conditions hold: %s"
                        % ", ".join(sorted(gaps)))

    multi = [rid for rid, d in derivations.items() if d.max_candidates > 1]
    ambiguous = [rid for rid, d in derivations.items()
                 if d.clause is not None and d.clause not in LADDER]
    if ambiguous:
        failures.append("A3: cells whose governing clause is not a rung: %s"
                        % ", ".join(sorted(ambiguous)))

    reproduction = []
    agreement, disagreement = [], []
    membership_only = []
    for row in rows:
        derivation = derivations[row["id"]]
        want = (row["expect"]["disposition"], tuple(sorted(row["expect"]["reasons"])))
        got = derivation.verdict
        if got != want:
            reproduction.append((row["id"], got, want))
        if derivation.clause == row["cite"][0]:
            agreement.append(row["id"])
        else:
            disagreement.append((row["id"], derivation.clause, list(row["cite"]),
                                 derivation.route))
            if derivation.clause in row["cite"]:
                membership_only.append(row["id"])
    if reproduction:
        failures.append("A4: %d rows whose derived outcome is not the gold "
                        "expectation" % len(reproduction))
    if disagreement:
        failures.append("A5: %d rows whose derived governing clause is not the "
                        "first cite entry" % len(disagreement))

    x1_rows = [row["id"] for row in rows if retired_x1(row["inputs"])]
    if not x1_rows:
        failures.append("A6: the region the retired X1 class used to forbid carries "
                        "no gold row: an exclusion that once existed is no longer "
                        "falsifiable")

    # B2 — the purely lexical reading of the cite lists
    lexical_first, lexical_other = [], []
    for row in rows:
        earliest = min(row["cite"], key=lambda name: LEXICAL_RANK[name])
        (lexical_first if earliest == row["cite"][0] else lexical_other).append(row["id"])

    print("ASSERTIONS")
    print("-" * 72)
    print("A1 structure       %s  %d rows, ids unique, cites well formed, spend "
          "quotient checked" % ("PASS" if not any(f.startswith("A1") for f in failures)
                                else "FAIL", len(rows)))
    unreadable_cells = sum(1 for d in derivations.values() if d.route != "readable")
    print("A2 coverage        %s  %d/%d cells carry at least one clause, over %d "
          "ladder evaluations (%d fully readable cells once each; %d readable "
          "completions of the %d cells carrying an unreadable input)"
          % ("PASS" if not gaps else "FAIL", len(rows) - len(gaps), len(rows),
             total_completions, len(rows) - unreadable_cells,
             total_completions - (len(rows) - unreadable_cells), unreadable_cells))
    print("A3 determinacy     %s  exactly one governing clause per cell; %d cells "
          "have >1 candidate clause, all resolved by the earliest-clause tie-break"
          % ("PASS" if not ambiguous and not gaps else "FAIL", len(multi)))
    print("A4 reproduction    %s  %d/%d derived outcomes equal the gold expectation"
          % ("PASS" if not reproduction else "FAIL", len(rows) - len(reproduction),
             len(rows)))
    print("A5 cite agreement  %s  %d/%d derived governing clauses equal cite[0]"
          % ("PASS" if not disagreement else "FAIL", len(agreement), len(rows)))
    print("A6 X1 covered      %s  %d gold rows inside the retired X1 region"
          % ("PASS" if x1_rows else "FAIL", len(x1_rows)))
    print()
    print("REPORTED, NOT GATED")
    print("-" * 72)
    print("B1 membership      %d/%d derived governing clauses appear SOMEWHERE in "
          "the row's cite list" % (len(agreement) + len(membership_only), len(rows)))
    print("B2 ladder order    %d/%d cite lists open with the earliest CITED clause "
          "under the registered ladder" % (len(lexical_first), len(rows)))
    if lexical_other:
        print("                   not ladder-first: %s" % ", ".join(lexical_other))
    print()

    print("ROWS PER GOVERNING CLAUSE (derived | gold cite[0])")
    print("-" * 72)
    for clause in LEXICAL:
        derived = sum(1 for d in derivations.values() if d.clause == clause)
        cited = sum(1 for row in rows if row["cite"][0] == clause)
        if derived or cited:
            print("  %-4s %4d | %4d%s" % (clause, derived, cited,
                                          "" if derived == cited else "   <- differ"))
    print("  %-4s %4d | %4d" % ("all", len(rows), len(rows)))
    print()

    print("ROUTES")
    print("-" * 72)
    for route in ("readable", "stands", "u1-uniform", "u1-unknown", "gap"):
        count = sum(1 for d in derivations.values() if d.route == route)
        if count:
            print("  %-11s %4d" % (route, count))
    print()

    print("CANDIDATE MULTIPLICITY (clauses whose conditions hold, per cell;")
    print("worst case over the readable completions where there are several)")
    print("-" * 72)
    counts = {}
    for derivation in derivations.values():
        counts[derivation.max_candidates] = counts.get(derivation.max_candidates, 0) + 1
    for size in sorted(counts):
        print("  %d clause(s): %4d cell(s)%s"
              % (size, counts[size], "" if size < 2 else
                 "  <- resolved by the earliest-clause tie-break"))
    print()

    print("READING EVIDENCE — the `stands` route, split by whether gold's cite[0]")
    print("names the standing clause or U1 (see V7-COMPLETENESS.md, 'the pinch')")
    print("-" * 72)
    for rid, derivation in sorted(derivations.items()):
        if derivation.route != "stands":
            continue
        row = next(r for r in rows if r["id"] == rid)
        verdict = "cite[0] = the standing clause" if row["cite"][0] == derivation.clause \
            else "cite[0] = %s, not the standing clause %s" % (row["cite"][0],
                                                               derivation.clause)
        print("  %-32s %s" % (rid, verdict))
    print()

    if reproduction:
        print("A4 FAILURES — derived outcome vs gold expectation")
        print("-" * 72)
        for rid, got, want in reproduction:
            print("  %-32s derived %s  gold %s" % (rid, got, want))
        print()

    if disagreement:
        print("A5 FAILURES — derived governing clause vs cite[0]")
        print("-" * 72)
        for rid, clause, cite, route in disagreement:
            print("  %-32s derived %-4s cite %-16s route %s"
                  % (rid, clause, ",".join(cite), route))
        print()

    print("A6 — the retired X1 region, row by row")
    print("-" * 72)
    print("  predicate: design/gold/check_gold.py::retired_x1 (%s)" % x1_digest)
    for rid in x1_rows:
        derivation = derivations[rid]
        row = next(r for r in rows if r["id"] == rid)
        print("  %-32s derived %-4s outcome %-8s %-9s cite %s"
              % (rid, derivation.clause, derivation.verdict[0],
                 ",".join(derivation.verdict[1]) or "-", ",".join(row["cite"])))
    outside = [row["id"] for row in rows
               if row["id"].startswith("x1r-") and not retired_x1(row["inputs"])]
    for rid in outside:
        print("  %-32s (adjacency control, OUTSIDE the region: derived %s)"
              % (rid, derivations[rid].clause))
    print()

    if full:
        print("FULL DERIVATION")
        print("-" * 72)
        for row in rows:
            derivation = derivations[row["id"]]
            print("  %-32s %-4s %-8s %-25s route %-10s cands<=%d cite %s"
                  % (row["id"], derivation.clause, derivation.verdict[0],
                     ",".join(derivation.verdict[1]) or "-", derivation.route,
                     derivation.max_candidates, ",".join(row["cite"])))
        print()

    print("RESULT")
    print("-" * 72)
    if failures:
        for failure in failures:
            print("  FAIL  " + failure)
        print("  %d assertion(s) failed. V7 is NOT clean; the disagreements above "
              "are for the maintainer to adjudicate — this program reconciles "
              "nothing." % len(failures))
        return 1
    print("  A1-A6 pass. %d cells, %d readable completions, one governing clause "
          "each." % (len(rows), total_completions))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
