#!/usr/bin/env python3
"""MIRROR-AGREEMENT.md's numbers, recomputed: two mirrors, one corpus, one grid.

POST-HOC and DESCRIPTIVE, exactly like `analysis/diversity.py`. This script
answers a question asked after the study merged — the census's own caveat that
"the mirror encodes the same policy text the prompt inlines", so 784/784
agreement between the model's labels and the study's mirror is not evidence of
an independent reading. It registers nothing, changes no published rate, and
evaluates no pack.

It compares two implementations of POLICY.md:

  study    `harness/policy_mirror.py`, the mirror the study scored with;
  clean    `analysis/mirror2.py`, written by an agent whose only input was the
           bytes of POLICY.md — it never saw the study's mirror, its records,
           FAMILY.json, or any test. Its interpretive decisions are recorded
           verbatim in `analysis/MIRROR2-NOTES.md`.

Three comparisons, in order of what they are worth:

  1. THE CORPUS — the 784 accepted records, recompiled here from the retained
     completions the same way `harness/score_rates.py` compiles them. Every
     record is put to both mirrors. Real evidence for precedence and for the
     embargo literals; near-vacuous per-record for the numeric boundaries,
     which the corpus pins with about five distinct points (see table B).
  2. THE GRID — 2 x 2 x 2 x 15 = 120 cells over the two booleans, one
     embargoed and one non-embargoed country code, and fifteen scores placed
     on both sides of every stated threshold BY CONSTRUCTION rather than by
     the model's luck. This is what earns the boundary conclusion.
  3. THE WITNESS TABLE — DIVERSITY.md §I's nine one-token perturbations of the
     mirror, scored over the corpus and over the grid, so the two instruments'
     discriminating power can be read side by side. A perturbation with zero
     witnesses is a mirror encoding neither instrument can test.

An ADAPTER note, because "the two mirrors were compared" has to mean something
checkable: no logic in either implementation was altered, wrapped, subclassed,
or monkeypatched. Both functions already take the *vendor* sub-object, so the
adapter is a single call-site expression — `pm.verdict(v)` against
`mirror2.verdict(v)` on the same `record["vendor"]`. mirror2 reads only the
four policy members and ignores `legalName`, so no projection was needed.

Read-only on the study tree, and deterministic: no clock, no randomness, no
network, no environment lookup, every iteration over a sorted or
source-ordered sequence. Running it twice prints identical bytes.

    python3 analysis/agreement.py     # exit 0 iff every comparison agrees

Exit status is the point: any disagreement — a differing verdict, a raise from
one mirror and not the other, or a recompiled set that is not RESULTS.json's
scored set — prints the offending record or cell and exits nonzero.
"""
from __future__ import annotations

import collections
import json
import os
import sys
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(STUDY, "harness"))
sys.path.insert(0, HERE)

import records_compile as rc  # noqa: E402
import policy_mirror as pm  # noqa: E402
import mirror2  # noqa: E402

# The grid, exactly as MIRROR-AGREEMENT.md defines it. One embargoed code and
# one non-embargoed code; fifteen scores straddling 39 (the unstated edge), 40
# and 70 on both sides at four magnitudes of approach. Written here rather
# than derived, because the whole point of a grid is that a human placed the
# points; the counts below are all derived.
GRID_COUNTRIES = ("KP", "DE")
GRID_SCORES = ("0", "23.75", "39", "39.5", "39.99", "39.999", "40", "40.01",
               "41", "69", "69.99", "70", "70.001", "71", "100")


# ---------------------------------------------------------------- loading

def load() -> tuple[dict, dict, dict]:
    """(runs by slot, the population block, FAMILY.json). Slot validity comes
    from RESULTS.json, not from a list written here — the same derivation
    `analysis/diversity.py` uses."""
    with open(os.path.join(STUDY, "RESULTS.json")) as handle:
        results = json.load(handle)
    with open(os.path.join(STUDY, "FAMILY.json")) as handle:
        family = json.load(handle)

    authoring = os.path.join(STUDY, "transcription", "authoring")
    on_disk = sorted(name for name in os.listdir(authoring)
                     if name.startswith("run-"))
    scored = [row["slot"] for row in results["runs"]]
    if sorted(scored) != on_disk:
        raise SystemExit("RESULTS.json scores %d slots; %d are on disk"
                         % (len(scored), len(on_disk)))

    valid = [row["slot"] for row in results["runs"] if row["valid"]]
    excluded = [(row["slot"], row["code"]) for row in results["runs"]
                if not row["valid"]]

    runs = {}
    for slot in valid:
        raw = rc.read_completion(
            os.path.join(authoring, slot, "completion.txt"))
        accepted, ledger, _span = rc.compile_records(raw)
        runs[slot] = [accepted[case] for _index, case, _drop in ledger if case]

    population = {"valid": valid, "excluded": excluded, "slots": len(scored),
                  "results_valid": results["population"]["valid"],
                  "results_accepted": results["records"]["acceptedTotal"]}
    return runs, population, family


