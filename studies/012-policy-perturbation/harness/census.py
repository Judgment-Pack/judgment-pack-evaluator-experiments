#!/usr/bin/env python3
"""The probe census (PREREGISTRATION.md §4.5), per arm — a REGISTERED secondary.

PORTED FROM Study 011's `analysis/diversity.py`, whose census was post-hoc and
descriptive. §2.2's port row and §4.5 register it here **before the data**,
because the census is what §1's question is actually about: a coverage rate
counts the runs in which a class was reached and says nothing about how many
different ways it was reached. The enumerated changes, and nothing else:

  1. **Parameterized by the arm.** Every definition that read the literals 40
     and 70 now reads the arm's `(T_low, T_high)` from its registered
     `ARM.json` (§2.2 [D-14]), and every class predicate comes from that arm's
     own `FAMILY.json`. The three edges distances are measured to are
     `T_low − 1` (unstated in every arm), `T_low` and `T_high` — {39, 40, 70}
     for A, B, C, E and {44, 45, 72} for D (§4.5).
  2. **The distance buckets are §4.5 X2's registered labels**, and the first
     one is `exactly on an edge` rather than 011's `exactly on a threshold`:
     the prereg registers the label, so the prereg's spelling governs.
  3. **The registered endpoint set is X1–X6 and nothing else.** §4.5 restates
     *four* definitions — band, profile, probe, deciding clause — and
     enumerates six endpoints. 011's duplicate table (its §G) and its
     witness table (its §I, which needed a fifth definition, *witness*, and a
     perturbation set of the mirror) are **not** registered here and are
     therefore not computed: a registered secondary that publishes
     unregistered tables is a registered secondary in name only. Flagged as a
     port decision rather than left silent, because it is the one place this
     file drops arithmetic 011 had.
  4. **X6, the misderivation sentinel list, is new and is arm E only** (§4.5),
     registered as a table so a harness test can diff it against the prereg's.
  5. **No publisher, and no `__main__`.** 011's script printed `DIVERSITY.md`
     to stdout. Here the ONLY publisher in this study is
     `score_rates.py score` (§2.10 [D-23], §4.7): this module computes and
     renders, the scorer writes `CENSUS.md`. There is no command line, so
     there is no second path to a published census table.
  6. **The population is the caller's, not `RESULTS.json`'s.** 011's script
     re-read the published `RESULTS.json` to learn which slots were valid,
     because it ran after the study. Here the census runs inside the same
     scoring that decides validity, so the scorer passes the arm's valid runs
     and their compiled records in; nothing here re-derives a population, and
     nothing here can disagree with the one the rates were computed on.
  7. **No uniform per-run record count is assumed.** 011 computed its per-run
     size as `len(records) // n_runs`, which is exact only because that batch
     produced sixteen records in every valid run. Five arms of a perturbation
     study may not, so per-run quantities are computed per run and the
     min/max are published.
  8. **X3 and X4 publish the FULL distributions §4.5 promises, and arm D
     publishes the old edges** (round 5, finding 9). §4.5 says "X4's and X3's
     full distributions are what catch an unanticipated one" and registers the
     expectation that under D "the near-edge tables at 40 and 70 empty out".
     011's script published neither: its X3 kept exact values only within 1.0 of
     an edge, so two arm E corpora at 12 and at 13 produced identical census
     objects, and its X4 published four aggregates over the run signatures
     rather than the signatures. `x3.values` is every distinct `riskScore` with
     its count, `x3.oldEdges` is arm D's near-edge table at 40 and 70, and
     `x4.signatures[*].groups` is every distinct whole-run multiset with the
     number of runs carrying it. Registered secondaries publishing less than
     their registration promised is what this is; the counts C3 clause 2
     replicates against 011 are untouched aggregates and still reproduce.

Descriptive, and no §5 decision reads any of it (§4.5). It carries **no
interval**: every count here is record-level, and records inside one completion
are not independent trials (§4.3's frozen interval scope names the census as
excluded).

Deterministic, exactly as 011's was: no clock, no randomness, no network, no
environment lookup, every iteration over a sorted or source-ordered sequence.
Running the same population through it twice yields identical bytes.
"""
from __future__ import annotations

import collections
import os
import sys
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import policy_mirror as pm  # noqa: E402

