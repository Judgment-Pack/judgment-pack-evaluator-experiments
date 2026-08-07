"""Deterministic replay of the evidence-sufficiency case set.

Each case in `cases/` freezes one acquired artifact, the derivation parameters,
the availability documents the arms produce from it, the requirement-demand
table that says whether the requirement is actually satisfied, and the Core §8.3
disposition every (arm, pack) combination reaches. This module recomputes all of
that from the shipped mechanisms -- the portable derivation rule for the
convention arms, `naive.py` for the naive arms, and the clean-room Python
evaluator for the dispositions -- and diffs the result against the frozen bytes.

Nothing here is a judgment call: given a pack, a facts document, and an
availability document, the disposition follows mechanically from Core §8, and
the requirement-demand table below is computed from each artifact's own bytes
rather than stored by hand. The frozen tables are the oracle; this file is the
referee.

    python3 replay.py            verify every frozen cell (exit 1 on any diff)
    python3 replay.py --table    print the README's case tables from the frozen
                                 cases, so the prose cannot drift from the data
                                 (asserted: test_replay.TheReadmeTables)
"""

import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "derivation-rule"))
sys.path.insert(0, os.path.join(HERE, "..", "python"))

import derive  # the shipped portable derivation rule (ADR-0002 item 2)
from jps_evaluator import canonicalize_disposition, evaluate

import naive

REQUIREMENT_ID = "signed-agreement"

# The derivation rule's own sentinel for a pointer that does not resolve,
# obtained through its public API rather than by reaching for a private name.
ABSENT = derive.get({}, "/does-not-resolve")

# Each combination is one (availability arm, pack) pair. The keys are the frozen
# case files' `expected` members, and the tests assert every one of them.
COMBINATIONS = {
    # the naive existence mapping against the pack as an acquisition author
    # would most plausibly find it: one required requirement, one rule over it
    "naive": ("naive", "release-evidence-only"),
    # the shipped derivation convention, pack-independent clauses only
    "convention": ("convention", "release-evidence-only"),
    # the same convention plus one clause whose pointer is chosen because of
    # what this pack asks -- the pack-coupled catch
    "conventionCoupled": ("convention-coupled", "release-evidence-only"),
    # the convention arm against a pack that states its clause as a Core fact
    # condition: the probe for whether the pack-side lever already exists
    "conventionClauseFact": ("convention", "release-clause-fact"),
    # the same fact-conditioned pack against the plain naive arm, which supplies
    # no facts at all: the omission mode
    "naiveClauseFact": ("naive", "release-clause-fact"),
    # and against the credulous naive arm, which asserts the fact the pack names
    # from existence alone: the assertion mode
    "naiveCredulousClauseFact": ("naive-credulous", "release-clause-fact"),
}

ARM_RULES = {
    "convention": "agreement.rule.json",
    "convention-coupled": "agreement-coupled.rule.json",
}

# The per-clause coupling verdict ADR-0003 fixed before any case was written,
# plus `none` for a case with no divergence to catch and `unattested` for the
# authority ceiling: there a clause CAN catch the fixture (`isTrue
# /signatoryHadDelegatedAuthority`), and what no clause reaches is whether the
# field it would read is true.
COUPLING_VALUES = ("pack-independent", "pack-coupled", "none", "unattested")

# The pack's requirement description, decomposed into checks over the artifact
# and the acquisition parameters. Each is computed below from the artifact's own
# bytes, so `requirementSatisfied` -- the field that decides which rows count as
# failures -- is refereed rather than asserted. The README says what would make
# a reader disagree with the decomposition.
REQUIREMENT_DEMANDS = (
    ("onFile", "on file"),
    ("withThisCounterparty", "with this counterparty"),
    ("executedByBothParties", "executed by both parties"),
    ("current", "current"),
    ("grantsOnwardTransfer", "grants onward transfer"),
)

DEMAND_LABELS = dict(REQUIREMENT_DEMANDS)


def _load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def load_pack(name):
    return _load(os.path.join(HERE, "pack", name + ".json"))


def load_rule(name):
    return _load(os.path.join(HERE, "rules", ARM_RULES[name]))


def case_paths():
    return sorted(glob.glob(os.path.join(HERE, "cases", "*.json")))


def load_cases():
    return [_load(path) for path in case_paths()]


# --- the requirement's own demands, computed from each artifact ---