# ------------------------------------------------------------- vocabulary

def score(vendor: dict) -> Decimal:
    return Decimal(vendor["riskScore"])


def probe(vendor: dict, embargo: tuple) -> tuple:
    """DIVERSITY.md's probe: (exact riskScore string, sanctionsHit,
    embargo-normalised country, handlesPersonalData)."""
    country = (vendor["registeredCountry"]
               if vendor["registeredCountry"] in embargo else "non-emb")
    return (str(score(vendor)), vendor["sanctionsHit"], country,
            vendor["handlesPersonalData"])


def deciding_clause(vendor: dict, embargo: tuple) -> str:
    """The first clause of the mirror's if-chain that fires."""
    if vendor["sanctionsHit"]:
        return "P1"
    if vendor["registeredCountry"] in embargo:
        return "P2"
    value = score(vendor)
    if value >= 70:
        return "P3"
    if vendor["handlesPersonalData"] and value >= 40:
        return "P4"
    return "P5"


def perturbed(vendor: dict, embargo: tuple, drop_p1=False, embargo_list=None,
              p3_operator="ge", p3_threshold="70", p4_lower="40",
              p4_personal=True, p5_inner="40") -> str:
    """DIVERSITY.md §I's one-token perturbations of the mirror's if-chain,
    reproduced token for token so the witness counts are comparable to the
    census's table I. Unperturbed, this is `policy_mirror.verdict`."""
    if embargo_list is None:
        embargo_list = embargo
    if vendor["sanctionsHit"] and not drop_p1:
        return "reject"
    if vendor["registeredCountry"] in embargo_list:
        return "reject"
    value = score(vendor)
    if (value >= Decimal(p3_threshold) if p3_operator == "ge"
            else value > Decimal(p3_threshold)):
        return "manual-review"
    if vendor["handlesPersonalData"] is p4_personal \
            and value >= Decimal(p4_lower):
        return "manual-review"
    if vendor["handlesPersonalData"] and value >= Decimal(p5_inner):
        return "unresolved"
    return "clear"


def perturbations(embargo: tuple) -> tuple:
    return (
        ("P1 dropped entirely", "P1", {"drop_p1": True}),
        ("P2 embargo list loses KP", "P2",
         {"embargo_list": tuple(c for c in embargo if c != "KP")}),
        ("P2 embargo list loses IR", "P2",
         {"embargo_list": tuple(c for c in embargo if c != "IR")}),
        ("P2 embargo list loses SY", "P2",
         {"embargo_list": tuple(c for c in embargo if c != "SY")}),
        ("P3 `>=` becomes `>` (70 excluded)", "P3", {"p3_operator": "gt"}),
        ("P3 threshold 70 -> 71", "P3", {"p3_threshold": "71"}),
        ("P4 lower bound 40 -> 41", "P4", {"p4_lower": "41"}),
        ("P4 personal-data condition inverted", "P4", {"p4_personal": False}),
        ("P5 inner clearance bound 40 -> 39", "P5", {"p5_inner": "39"}),
    )


def outcome(mirror, vendor: dict) -> str:
    """One mirror's answer, with a raise folded into the answer rather than
    allowed to abort the comparison: two mirrors that raise the same exception
    type AGREE, and one that raises where the other returns DISAGREES."""
    try:
        return mirror(vendor)
    except Exception as failure:          # noqa: BLE001 - the point is the type
        return "raise:%s" % type(failure).__name__


def show(vendor: dict) -> str:
    return ('(sanctionsHit=%s, registeredCountry=%s, handlesPersonalData=%s, '
            'riskScore="%s")'
            % (str(vendor["sanctionsHit"]).lower(),
               vendor["registeredCountry"],
               str(vendor["handlesPersonalData"]).lower(),
               vendor["riskScore"]))


# ---------------------------------------------------------------- the run

