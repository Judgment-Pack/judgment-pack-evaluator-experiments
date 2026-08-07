#!/usr/bin/env python3
"""DIVERSITY.md's tables, recomputed from Study 011's retained bytes.

POST-HOC and DESCRIPTIVE. This script answers a reader's question asked after
the study merged — how much test VARIETY is behind a coverage rate of 49/49 —
and it registers nothing, changes no published rate, and evaluates no pack.

Read-only on the study tree, and deterministic: no clock, no randomness, no
network, no environment lookup, every iteration over a sorted or
source-ordered sequence. Running it twice prints identical bytes; the tables
it prints are the tables DIVERSITY.md carries.

    python3 analysis/diversity.py

The record set is the scored set, derived rather than asserted: RESULTS.json
names each slot valid or pipeline-invalid with the code that made it so, and
this script keeps exactly the valid ones. In this batch that excludes one
slot, `run-026`, code `transcript-refused` — the name is printed from
RESULTS.json, never hard-coded, so a re-scored tree with a different invalid
slot excludes that one instead. Each kept slot's completion.txt is read
byte-exactly and compiled by the study's own ported compiler
(`harness/records_compile.py`); labels come from the study's own mirror
(`harness/policy_mirror.py`) and class membership from FAMILY.json's
predicates. Nothing here re-runs a model or rewrites a retained byte.

DEFINITIONS, stated because they are choices this analysis makes and the
preregistration does not:

  band            the policy's three decision regions on riskScore:
                  `<40`, `[40,70)`, `>=70`.
  embargoed?      registeredCountry in KP/IR/SY (FAMILY.json's embargoList).
  profile (i)     (sanctionsHit, embargoed?, handlesPersonalData, band) — a
                  semantic "same test" key.
  probe           (exact riskScore string, sanctionsHit, embargo-normalised
                  country, handlesPersonalData). Non-embargoed countries
                  collapse to one token because the policy cannot distinguish
                  CA from DE; embargoed codes are kept. The count with the
                  exact country code is also reported: it is a count of
                  surface variation, not of test variation.
  deciding clause the first clause of the mirror's if-chain that fires
                  (P1 sanctions, P2 embargo, P3 >=70, P4 personal & >=40,
                  P5 otherwise clear).
  witness         a record whose verdict a one-token perturbation of the
                  mirror would CHANGE. Deciding counts say how busy a clause
                  is; witness counts say how much of the corpus would notice
                  if its encoding were wrong.
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

import records_compile as rc  # noqa: E402
import policy_mirror as pm  # noqa: E402

# The three edges distances are measured to. 40 and 70 are STATED in the
# policy text the prompt inlines; 39 is the unstated lower edge of class 5's
# window, named by FAMILY.json and by nothing the model was shown. Which are
# stated is a fact about the policy text, so it is written here rather than
# derived; the numbers below are all derived.
THRESHOLDS = ((Decimal("39"), "unstated"),
              (Decimal("40"), "stated"),
              (Decimal("70"), "stated"))


# ---------------------------------------------------------------- loading

def load() -> tuple[dict, list, dict, dict]:
    """(runs by slot, class definitions, the results population block,
    FAMILY.json). Slot validity comes from RESULTS.json, not from a list
    written here."""
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

    population = {"valid": valid, "excluded": excluded,
                  "slots": len(scored),
                  "results_valid": results["population"]["valid"],
                  "results_accepted": results["records"]["acceptedTotal"],
                  "results_h": results["labelAccuracy"]["h"],
                  "results_q": results["labelAccuracy"]["q"]}
    return runs, family["mutations"], population, family


# ------------------------------------------------------------- vocabulary

def embargoed(vendor: dict, embargo: tuple) -> bool:
    return vendor["registeredCountry"] in embargo


def score(vendor: dict) -> Decimal:
    return Decimal(vendor["riskScore"])


def band(vendor: dict) -> str:
    value = score(vendor)
    if value >= 70:
        return ">=70"
    if value >= 40:
        return "[40,70)"
    return "<40"


def profile_i(vendor: dict, embargo: tuple) -> tuple:
    return (vendor["sanctionsHit"], embargoed(vendor, embargo),
            vendor["handlesPersonalData"], band(vendor))


def probe(vendor: dict, embargo: tuple) -> tuple:
    country = (vendor["registeredCountry"] if embargoed(vendor, embargo)
               else "non-emb")
    return (str(score(vendor)), vendor["sanctionsHit"], country,
            vendor["handlesPersonalData"])


def probe_exact(vendor: dict) -> tuple:
    return (str(score(vendor)), vendor["sanctionsHit"],
            vendor["registeredCountry"], vendor["handlesPersonalData"])


def vendor_tuple(vendor: dict) -> tuple:
    return (vendor["legalName"], vendor["sanctionsHit"],
            vendor["registeredCountry"], vendor["handlesPersonalData"],
            vendor["riskScore"])


def facts_tuple(vendor: dict) -> tuple:
    return (vendor["sanctionsHit"], vendor["registeredCountry"],
            vendor["handlesPersonalData"], str(score(vendor)))


def deciding_clause(vendor: dict, embargo: tuple) -> str:
    """The first clause of the mirror's if-chain that fires. Kept in lockstep
    with policy_mirror.verdict by test_diversity.py, which asserts the clause
    this returns implies the verdict the mirror returns."""
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


def show_probe(key: tuple) -> str:
    value, sanctions, country, personal = key
    return '("%s", %s, %s, %s)' % (value, str(sanctions).lower(), country,
                                   str(personal).lower())


def show_multiset(counter: collections.Counter) -> str:
    """Exact riskScore values, ascending, as `39.99 x58`."""
    if not counter:
        return "none"
    return ", ".join("%s x%d" % (value, count) for value, count
                     in sorted(counter.items(), key=lambda kv: Decimal(kv[0])))


def cover_greedily(probe_runs: dict, n_runs: int) -> int:
    """How few probes suffice to cover every covered run. Greedy, with a
    deterministic tie-break on the probe key, so the count is reproducible;
    it is an upper bound on the true minimum, and it is exact wherever it
    equals the number of probes."""
    remaining = set()
    for runs in probe_runs.values():
        remaining |= runs
    chosen = 0
    while remaining:
        best = max(sorted(probe_runs), key=lambda key: len(probe_runs[key] & remaining))
        gain = probe_runs[best] & remaining
        if not gain:
            break
        remaining -= gain
        chosen += 1
    return chosen


# ---------------------------------------------------------------- the run

def main() -> int:
    runs, mutations, population, family = load()
    embargo = tuple(family["embargoList"])

    slots = sorted(runs)
    n_runs = len(slots)
    records = [(slot, record) for slot in slots for record in runs[slot]]
    vendors = [(slot, record["vendor"]) for slot, record in records]

    def concordant(record: dict) -> bool:
        return record["decision"]["outcome"] == pm.verdict(record["vendor"])

    n_h = sum(1 for _slot, record in records if concordant(record))
    n_q = len(records) - n_h

    print("# Study 011 — post-hoc diversity census")
    print()
    print("Recomputed from the retained bytes by `analysis/diversity.py`. "
          "Descriptive; nothing here is preregistered.")
    print()
    print("Record set: %d valid runs x %d accepted records = %d, 0 dropped; "
          "H = %d, Q = %d."
          % (n_runs, len(records) // n_runs, len(records), n_h, n_q))
    excluded = ", ".join("`%s` (%s)" % (slot, code)
                         for slot, code in population["excluded"])
    print("Excluded by RESULTS.json, not by this script: %d of %d slots — %s."
          % (len(population["excluded"]), population["slots"],
             excluded or "none"))
    if (population["results_valid"], population["results_accepted"],
            population["results_h"], population["results_q"]) != (
            n_runs, len(records), n_h, n_q):
        raise SystemExit("the recompiled set disagrees with RESULTS.json")
    print()

    # --- 1. corpus distance buckets ------------------------------------
    edges = [value for value, _stated in THRESHOLDS]
    buckets = collections.Counter()
    for _slot, vendor in vendors:
        distance = min(abs(score(vendor) - edge) for edge in edges)
        if distance == 0:
            buckets["exactly on a threshold"] += 1
        elif distance <= Decimal("0.001"):
            buckets["0 < d <= 0.001"] += 1
        elif distance <= Decimal("0.01"):
            buckets["0.001 < d <= 0.01"] += 1
        elif distance <= Decimal("0.1"):
            buckets["0.01 < d <= 0.1"] += 1
        elif distance <= Decimal("1"):
            buckets["0.1 < d <= 1"] += 1
        else:
            buckets["d > 1"] += 1
    order = ["exactly on a threshold", "0 < d <= 0.001", "0.001 < d <= 0.01",
             "0.01 < d <= 0.1", "0.1 < d <= 1", "d > 1"]

    print("## A. Every record's distance to the nearest threshold")
    print()
    print("| min distance to {39, 40, 70} | records |")
    print("|---|---|")
    for label in order:
        print("| %s | %d |" % (label, buckets[label]))
    print()
    hugging = sum(buckets[label] for label in order[:3])
    gap = buckets["0.01 < d <= 0.1"] + buckets["0.1 < d <= 1"]
    print("%d of %d (%.1f%%) sit on a threshold or within 0.01 of one. "
          "Exactly %d land in the human-sized gap (0.01, 1.0]."
          % (hugging, len(vendors), 100.0 * hugging / len(vendors), gap))
    print()

    # --- 2. per-threshold value multisets within 1.0 --------------------
    print("## B. Within 1.0 of each threshold, both sides, exact values")
    print()
    print("| threshold | strictly below within 1.0 | n | exactly at | "
          "strictly above within 1.0 | n |")
    print("|---|---|---|---|---|---|")
    for edge, stated in THRESHOLDS:
        below, above, at = collections.Counter(), collections.Counter(), 0
        for _slot, vendor in vendors:
            value = score(vendor)
            if value == edge:
                at += 1
            elif edge - 1 <= value < edge:
                below[str(value)] += 1
            elif edge < value <= edge + 1:
                above[str(value)] += 1
        print("| %s (%s) | %s | %d | %d | %s | %d |"
              % (edge, stated, show_multiset(below), sum(below.values()), at,
                 show_multiset(above), sum(above.values())))
    print()

    # --- 3. per-class distinct probes -----------------------------------
    print("## C. Distinct probes per class")
    print()
    print("Probe = (exact riskScore, sanctionsHit, embargo-normalised "
          "country, handlesPersonalData), over the H records matching the "
          "class predicate.")
    print()
    print("| class | predicate (FAMILY.json prose) | H records | runs "
          "covering | distinct riskScore values | DISTINCT PROBES | distinct "
          "probes w/ exact country | modal probe | modal probe's run share | "
          "runs still covered if the modal probe is removed | min probes "
          "needed to cover every covered run | probes used by exactly 1 run |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")

    per_class = {}
    for mutation in mutations:
        members = [(slot, record["vendor"]) for slot, record in records
                   if pm.predicate_matches(mutation["predicate"],
                                           record["vendor"])
                   and concordant(record)]
        probe_runs = collections.defaultdict(set)
        for slot, vendor in members:
            probe_runs[probe(vendor, embargo)].add(slot)
        covering = {slot for slot, _vendor in members}
        widest = max(len(key_runs) for key_runs in probe_runs.values())
        tied = [key for key in sorted(probe_runs)
                if len(probe_runs[key]) == widest]
        modal = tied[0]
        without_modal = set()
        for key, key_runs in probe_runs.items():
            if key != modal:
                without_modal |= key_runs
        entry = {
            "records": len(members),
            "runs": len(covering),
            "values": len({str(score(vendor)) for _slot, vendor in members}),
            "probes": len(probe_runs),
            "probes_exact": len({probe_exact(vendor)
                                 for _slot, vendor in members}),
            "modal": modal,
            "modal_runs": len(probe_runs[modal]),
            "without_modal": len(without_modal),
            "min_cover": cover_greedily(probe_runs, n_runs),
            "singletons": sum(1 for key_runs in probe_runs.values()
                              if len(key_runs) == 1),
            "probe_runs": probe_runs,
            "tied": tied,
        }
        per_class[mutation["index"]] = entry
        print("| %d | %s | %d | %d/%d | %d | **%d** | %d | %s | %d/%d | %d | "
              "%d | %d |"
              % (mutation["index"], mutation["predicateProse"],
                 entry["records"], entry["runs"], n_runs, entry["values"],
                 entry["probes"], entry["probes_exact"], show_probe(modal),
                 entry["modal_runs"], n_runs, entry["without_modal"],
                 entry["min_cover"], entry["singletons"]))
    print()
    for index in sorted(per_class):
        tied = per_class[index]["tied"]
        if len(tied) > 1:
            print("Class %d's modal probe is a tie at %d/%d runs — %s. The "
                  "table names the first in sort order; every one of them is "
                  "listed in D."
                  % (index, per_class[index]["modal_runs"], n_runs,
                     " and ".join(show_probe(key) for key in tied)))
            print()

    # --- 4. the all-49-run probes and the collapse ----------------------
    print("## D. Probes present in every covered run, and the collapse "
          "without them")
    print()
    print("| class | a probe present in all %d runs | records it carries | "
          "runs still covered if it is deleted |" % n_runs)
    print("|---|---|---|---|")
    for index in sorted(per_class):
        entry = per_class[index]
        universal = [key for key in sorted(entry["probe_runs"])
                     if len(entry["probe_runs"][key]) == n_runs]
        if not universal:
            print("| %d | none — the widest reaches %d/%d runs | — | — |"
                  % (index, entry["modal_runs"], n_runs))
            continue
        for key in universal:
            carried = sum(1 for _slot, record in records
                          if concordant(record)
                          and probe(record["vendor"], embargo) == key
                          and pm.predicate_matches(
                              mutations[index]["predicate"],
                              record["vendor"]))
            remainder = set()
            for other, other_runs in entry["probe_runs"].items():
                if other != key:
                    remainder |= other_runs
            print("| %d | %s | %d | %d |"
                  % (index, show_probe(key), carried, len(remainder)))
    print()

    # --- 5. per-run distinctness and cross-run identity ------------------
    distinct_per_run = collections.Counter()
    redundant_per_run = collections.Counter()
    for slot in slots:
        counted = collections.Counter(profile_i(record["vendor"], embargo)
                                      for record in runs[slot])
        distinct_per_run[len(counted)] += 1
        redundant_per_run[sum(n - 1 for n in counted.values() if n > 1)] += 1
    per_run_size = len(records) // n_runs
    mean_redundant = sum(key * count for key, count
                         in redundant_per_run.items()) / n_runs

    print("## E. Within a run: how many of the %d records are different tests"
          % per_run_size)
    print()
    print("| distinct profiles (def (i)) in a run, of %d | runs |"
          % per_run_size)
    print("|---|---|")
    for value, count in sorted(distinct_per_run.items()):
        print("| %d | %d |" % (value, count))
    print()
    print("| redundant records in a run | runs |")
    print("|---|---|")
    for value, count in sorted(redundant_per_run.items()):
        print("| %d | %d |" % (value, count))
    print()
    print("Mean redundant records per run: %.3f of %d (%.1f%%)."
          % (mean_redundant, per_run_size,
             100.0 * mean_redundant / per_run_size))
    print()

    signature_i = collections.Counter(
        tuple(sorted(collections.Counter(
            profile_i(record["vendor"], embargo)
            for record in runs[slot]).items(), key=repr))
        for slot in slots)
    signature_probe = collections.Counter(
        tuple(sorted(collections.Counter(
            probe(record["vendor"], embargo)
            for record in runs[slot]).items(), key=repr))
        for slot in slots)

    print("## F. Across runs: whole-run identity")
    print()
    print("| run signature | distinct signatures over %d runs | runs sharing "
          "a signature with another run | group sizes |" % n_runs)
    print("|---|---|---|---|")
    for label, counted in (("profile multiset, def (i)", signature_i),
                           ("probe multiset (exact value + tuple)",
                            signature_probe)):
        shared = sum(count for count in counted.values() if count > 1)
        groups = sorted((count for count in counted.values() if count > 1),
                        reverse=True)
        singletons = sum(1 for count in counted.values() if count == 1)
        sizes = (", ".join(str(size) for size in groups) +
                 (", then %d singletons" % singletons if singletons else "")
                 ) if groups else "all singletons"
        print("| %s | %d | %d (%.1f%%) | %s |"
              % (label, len(counted), shared, 100.0 * shared / n_runs, sizes))
    print()

    # --- 6. duplicates ---------------------------------------------------
    def duplicate_row(label: str, key) -> str:
        corpus = collections.Counter(key(record) for _slot, record in records)
        within = 0
        for slot in slots:
            counted = collections.Counter(key(record) for record in runs[slot])
            within += sum(n - 1 for n in counted.values() if n > 1)
        in_repeat = sum(n for n in corpus.values() if n > 1)
        return "| %s | %d | %d | %d | %d | %d |" % (
            label, len(corpus), sum(1 for n in corpus.values() if n > 1),
            in_repeat, len(records) - len(corpus), within)

    print("## G. Duplicates, at four levels")
    print()
    print("| level | distinct keys of %d records | keys occurring more than "
          "once | records in a repeated key | redundant copies | repeats "
          "WITHIN a run |" % len(records))
    print("|---|---|---|---|---|---|")
    print(duplicate_row("exact vendor tuple (all five members)",
                        lambda record: vendor_tuple(record["vendor"])))
    print(duplicate_row("whole record (caseId + vendor + decision)",
                        lambda record: json.dumps(record, sort_keys=True)))
    print(duplicate_row("facts only (vendor tuple minus legalName)",
                        lambda record: facts_tuple(record["vendor"])))
    print(duplicate_row("semantic profile (i)",
                        lambda record: profile_i(record["vendor"], embargo)))
    print()

    tuples = collections.Counter(vendor_tuple(record["vendor"])
                                 for _slot, record in records)
    # The head is cut at 4 copies rather than at a rank, so no arbitrary
    # tie-break decides which of the many 3-copy tuples gets printed.
    head = sorted(((key, count) for key, count in tuples.items() if count >= 4),
                  key=lambda kv: (-kv[1], repr(kv[0])))
    print("| vendor tuple repeated 4 or more times | copies |")
    print("|---|---|")
    for key, count in head:
        name, sanctions, country, personal, value = key
        print('| ("%s", %s, %s, %s, "%s") | %d |'
              % (name, str(sanctions).lower(), country,
                 str(personal).lower(), value, count))
    print()
    tail = sum(1 for count in tuples.values() if 2 <= count <= 3)
    print("A further %d tuples recur at 2 or 3 copies each." % tail)
    print()

    # --- 7. per-clause deciding counts ------------------------------------
    clause_records = collections.Counter(deciding_clause(vendor, embargo)
                                         for _slot, vendor in vendors)
    clause_runs = collections.Counter()
    for slot in slots:
        for name in sorted({deciding_clause(record["vendor"], embargo)
                            for record in runs[slot]}):
            clause_runs[name] += 1
    clause_text = {
        "P1": "sanctions hit -> reject",
        "P2": "embargoed country -> reject",
        "P3": "score >= 70 -> manual review",
        "P4": "personal data and 40 <= score < 70 -> manual review",
        "P5": "otherwise -> clear",
    }
    print("## H. Which clause decides each record")
    print()
    print("| clause | text | records | share | runs with >=1 | distinct "
          "probes among its records |")
    print("|---|---|---|---|---|---|")
    for name in ("P1", "P2", "P3", "P4", "P5"):
        probes = {probe(vendor, embargo) for _slot, vendor in vendors
                  if deciding_clause(vendor, embargo) == name}
        print("| %s | %s | %d | %.2f%% | %d/%d | %d |"
              % (name, clause_text[name], clause_records[name],
                 100.0 * clause_records[name] / len(vendors),
                 clause_runs[name], n_runs, len(probes)))
    outcomes = collections.Counter(record["decision"]["outcome"]
                                   for _slot, record in records)
    print()
    print("Outcome distribution: " + ", ".join(
        "%s %d" % (name, outcomes[name]) for name in sorted(outcomes)) + ".")
    print()

    # --- 8. witness counts: where a mirror bug could hide ------------------
    def perturbed(vendor: dict, drop_p1=False, embargo_list=embargo,
                  p3_operator="ge", p3_threshold="70", p4_lower="40",
                  p4_personal=True, p5_inner="40") -> str:
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

    perturbations = (
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
    print("## I. Where a mirror-encoding bug could hide: witnesses, not "
          "deciding counts")
    print()
    print("| perturbation of the mirror | clause | witness records | runs "
          "with >=1 witness | distinct probes among the witnesses | runs "
          "whose only witness is a single record |")
    print("|---|---|---|---|---|---|")
    for title, clause, keywords in perturbations:
        witnesses = [(slot, vendor) for slot, vendor in vendors
                     if perturbed(vendor, **keywords) != pm.verdict(vendor)]
        by_run = collections.Counter(slot for slot, _vendor in witnesses)
        probes = {probe(vendor, embargo) for _slot, vendor in witnesses}
        marker = "**%d**" % len(probes) if len(probes) <= 2 else str(len(probes))
        print("| %s | %s | %d | %d | %s | %d |"
              % (title, clause, len(witnesses), len(by_run), marker,
                 sum(1 for count in by_run.values() if count == 1)))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