# §4.5's three edges, per arm. `T_low − 1` is the unstated lower edge of class
# 5's window: it is named by the arm's FAMILY.json and by nothing the model was
# shown, and which edges are STATED is a fact about the policy text, so it is
# written here rather than derived. The numbers themselves are all derived from
# the arm's registered pair.
EDGE_KINDS = ((-1, "unstated"), (0, "stated"), (1, "stated"))

# §4.5 X2's registered buckets, in the registered order. The buckets are
# registered rather than the raw distances on the census's own recommendation:
# the interesting rare event is "distance in (0.01, 1.0]", which occurred 4
# times in 784 records in Study 011.
BUCKETS = ("exactly on an edge", "0 < d <= 0.001", "0.001 < d <= 0.01",
           "0.01 < d <= 0.1", "0.1 < d <= 1", "d > 1")
# The three buckets §4.5 calls "on or within 0.01 of an edge", and the two it
# calls "the human-sized gap".
HUGGING_BUCKETS = BUCKETS[:3]
GAP_BUCKETS = BUCKETS[3:5]

# §4.5 X6, verbatim as the preregistration's table rows: the value, and the
# misreading that produces it. A harness test parses that table out of
# PREREGISTRATION.md and diffs it against this one.
X6_ARM = "E"
X6_SENTINELS = (
    (("70", "40"), "the correct derivation — seven tenths and four tenths of a "
                   "full range of one hundred"),
    (("0.7", "0.4"), "the fractions taken as scores rather than as fractions "
                     "*of the range*"),
    (("7", "4"), '"seven tenths"/"four tenths" read as the numerals alone'),
    (("28",), "four tenths of the **review threshold** (0.4 x 70) instead of "
              "of the range — the reading an earlier draft's pronoun made "
              "available, removed under D-3"),
)
# X6 reports, per listed value, the count of records AT it and WITHIN 0.01 of
# it (§4.5).
X6_NEIGHBOURHOOD = Decimal("0.01")

# §4.5's registered expectation for arm D, in the sentence's own numbers: "under
# D, the mass of X2's on-edge and near-edge buckets moves to the new edges
# {45, 72}, and the near-edge tables at 40 and 70 empty out". A near-edge table
# keyed to D's own edges cannot show that, so D publishes the OLD ones too
# (round 5, finding 9). Written as literals for the same reason X6's sentinels
# are: which numbers the expectation names is a fact about the preregistration,
# not something to re-derive from an arm's registered pair.
X3_OLD_EDGE_ARM = "D"
X3_OLD_EDGES = ("40", "70")


# ------------------------------------------------------------- vocabulary

def edges(t_low, t_high) -> tuple:
    """((value, stated), ...) — the arm's three edges, ascending."""
    low, high = Decimal(t_low), Decimal(t_high)
    return ((low - 1, "unstated"), (low, "stated"), (high, "stated"))


def embargoed(vendor: dict, embargo: tuple) -> bool:
    return vendor["registeredCountry"] in embargo


def score(vendor: dict) -> Decimal:
    return Decimal(vendor["riskScore"])


def band(vendor: dict, t_low, t_high) -> str:
    """§4.5's *band*: the policy's three decision regions on `riskScore`, at
    this arm's thresholds — `< T_low`, `[T_low, T_high)`, `>= T_high`."""
    value = score(vendor)
    if value >= Decimal(t_high):
        return ">=%s" % t_high
    if value >= Decimal(t_low):
        return "[%s,%s)" % (t_low, t_high)
    return "<%s" % t_low


def profile(vendor: dict, embargo: tuple, t_low, t_high) -> tuple:
    """§4.5's *profile*: two records with the same profile ask the policy the
    same question."""
    return (vendor["sanctionsHit"], embargoed(vendor, embargo),
            vendor["handlesPersonalData"], band(vendor, t_low, t_high))


def probe(vendor: dict, embargo: tuple) -> tuple:
    """§4.5's *probe*. Non-embargoed countries collapse to one token because
    the policy cannot distinguish CA from DE; embargoed codes are kept."""
    country = (vendor["registeredCountry"] if embargoed(vendor, embargo)
               else "non-emb")
    return (str(score(vendor)), vendor["sanctionsHit"], country,
            vendor["handlesPersonalData"])


def probe_exact(vendor: dict) -> tuple:
    """The same key with the exact country code: a count of SURFACE variation,
    not of test variation (§4.5)."""
    return (str(score(vendor)), vendor["sanctionsHit"],
            vendor["registeredCountry"], vendor["handlesPersonalData"])