def requirement_demands(case):
    """Which of the requirement description's five demands this artifact meets.

    `release-*.json`'s single evidence requirement reads: "The data-sharing
    agreement with this counterparty, executed by both parties and current,
    whose executed schedule grants onward transfer of the requested dataset to
    this counterparty." Each clause of that sentence is one entry below, and
    every entry is a function of the artifact and the acquisition parameters --
    no hand-set booleans, no case-by-case judgement.
    """

    artifact = case["artifact"]
    params = case["params"]
    on_file = derive.get(artifact, "/status") == "found"
    observed = derive.instant(derive.get(artifact, "/observedAt"))
    as_of = derive.instant(params.get("asOf"))
    max_age = params.get("maxAgeSeconds")
    current = (
        observed is not None
        and as_of is not None
        and isinstance(max_age, int)
        and 0 <= (as_of - observed) <= max_age
    )
    return {
        # a document came back at all
        "onFile": on_file,
        # "the agreement with this counterparty"
        "withThisCounterparty": derive.get(artifact, "/counterpartyLegalName")
        == params["subject"],
        # "executed by both parties" -- a signature that cannot bind the
        # counterparty does not execute anything, which is what C6 turns on
        "executedByBothParties": on_file
        and derive.get(artifact, "/sections/executionBlock") is not ABSENT
        and derive.get(artifact, "/signatoryHadDelegatedAuthority") is True,
        # "and current" -- inside the acquisition's freshness window
        "current": current,
        # "whose executed schedule grants onward transfer"
        "grantsOnwardTransfer": derive.get(artifact, "/executedGrants/onwardTransfer")
        is True,
    }


def requirement_satisfied(case):
    """True iff the artifact meets every demand the requirement's own
    description states. Computed, never read from the case file."""

    demands = requirement_demands(case)
    return all(demands[name] for name, _ in REQUIREMENT_DEMANDS)


# --- the arms ---


def arm_inputs(case, arm):
    """Return (facts, evidenceAvailability) for one arm over one case's artifact.

    The convention arms run the real derivation rule; the naive arms run the
    existence mapping. Neither is re-implemented here.
    """

    if arm == "naive":
        return naive.naive_facts(case["artifact"]), naive.naive_availability(
            case["artifact"], REQUIREMENT_ID
        )
    if arm == "naive-credulous":
        return naive.credulous_facts(case["artifact"]), naive.naive_availability(
            case["artifact"], REQUIREMENT_ID
        )
    claim = derive.derive(load_rule(arm), case["artifact"], case["params"])
    return claim["facts"], claim["evidenceAvailability"]


def derived_claims(case):
    """The frozen derived claims, recomputed: one per convention arm."""

    return {
        arm: derive.derive(load_rule(arm), case["artifact"], case["params"])
        for arm in sorted(ARM_RULES)
    }


def dispositions(case):
    """Recompute every (arm, pack) disposition for one case."""

    result = {}
    for key, (arm, pack_name) in COMBINATIONS.items():
        facts, availability = arm_inputs(case, arm)
        result[key] = evaluate(load_pack(pack_name), facts, availability)
    return result


# --- coupling, measured per clause rather than per rule ---

_FALLBACK_CLAUSE = {
    "when": {"op": "always"},
    "claim": {"facts": [], "evidence": {}, "acquisitionStatus": "unknown"},
    "reason": "probe-fallback",
}


def clause_reads(rule_name):
    """{clause `reason`: the artifact pointers that clause's own `when` resolves}.

    A rule's `basis` is cumulative over clauses 0 … matchIndex (SPEC.md), so it
    cannot answer a per-clause question. This runs each clause on its own -- the
    clause followed by a fallback that reads nothing, which makes the derived
    basis exactly that clause's own reads -- and unions the result over every
    frozen case, so short-circuiting on one artifact cannot hide a pointer the
    clause reads on another.

    This is what lets the README state the coupling verdict clause by clause and
    have it be checked at that granularity.
    """

    rule = load_rule(rule_name)
    cases = load_cases()
    reads = {}
    for clause in rule["clauses"]:
        pointers = set()
        probe = {
            "ruleVersion": rule["ruleVersion"],
            "parameters": rule["parameters"],
            "clauses": [clause, _FALLBACK_CLAUSE],
        }
        for case in cases:
            claim = derive.derive(probe, case["artifact"], case["params"])
            pointers |= set(claim["basis"])
        reads[clause["reason"]] = sorted(pointers)
    return reads


def fact_sources(rule_name):
    """The artifact pointers a rule copies into its facts document (`from`).

    An empty string is the whole artifact: a projection that names no field, and
    therefore encodes no knowledge of which field any pack will ask about.
    """

    sources = set()
    for clause in load_rule(rule_name)["clauses"]:
        for entry in clause["claim"].get("facts", []):
            sources.add(entry["from"])
    return sorted(sources)


# --- replay ---


def _diff(label, got, expected, failures):
    if canonicalize_disposition(got) != canonicalize_disposition(expected):
        failures.append(
            "%s\n     got: %s\n     frozen: %s"
            % (
                label,
                canonicalize_disposition(got).decode("utf-8"),
                canonicalize_disposition(expected).decode("utf-8"),
            )
        )