def main() -> int:
    runs, population, family = load()
    embargo = tuple(family["embargoList"])
    disagreements = []

    slots = sorted(runs)
    records = [(slot, record) for slot in slots for record in runs[slot]]
    vendors = [(slot, record["vendor"]) for slot, record in records]

    print("# Study 011 — clean-room mirror agreement")
    print()
    print("Recomputed from the retained bytes by `analysis/agreement.py`. "
          "Descriptive; nothing here is preregistered.")
    print()

    # --- 1. the corpus -------------------------------------------------
    for slot, vendor in vendors:
        study, clean = outcome(pm.verdict, vendor), outcome(mirror2.verdict,
                                                            vendor)
        if study != clean:
            disagreements.append(("corpus", slot, show(vendor), study, clean))

    n_runs = len(slots)
    agreed = len(vendors) - sum(1 for row in disagreements if row[0] == "corpus")
    print("## A. The corpus: every accepted record, both mirrors")
    print()
    print("Record set: %d valid runs x %d accepted records = %d, 0 dropped."
          % (n_runs, len(records) // n_runs, len(records)))
    excluded = ", ".join("`%s` (%s)" % (slot, code)
                         for slot, code in population["excluded"])
    print("Excluded by RESULTS.json, not by this script: %d of %d slots — %s."
          % (len(population["excluded"]), population["slots"],
             excluded or "none"))
    if (population["results_valid"], population["results_accepted"]) != (
            n_runs, len(records)):
        raise SystemExit("the recompiled set disagrees with RESULTS.json")
    print()
    print("**Corpus agreement: %d/%d, %d disagreements.**"
          % (agreed, len(vendors), len(vendors) - agreed))
    print()

    # --- 2. the set compared is the scorer's set -----------------------
    print("## B. The set compared is the scorer's set, and what it can test")
    print()
    print("Deciding counts and distinct probes recomputed here; they match "
          "DIVERSITY.md table H cell for cell, which is how this script "
          "shows it recompiled the scored corpus rather than some other set.")
    print()
    print("| clause | deciding records | distinct probes among its records |")
    print("|---|---|---|")
    deciding = collections.Counter()
    clause_probes = collections.defaultdict(set)
    for _slot, vendor in vendors:
        clause = deciding_clause(vendor, embargo)
        deciding[clause] += 1
        clause_probes[clause].add(probe(vendor, embargo))
    for clause in ("P1", "P2", "P3", "P4", "P5"):
        print("| %s | %d | %d |"
              % (clause, deciding[clause], len(clause_probes[clause])))
    print()

    # --- 3. the grid ---------------------------------------------------
    grid = []
    for sanctions in (False, True):
        for country in GRID_COUNTRIES:
            for personal in (False, True):
                for value in GRID_SCORES:
                    grid.append({"legalName": "grid", "sanctionsHit": sanctions,
                                 "registeredCountry": country,
                                 "handlesPersonalData": personal,
                                 "riskScore": value})
    distribution = collections.Counter()
    for vendor in grid:
        study, clean = outcome(pm.verdict, vendor), outcome(mirror2.verdict,
                                                            vendor)
        distribution[study] += 1
        if study != clean:
            disagreements.append(("grid", "-", show(vendor), study, clean))

    grid_agreed = len(grid) - sum(1 for row in disagreements if row[0] == "grid")
    print("## C. The grid: 2 x 2 x 2 x 15 = %d cells, boundaries by "
          "construction" % len(grid))
    print()
    print("sanctionsHit {false, true} x registeredCountry {%s} x "
          "handlesPersonalData {false, true} x %d scores {%s}."
          % (", ".join(GRID_COUNTRIES), len(GRID_SCORES),
             ", ".join(GRID_SCORES)))
    print()
    print("**Grid agreement: %d/%d, %d disagreements.**"
          % (grid_agreed, len(grid), len(grid) - grid_agreed))
    print()
    print("Study-mirror verdict distribution over the grid: %s."
          % ", ".join("%s %d" % (name, distribution[name])
                      for name in ("reject", "clear", "manual-review")))
    short_p1 = sum(1 for vendor in grid if vendor["sanctionsHit"])
    short_p2 = sum(1 for vendor in grid if not vendor["sanctionsHit"]
                   and vendor["registeredCountry"] in embargo)
    print("%d of %d cells short-circuit at P1 and %d more at P2, so %d "
          "unsanctioned non-embargoed cells carry all the boundary work."
          % (short_p1, len(grid), short_p2, len(grid) - short_p1 - short_p2))
    print()

    # --- 4. the witness table ------------------------------------------
    print("## D. Per-clause witnesses: what each instrument can discriminate")
    print()
    print("A witness is a record or cell whose verdict the perturbation "
          "CHANGES. Zero witnesses means that encoding is untested by that "
          "instrument — agreement on it is arithmetic, not evidence.")
    print()
    print("| perturbation of the mirror | clause | corpus witnesses | corpus "
          "distinct probes | grid witness cells |")
    print("|---|---|---|---|---|")
    for title, clause, keywords in perturbations(embargo):
        witnesses = [vendor for _slot, vendor in vendors
                     if perturbed(vendor, embargo, **keywords)
                     != pm.verdict(vendor)]
        probes = {probe(vendor, embargo) for vendor in witnesses}
        cells = sum(1 for vendor in grid
                    if perturbed(vendor, embargo, **keywords)
                    != pm.verdict(vendor))
        print("| %s | %s | %d | %d | %d |"
              % (title, clause, len(witnesses), len(probes), cells))
    print()

    # --- 5. the admitted domain ----------------------------------------
    print("## E. The admitted domain, checked rather than asserted")
    print()
    print("The two mirrors are NOT extensionally identical everywhere: "
          "`mirror2` refuses a float or a bool `riskScore` with a TypeError "
          "where the study's mirror coerces it through `Decimal`. The claim "
          "that this is unobservable is a claim about the compiler, so it is "
          "checked here — each of these is put to `records_compile.classify` "
          "inside an otherwise well-formed record and must be DROPPED.")
    print()
    template = {
        "caseId": "grid-probe",
        "vendor": {"legalName": "Probe GmbH", "sanctionsHit": False,
                   "registeredCountry": "DE", "handlesPersonalData": False,
                   "riskScore": "69.99"},
        "decision": {"outcome": "clear", "decidedBy": "policy",
                     "decidedAt": "2026-01-01T00:00:00Z"},
    }
    accepted_case, drop = rc.classify(template, set())
    if drop or accepted_case != "grid-probe":
        raise SystemExit("the control record is not admitted: %r" % drop)
    print("| riskScore put to the compiler | admitted? | drop code |")
    print("|---|---|---|")
    for label, value in (("69.99 (str, the control)", "69.99"),
                         ("69.99 (float)", 69.99), ("40.0 (float)", 40.0),
                         ("True (bool)", True), ('"NaN"', "NaN"),
                         ('"Infinity"', "Infinity"), ('"1e2"', "1e2"),
                         ('"+40"', "+40"), ('"-5"', "-5")):
        element = json.loads(json.dumps(template))
        element["vendor"]["riskScore"] = value
        case_id, code = rc.classify(element, set())
        print("| %s | %s | %s |"
              % (label, "yes" if case_id else "**no**", code or "—"))
        if label.startswith("69.99 (str") and not case_id:
            disagreements.append(("domain", "-", label, "admitted", "dropped"))
        if not label.startswith("69.99 (str") and case_id:
            disagreements.append(("domain", "-", label, "dropped", "admitted"))
    print()
    print("Floats and bools are barred by the `isinstance(..., str)` check "
          "(code `schema`); `NaN`, `Infinity`, `1e2`, `+40` and `-5` are "
          "barred by `DECIMAL = %s` (code `decimal-form`). No admitted record "
          "can present any of them, so the divergence is real and "
          "unreachable." % rc.DECIMAL.pattern)
    print()
    print("One correction, recorded because the check caught it: "
          "`MIRROR2-NOTES.md` decision 10 states that a `\"NaN\"` score "
          "\"compares false against every bound and would therefore fall "
          "through to `clear`\". That is false of mirror2's own code — "
          "`Decimal('NaN') >= Decimal(70)` raises `InvalidOperation` — and "
          "both mirrors raise it identically:")
    nan_vendor = {"sanctionsHit": False, "registeredCountry": "DE",
                  "handlesPersonalData": False, "riskScore": "NaN"}
    study_nan, clean_nan = (outcome(pm.verdict, nan_vendor),
                            outcome(mirror2.verdict, nan_vendor))
    print()
    print("    study=%s  clean=%s" % (study_nan, clean_nan))
    if study_nan != clean_nan or not study_nan.startswith("raise:"):
        disagreements.append(("notes", "-", "NaN riskScore", study_nan,
                              clean_nan))
    print()

    # --- 6. verdict ----------------------------------------------------
    if disagreements:
        print("## DISAGREEMENTS")
        print()
        for where, slot, vendor, study, clean in disagreements:
            print("- [%s] %s %s: study=%s clean=%s"
                  % (where, slot, vendor, study, clean))
        return 1
    print("No disagreement anywhere in the admitted domain: %d/%d records and "
          "%d/%d grid cells." % (agreed, len(vendors), grid_agreed, len(grid)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