def deciding_clause(vendor: dict, embargo: tuple, t_low, t_high) -> str:
    """§4.5's *deciding clause*: the first clause of the mirror's if-chain that
    fires, at this arm's thresholds. Kept in lockstep with
    `policy_mirror.verdict` by the harness tests, which assert that the clause
    this returns implies the verdict the mirror returns for that arm."""
    if vendor["sanctionsHit"]:
        return "P1"
    if vendor["registeredCountry"] in embargo:
        return "P2"
    value = score(vendor)
    if value >= Decimal(t_high):
        return "P3"
    if vendor["handlesPersonalData"] and value >= Decimal(t_low):
        return "P4"
    return "P5"


def clause_text(t_low, t_high) -> dict:
    """The five clauses' prose, at this arm's numbers. 011 could write `>= 70`
    as a constant; five arms cannot."""
    return {
        "P1": "sanctions hit -> reject",
        "P2": "embargoed country -> reject",
        "P3": "score >= %s -> manual review" % t_high,
        "P4": "personal data and %s <= score < %s -> manual review"
              % (t_low, t_high),
        "P5": "otherwise -> clear",
    }


def show_probe(key: tuple) -> str:
    value, sanctions, country, personal = key
    return '("%s", %s, %s, %s)' % (value, str(sanctions).lower(), country,
                                   str(personal).lower())


def show_signature(multiset: tuple) -> str:
    """One whole-run multiset as text — `(false, false, true, [40,70)) x3, …` —
    in the order the multiset was built in, so two runs that asked the same
    questions the same number of times render identically and two that did not
    cannot render the same (§4.5 X4, round 5 finding 9)."""
    if not multiset:
        return "none"
    return ", ".join("(%s) x%d" % (", ".join(_token(part) for part in key), count)
                     for key, count in multiset)


def _token(part) -> str:
    """One member of a profile or probe key, written as the census writes
    booleans everywhere else in this file."""
    return str(part).lower() if isinstance(part, bool) else str(part)


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


# ------------------------------------------------------------- the census

def census(arm: str, runs: dict, classes: list, embargo: tuple,
           t_low, t_high) -> dict:
    """§4.5's X1-X6 for one arm, over that arm's valid runs.

    `runs` is {slot: [accepted record, ...]} in the compiler's own order and
    `classes` is that arm's `FAMILY.json` mutations. Labels come from the ONE
    registered mirror module instantiated at this arm's registered pair (§4.1,
    §2.2 [D-14]) — the same module and the same pair the scorer's own H/Q split
    uses, so the census and the rates cannot disagree about what H is. Nothing
    here re-runs a model or rewrites a retained byte.
    """
    slots = sorted(runs)
    n_runs = len(slots)
    records = [(slot, record) for slot in slots for record in runs[slot]]
    vendors = [(slot, record["vendor"]) for slot, record in records]
    arm_edges = edges(t_low, t_high)
    edge_values = [value for value, _stated in arm_edges]

    def concordant(record: dict) -> bool:
        return record["decision"]["outcome"] == pm.verdict(record["vendor"],
                                                           t_low, t_high)

    per_run_sizes = [len(runs[slot]) for slot in slots]
    n_h = sum(1 for _slot, record in records if concordant(record))
    population = {
        "runs": n_runs,
        "records": len(records),
        "h": n_h,
        "q": len(records) - n_h,
        "recordsPerRun": {"min": min(per_run_sizes) if per_run_sizes else None,
                          "max": max(per_run_sizes) if per_run_sizes else None},
    }

    return {
        "arm": arm,
        "thresholds": {"tLow": str(t_low), "tHigh": str(t_high)},
        "edges": [{"value": str(value), "stated": stated}
                  for value, stated in arm_edges],
        "population": population,
        "x1": _x1(records, classes, embargo, n_runs, concordant),
        "x2": _x2(vendors, edge_values),
        "x3": _x3(vendors, arm_edges, arm),
        "x4": _x4(slots, runs, embargo, t_low, t_high),
        "x5": _x5(slots, runs, vendors, records, embargo, t_low, t_high),
        "x6": _x6(vendors) if arm == X6_ARM else None,
        "note": "Descriptive. No §5 decision reads any of it, and no count here "
                "carries an interval: records inside one completion are not "
                "independent trials (§4.3, §4.5).",
    }