def check():
    """Return a list of human-readable diffs; empty means every cell replays."""

    failures = []
    for path in case_paths():
        case = _load(path)
        name = case["id"]

        got_naive = naive.naive_availability(case["artifact"], REQUIREMENT_ID)
        if got_naive != case["naiveAvailability"]:
            failures.append(
                "%s naiveAvailability: got %r, frozen %r"
                % (name, got_naive, case["naiveAvailability"])
            )

        got_demands = requirement_demands(case)
        if got_demands != case["requirementDemands"]:
            failures.append(
                "%s requirementDemands: got %s, frozen %s"
                % (
                    name,
                    json.dumps(got_demands, sort_keys=True),
                    json.dumps(case["requirementDemands"], sort_keys=True),
                )
            )
        if requirement_satisfied(case) != case["requirementSatisfied"]:
            failures.append(
                "%s requirementSatisfied: got %r, frozen %r"
                % (name, requirement_satisfied(case), case["requirementSatisfied"])
            )

        got_claims = derived_claims(case)
        for arm in sorted(ARM_RULES):
            if got_claims[arm] != case["derived"][arm]:
                failures.append(
                    "%s derived[%s]: got %s, frozen %s"
                    % (
                        name,
                        arm,
                        json.dumps(got_claims[arm], sort_keys=True),
                        json.dumps(case["derived"][arm], sort_keys=True),
                    )
                )

        got = dispositions(case)
        for key in sorted(COMBINATIONS):
            _diff("%s %s" % (name, key), got[key], case["expected"][key], failures)
    return failures


def summarize(disposition):
    """One cell of the README's tables."""

    if disposition["kind"] == "outcome":
        return "`outcome:%s`" % disposition["outcomeId"]
    reasons = ",".join(disposition["reasons"])
    handoff = disposition["handoff"]["state"]
    return "`%s{%s}` + handoff %s" % (disposition["kind"], reasons, handoff)


def unsupported_release(case, disposition):
    """True iff this disposition releases on evidence the requirement's own
    description does not support. This -- not bare divergence between the arms --
    is what makes a row a failure.

    The satisfaction half is computed by `requirement_satisfied` from the
    artifact's own bytes, so the headline measure has no hand-set input.
    """

    return (
        not requirement_satisfied(case)
        and disposition["kind"] == "outcome"
        and disposition["outcomeId"] == "release"
    )


def _unsupported_label(case, got):
    naive_bad = unsupported_release(case, got["naive"])
    convention_bad = unsupported_release(case, got["convention"])
    if naive_bad and convention_bad:
        return "**both arms**"
    if naive_bad:
        return "naive only"
    if convention_bad:
        return "convention only"
    return "—"


def _demand_table():
    lines = [
        "| # | "
        + " | ".join(label for _, label in REQUIREMENT_DEMANDS)
        + " | Requirement satisfied? |",
        "| --- |" + " --- |" * (len(REQUIREMENT_DEMANDS) + 1),
    ]
    for case in load_cases():
        demands = requirement_demands(case)
        cells = ["yes" if demands[name] else "**no**" for name, _ in REQUIREMENT_DEMANDS]
        lines.append(
            "| %s | %s | %s |"
            % (
                case["id"],
                " | ".join(cells),
                "yes" if requirement_satisfied(case) else "**no**",
            )
        )
    return "\n".join(lines)


def _case_table():
    lines = [
        "| # | Case | Naive arm | Convention arm | What the requirement demands | Unsupported release? | Catching clause |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for case in load_cases():
        got = dispositions(case)
        lines.append(
            "| %s | **%s** | %s | %s | %s | %s | %s |"
            % (
                case["id"],
                case["name"],
                summarize(got["naive"]),
                summarize(got["convention"]),
                case["packDemand"],
                _unsupported_label(case, got),
                case["catchingClause"]["coupling"],
            )
        )
    return "\n".join(lines)


def _probe_table():
    lines = [
        "| # | + one pack-coupled clause | The clause stated as a Core fact condition | The fact-conditioned pack, plain naive arm | The fact-conditioned pack, credulous naive arm |",
        "| --- | --- | --- | --- | --- |",
    ]
    for case in load_cases():
        got = dispositions(case)
        lines.append(
            "| %s | %s | %s | %s | %s |"
            % (
                case["id"],
                summarize(got["conventionCoupled"]),
                summarize(got["conventionClauseFact"]),
                summarize(got["naiveClauseFact"]),
                summarize(got["naiveCredulousClauseFact"]),
            )
        )
    return "\n".join(lines)


def tables():
    """The three README tables, rebuilt from the frozen cases.

    `test_replay.TheReadmeTables` asserts each block appears verbatim in
    README.md, so the prose genuinely cannot drift from the data.
    """

    return [_case_table(), _probe_table(), _demand_table()]


def main(argv):
    if "--table" in argv:
        print("\n\n".join(tables()))
        return 0
    failures = check()
    if failures:
        print("evidence-sufficiency replay: %d diff(s)" % len(failures))
        for failure in failures:
            print("  - %s" % failure)
        return 1
    print("evidence-sufficiency replay: %d cases, every frozen cell reproduces" % len(case_paths()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