def _x1(records: list, classes: list, embargo: tuple, n_runs: int,
        concordant) -> dict:
    """X1 — distinct probes per class, the modal probe's run share, and the
    runs still covered if the modal probe is deleted. Over the H records
    matching the class predicate, which is the set the primary rate counts.

    Study 011's values, the reference this study's arm A is read against, were
    2, 6, 2, 24, 26, 2 (§4.5).
    """
    rows = []
    for entry in classes:
        members = [(slot, record["vendor"]) for slot, record in records
                   if pm.predicate_matches(entry["predicate"], record["vendor"])
                   and concordant(record)]
        probe_runs: dict = collections.defaultdict(set)
        for slot, vendor in members:
            probe_runs[probe(vendor, embargo)].add(slot)
        covering = {slot for slot, _vendor in members}
        widest = max((len(key_runs) for key_runs in probe_runs.values()),
                     default=0)
        tied = [key for key in sorted(probe_runs)
                if len(probe_runs[key]) == widest]
        modal = tied[0] if tied else None
        universal = [key for key in sorted(probe_runs)
                     if n_runs and len(probe_runs[key]) == n_runs]

        def remainder(without) -> int:
            """The runs still covered if one probe is deleted — 011's collapse
            column, computed without mutating `probe_runs`."""
            kept = set()
            for other, other_runs in probe_runs.items():
                if other != without:
                    kept |= other_runs
            return len(kept)

        rows.append({
            "index": entry["index"],
            "predicateProse": entry["predicateProse"],
            "records": len(members),
            "runs": len(covering),
            "values": len({str(score(vendor)) for _slot, vendor in members}),
            "probes": len(probe_runs),
            "probesExact": len({probe_exact(vendor)
                                for _slot, vendor in members}),
            "modal": show_probe(modal) if modal else None,
            "modalRuns": len(probe_runs[modal]) if modal else 0,
            "modalTied": [show_probe(key) for key in tied],
            "withoutModal": remainder(modal),
            "minCover": cover_greedily(probe_runs, n_runs),
            "singletons": sum(1 for key_runs in probe_runs.values()
                              if len(key_runs) == 1),
            # The collapse table 011 printed as its §D: a probe present in
            # every covered run, and what is left if it is deleted.
            "universal": [{"probe": show_probe(key),
                           "records": sum(1 for _slot, vendor in members
                                          if probe(vendor, embargo) == key),
                           "runsWithoutIt": remainder(key)}
                          for key in universal],
        })
    return {"classes": rows, "runs": n_runs}


def _x2(vendors: list, edge_values: list) -> dict:
    """X2 — every record's distance to the nearest of the arm's three edges,
    over §4.5's registered buckets."""
    buckets = collections.Counter()
    for _slot, vendor in vendors:
        distance = min((abs(score(vendor) - edge) for edge in edge_values),
                       default=None)
        if distance is None:
            continue
        if distance == 0:
            buckets[BUCKETS[0]] += 1
        elif distance <= Decimal("0.001"):
            buckets[BUCKETS[1]] += 1
        elif distance <= Decimal("0.01"):
            buckets[BUCKETS[2]] += 1
        elif distance <= Decimal("0.1"):
            buckets[BUCKETS[3]] += 1
        elif distance <= Decimal("1"):
            buckets[BUCKETS[4]] += 1
        else:
            buckets[BUCKETS[5]] += 1
    return {
        "order": list(BUCKETS),
        "buckets": {label: buckets[label] for label in BUCKETS},
        "records": len(vendors),
        "onOrWithin001": sum(buckets[label] for label in HUGGING_BUCKETS),
        "humanGap": sum(buckets[label] for label in GAP_BUCKETS),
    }


def _near_edge_row(vendors: list, edge, stated: str) -> dict:
    """One near-edge row: the exact values strictly below within 1.0, the count
    exactly at, and the exact values strictly above within 1.0."""
    below, above, at = collections.Counter(), collections.Counter(), 0
    for _slot, vendor in vendors:
        value = score(vendor)
        if value == edge:
            at += 1
        elif edge - 1 <= value < edge:
            below[str(value)] += 1
        elif edge < value <= edge + 1:
            above[str(value)] += 1
    return {
        "edge": str(edge), "stated": stated,
        "below": [[value, below[value]] for value in sorted(below, key=Decimal)],
        "belowCount": sum(below.values()),
        "at": at,
        "above": [[value, above[value]] for value in sorted(above, key=Decimal)],
        "aboveCount": sum(above.values()),
    }


def _x3(vendors: list, arm_edges: tuple, arm: str) -> dict:
    """X3 — the near-edge tables, per edge: the exact values strictly below
    within 1.0, the count exactly at, and the exact values strictly above
    within 1.0. This is the table that showed the empty (23.75, 39) band.

    §4.5 makes X3 carry two further duties, and round 5's finding 9 is that it
    carried neither:

      * **the full distribution.** "X4's and X3's full distributions are what
        catch an unanticipated one" — an arm E value arrived at by a route
        nobody anticipated. A table of the values within 1.0 of THIS arm's edges
        is not a full distribution: it is the anticipated neighbourhood, and it
        is exactly where an unanticipated value is not. Two otherwise identical
        arm E corpora scoring 12 and 13 produced identical census objects.
        `values` is every distinct `riskScore` in the arm's accepted records
        with its count, ascending — the distribution the sentinel list is not an
        enumeration of;
      * **arm D's old edges.** §4.5's registered expectation is that under D
        "the near-edge tables at 40 and 70 empty out", and a table keyed to D's
        own {44, 45, 72} publishes no such thing. `oldEdges` is the same row
        computed at 40 and 70 for arm D and absent for every other arm, whose
        own edges those already are.

    Descriptive, like everything in §4.5: no §5 decision reads any of it, and a
    mass at a value not in X6's list is reported as a finding in its own right
    rather than adjudicated here.
    """
    rows = [_near_edge_row(vendors, edge, stated) for edge, stated in arm_edges]
    distribution = collections.Counter(str(score(vendor))
                                       for _slot, vendor in vendors)
    block = {
        "edges": rows,
        "values": [[value, distribution[value]]
                   for value in sorted(distribution, key=Decimal)],
        "distinctValues": len(distribution),
        "records": len(vendors),
    }
    if arm == X3_OLD_EDGE_ARM:
        # Stated nowhere in this arm's policy text: 40 and 70 are the edges the
        # OTHER four arms state, and D's registered expectation is about their
        # emptying out.
        block["oldEdges"] = [_near_edge_row(vendors, Decimal(edge), "unstated")
                             for edge in X3_OLD_EDGES]
    return block


def _x4(slots: list, runs: dict, embargo: tuple, t_low, t_high) -> dict:
    """X4 — within-run and across-run redundancy: distinct profiles per run,
    and the number of runs sharing a whole-run profile multiset.

    Round 5, finding 9: the registered wording is "the number of runs sharing a
    whole-run profile multiset", and §4.5 calls X4's a FULL distribution. Four
    aggregates over the signatures — how many are distinct, how many runs are in
    a group, the group sizes, how many are singletons — are not that
    distribution: they say how the runs pile up without saying onto what, so two
    corpora with different multisets and the same pile-up shape are one census
    object. `groups` is every distinct whole-run multiset with the number of
    runs carrying it, in a deterministic order (descending by that number, then
    by the rendered multiset), and the multiset is rendered so a reader can see
    WHICH question every run in a group asked.
    """
    distinct_per_run = collections.Counter()
    redundant_per_run = collections.Counter()
    for slot in slots:
        counted = collections.Counter(profile(record["vendor"], embargo,
                                              t_low, t_high)
                                      for record in runs[slot])
        distinct_per_run[len(counted)] += 1
        redundant_per_run[sum(n - 1 for n in counted.values() if n > 1)] += 1
    n_runs = len(slots)
    mean_redundant = (sum(key * count for key, count
                          in redundant_per_run.items()) / n_runs
                      if n_runs else None)

    def signature(key) -> dict:
        counted = collections.Counter(
            tuple(sorted(collections.Counter(key(record["vendor"])
                                             for record in runs[slot]).items(),
                         key=repr))
            for slot in slots)
        groups = sorted((count for count in counted.values() if count > 1),
                        reverse=True)
        return {"distinct": len(counted),
                "runsSharing": sum(count for count in counted.values()
                                   if count > 1),
                "groupSizes": groups,
                "singletons": sum(1 for count in counted.values()
                                  if count == 1),
                # The distribution itself, not only its shape: every distinct
                # multiset with the number of runs carrying it (round 5,
                # finding 9). Sorted by that number and then by the rendering,
                # so the order is a fact about the data and not about a hash.
                "groups": [{"signature": show_signature(multiset),
                            "runs": count}
                           for multiset, count in
                           sorted(counted.items(),
                                  key=lambda item: (-item[1],
                                                    show_signature(item[0])))]}

    return {
        "distinctProfilesPerRun": {str(value): count for value, count
                                   in sorted(distinct_per_run.items())},
        "redundantPerRun": {str(value): count for value, count
                            in sorted(redundant_per_run.items())},
        "meanRedundant": mean_redundant,
        "signatures": {
            "profile": signature(lambda vendor: profile(vendor, embargo,
                                                        t_low, t_high)),
            "probe": signature(lambda vendor: probe(vendor, embargo)),
        },
    }


def _x5(slots: list, runs: dict, vendors: list, records: list, embargo: tuple,
        t_low, t_high) -> dict:
    """X5 — per-clause deciding counts and the outcome distribution."""
    clause_records = collections.Counter(
        deciding_clause(vendor, embargo, t_low, t_high)
        for _slot, vendor in vendors)
    clause_runs = collections.Counter()
    for slot in slots:
        for name in sorted({deciding_clause(record["vendor"], embargo,
                                            t_low, t_high)
                            for record in runs[slot]}):
            clause_runs[name] += 1
    texts = clause_text(t_low, t_high)
    rows = []
    for name in ("P1", "P2", "P3", "P4", "P5"):
        probes = {probe(vendor, embargo) for _slot, vendor in vendors
                  if deciding_clause(vendor, embargo, t_low, t_high) == name}
        rows.append({
            "clause": name, "text": texts[name],
            "records": clause_records[name],
            "share": clause_records[name] / len(vendors) if vendors else None,
            "runsWithAtLeastOne": clause_runs[name],
            "probes": len(probes),
        })
    outcomes = collections.Counter(record["decision"]["outcome"]
                                   for _slot, record in records)
    return {"clauses": rows, "runs": len(slots),
            "outcomes": {name: outcomes[name] for name in sorted(outcomes)}}


def _x6(vendors: list) -> dict:
    """X6 — the misderivation sentinel list, arm E only, registered BEFORE the
    data so a comprehension failure in arm E is diagnosed rather than assumed
    away by S5 (§4.5).

    A sentinel list, NOT an enumeration: no finite list can be "every value the
    frozen wording admits under a wrong but coherent reading", and §4.5 says so
    and withdraws the earlier claim. X3's and X4's full distributions are what
    catch an unanticipated one, and a mass of arm E records at any single value
    not in this list is reported as a finding in its own right.
    """
    rows = []
    for values, misreading in X6_SENTINELS:
        for value in values:
            target = Decimal(value)
            at = sum(1 for _slot, vendor in vendors if score(vendor) == target)
            near = sum(1 for _slot, vendor in vendors
                       if abs(score(vendor) - target) <= X6_NEIGHBOURHOOD)
            rows.append({"value": value, "misreading": misreading,
                         "at": at, "within001": near})
    return {
        "values": rows,
        "note": "A sentinel list, not an enumeration (§4.5). Mass at 0.7/0.4, "
                "7/4 or 28 is evidence that arm E measured comprehension "
                "rather than anchoring, and §5.3 (i) reads it that way; 28 "
                "comes from wording this study has already removed and is kept "
                "precisely because removing a reading is not proving it gone. "
                "Descriptive: no §5 decision reads X6.",
    }


# ------------------------------------------------------------- rendering

def render_markdown(per_arm: list) -> str:
    """`CENSUS.md`, from the census blocks the scorer just computed. The scorer
    writes it (§4.7); this module renders it, exactly as 011's script rendered
    its own tables beside the arithmetic that produced them."""
    lines = [
        "# The probe census — Study 012",
        "",
        "Generated by `harness/score_rates.py` from the retained slots, through",
        "`harness/census.py`. §4.5's registered secondary: X1-X6, per arm, all",
        "descriptive. **No §5 decision reads any of it**, and no count here carries an",
        "interval — records inside one completion are not independent trials (§4.3).",
        "",
        "No clock and no randomness enter this file, so re-scoring the same slots",
        "reproduces it byte-for-byte.",
        "",
    ]
    for block in per_arm:
        population = block["population"]
        lines += [
            "## Arm %s — (T_low, T_high) = (%s, %s)"
            % (block["arm"], block["thresholds"]["tLow"],
               block["thresholds"]["tHigh"]),
            "",
            "Edges: %s." % ", ".join("%s (%s)" % (edge["value"], edge["stated"])
                                     for edge in block["edges"]),
            "",
            "Record set: %d valid runs, %d accepted records (%d-%d per run); "
            "H = %d, Q = %d."
            % (population["runs"], population["records"],
               population["recordsPerRun"]["min"] or 0,
               population["recordsPerRun"]["max"] or 0,
               population["h"], population["q"]),
            "",
            "### X1 — distinct probes per class",
            "",
            "Probe = (exact riskScore, sanctionsHit, embargo-normalised country,",
            "handlesPersonalData), over the H records matching the class predicate.",
            "",
            "| class | predicate (FAMILY.json prose) | H records | runs covering | "
            "distinct riskScore values | DISTINCT PROBES | distinct probes w/ exact "
            "country | modal probe | modal probe's run share | runs still covered if "
            "the modal probe is removed | min probes needed to cover every covered "
            "run | probes used by exactly 1 run |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|",
        ]
        for row in block["x1"]["classes"]:
            lines.append("| %d | %s | %d | %d/%d | %d | **%d** | %d | %s | %d/%d | "
                         "%d | %d | %d |"
                         % (row["index"], row["predicateProse"], row["records"],
                            row["runs"], block["x1"]["runs"], row["values"],
                            row["probes"], row["probesExact"],
                            row["modal"] or "—", row["modalRuns"],
                            block["x1"]["runs"], row["withoutModal"],
                            row["minCover"], row["singletons"]))
        lines.append("")
        for row in block["x1"]["classes"]:
            if len(row["modalTied"]) > 1:
                lines += ["Class %d's modal probe is a tie at %d/%d runs — %s. The "
                          "table names the first in sort order."
                          % (row["index"], row["modalRuns"], block["x1"]["runs"],
                             " and ".join(row["modalTied"])), ""]
            for universal in row["universal"]:
                lines += ["Class %d has a probe present in all %d covered runs — %s, "
                          "carrying %d records; deleting it leaves %d runs covered."
                          % (row["index"], block["x1"]["runs"], universal["probe"],
                             universal["records"], universal["runsWithoutIt"]), ""]
        x2 = block["x2"]
        lines += [
            "### X2 — every record's distance to the nearest edge",
            "",
            "| min distance to {%s} | records |"
            % ", ".join(edge["value"] for edge in block["edges"]),
            "|---|---|",
        ]
        for label in x2["order"]:
            lines.append("| %s | %d |" % (label, x2["buckets"][label]))
        lines += [
            "",
            "%d of %d sit on an edge or within 0.01 of one; %d land in the "
            "human-sized gap (0.01, 1.0]."
            % (x2["onOrWithin001"], x2["records"], x2["humanGap"]),
            "",
            "### X3 — within 1.0 of each edge, both sides, exact values",
            "",
            "| edge | strictly below within 1.0 | n | exactly at | strictly above "
            "within 1.0 | n |",
            "|---|---|---|---|---|---|",
        ]
        for row in block["x3"]["edges"]:
            lines.append("| %s (%s) | %s | %d | %d | %s | %d |"
                         % (row["edge"], row["stated"],
                            _multiset(row["below"]), row["belowCount"], row["at"],
                            _multiset(row["above"]), row["aboveCount"]))
        if block["x3"].get("oldEdges"):
            lines += [
                "",
                "The OLD edges, stated in no text this arm's author saw, published "
                "because §4.5",
                "registers the expectation that under arm %s the near-edge tables at "
                "%s empty out." % (X3_OLD_EDGE_ARM, " and ".join(X3_OLD_EDGES)),
                "",
                "| old edge | strictly below within 1.0 | n | exactly at | strictly "
                "above within 1.0 | n |",
                "|---|---|---|---|---|---|",
            ]
            for row in block["x3"]["oldEdges"]:
                lines.append("| %s (%s in this arm) | %s | %d | %d | %s | %d |"
                             % (row["edge"], row["stated"],
                                _multiset(row["below"]), row["belowCount"],
                                row["at"], _multiset(row["above"]),
                                row["aboveCount"]))
        lines += [
            "",
            "#### X3 — the full distribution: every distinct riskScore value",
            "",
            "Every value in the arm's accepted records, not only the ones near an "
            "edge:",
            "§4.5 registers X3's and X4's full distributions as what catch a value "
            "arrived at",
            "by a route X6's sentinel list does not anticipate.",
            "",
            "| exact riskScore | records |",
            "|---|---|",
        ]
        for value, count in block["x3"]["values"]:
            lines.append("| %s | %d |" % (value, count))
        lines += [
            "",
            "%d distinct values over %d records."
            % (block["x3"]["distinctValues"], block["x3"]["records"]),
        ]
        x4 = block["x4"]
        lines += [
            "",
            "### X4 — within-run and across-run redundancy",
            "",
            "| distinct profiles in a run | runs |",
            "|---|---|",
        ]
        for value, count in sorted(x4["distinctProfilesPerRun"].items(),
                                   key=lambda item: int(item[0])):
            lines.append("| %s | %d |" % (value, count))
        lines += ["", "| redundant records in a run | runs |", "|---|---|"]
        for value, count in sorted(x4["redundantPerRun"].items(),
                                   key=lambda item: int(item[0])):
            lines.append("| %s | %d |" % (value, count))
        lines += [
            "",
            "Mean redundant records per run: %s."
            % ("—" if x4["meanRedundant"] is None else "%.3f" % x4["meanRedundant"]),
            "",
            "| run signature | distinct signatures | runs sharing a signature with "
            "another run | group sizes |",
            "|---|---|---|---|",
        ]
        for label, key in (("profile multiset", "profile"),
                           ("probe multiset (exact value + tuple)", "probe")):
            signature = x4["signatures"][key]
            sizes = (", ".join(str(size) for size in signature["groupSizes"]) +
                     (", then %d singletons" % signature["singletons"]
                      if signature["singletons"] else "")
                     ) if signature["groupSizes"] else "all singletons"
            lines.append("| %s | %d | %d | %s |"
                         % (label, signature["distinct"], signature["runsSharing"],
                            sizes))
        for label, key in (("profile multiset", "profile"),
                           ("probe multiset (exact value + tuple)", "probe")):
            lines += [
                "",
                "Every distinct %s, with the runs carrying it — the distribution "
                "and not only" % label,
                "its shape (§4.5 X4):",
                "",
                "| runs | whole-run %s |" % label,
                "|---|---|",
            ]
            for group in x4["signatures"][key]["groups"]:
                lines.append("| %d | %s |" % (group["runs"], group["signature"]))
        lines += [
            "",
            "### X5 — which clause decides each record",
            "",
            "| clause | text | records | share | runs with >=1 | distinct probes "
            "among its records |",
            "|---|---|---|---|---|---|",
        ]
        for row in block["x5"]["clauses"]:
            lines.append("| %s | %s | %d | %s | %d/%d | %d |"
                         % (row["clause"], row["text"], row["records"],
                            "—" if row["share"] is None else "%.2f%%" % (100.0 * row["share"]),
                            row["runsWithAtLeastOne"], block["x5"]["runs"],
                            row["probes"]))
        lines += [
            "",
            "Outcome distribution: " + (", ".join(
                "%s %d" % (name, count)
                for name, count in sorted(block["x5"]["outcomes"].items()))
                or "none") + ".",
            "",
        ]
        if block["x6"] is not None:
            lines += [
                "### X6 — the misderivation sentinel list (arm %s only)" % X6_ARM,
                "",
                "| value | the misreading that produces it | records at it | records "
                "within 0.01 |",
                "|---|---|---|---|",
            ]
            for row in block["x6"]["values"]:
                lines.append("| %s | %s | %d | %d |"
                             % (row["value"], row["misreading"], row["at"],
                                row["within001"]))
            lines += ["", block["x6"]["note"], ""]
    lines += [
        "## What the census is and is not",
        "",
        "It counts test VARIETY behind a coverage rate; it evaluates no pack, applies",
        "no patch, and runs no evaluator. §4.5's registered expectations are stated in",
        "the preregistration before the data and carry no verdict; nothing here moves",
        "a §5 decision. Study 011's census already recorded that the claim \"low probe",
        "diversity costs detection power\" is a plausible mechanism there and a",
        "demonstrated one nowhere.",
        "",
    ]
    return "\n".join(lines)


def _multiset(pairs: list) -> str:
    """One X3 cell: `39.99 x58`, ascending, or `none`."""
    if not pairs:
        return "none"
    return ", ".join("%s x%d" % (value, count) for value, count in pairs)
