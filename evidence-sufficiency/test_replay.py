"""Tests for the evidence-sufficiency case set.

Two oracles, deliberately. `cases/*.json` freezes what the shipped mechanisms
produce, and `replay.check()` diffs a recomputation against those bytes -- that
catches drift. But frozen bytes cannot catch a case that was frozen wrong, so
the tables below are a second, hand-written oracle: every cell of all three
README tables is spelled out here from Core §8 and from the requirement's own
description, and asserted against both the frozen bytes and the recomputation.

The controls (C5, C6) and the coupling measurement ADR-0003 fixed before any
case was written are asserted as properties, not as prose -- and the coupling
measurement is asserted at the granularity the README states it: per clause,
from each clause's own basis.
"""

import json
import os
import unittest

import naive
import replay

# `replay` is what puts ../derivation-rule on the path, so the shipped rule
# engine is reached through it rather than imported ahead of it.
derive = replay.derive

HERE = os.path.dirname(os.path.abspath(__file__))

GRANT_POINTER = "/executedGrants/onwardTransfer"


def cell(disposition):
    """A disposition flattened to the tuple the tables below compare."""

    return (
        disposition["kind"],
        disposition.get("outcomeId"),
        tuple(disposition["reasons"]),
        disposition["handoff"]["state"],
        tuple(disposition["handoff"].get("triggeredBy", ())),
    )


RELEASE = ("outcome", "release", (), "none", ())
UNKNOWN = ("unresolved", None, ("unknown",), "requested", ("unknown",))
MISSING = (
    "unresolved",
    None,
    ("missing-required-evidence",),
    "requested",
    ("missing-required-evidence",),
)
NO_MATCH = ("unresolved", None, ("no-match",), "requested", ("no-match",))

# Every cell of the two disposition tables, derived by hand from Core §8:
#   naive                      existence -> present, evidence-only pack
#   convention                 shipped derivation rule, pack-independent clauses
#   conventionCoupled          the same rule plus the one pack-coupled clause
#   conventionClauseFact       derivation rule against the fact-conditioned pack
#   naiveClauseFact            plain naive arm (no facts), fact-conditioned pack
#   naiveCredulousClauseFact   credulous naive arm (asserts the fact from
#                              existence), fact-conditioned pack
EXPECTED = {
    "C0": {
        "naive": RELEASE,
        "convention": RELEASE,
        "conventionCoupled": RELEASE,
        "conventionClauseFact": RELEASE,
        "naiveClauseFact": UNKNOWN,
        "naiveCredulousClauseFact": RELEASE,
    },
    "C1": {
        "naive": RELEASE,
        "convention": UNKNOWN,
        "conventionCoupled": UNKNOWN,
        "conventionClauseFact": UNKNOWN,
        "naiveClauseFact": UNKNOWN,
        "naiveCredulousClauseFact": RELEASE,
    },
    "C2": {
        "naive": RELEASE,
        "convention": UNKNOWN,
        "conventionCoupled": UNKNOWN,
        "conventionClauseFact": UNKNOWN,
        "naiveClauseFact": UNKNOWN,
        "naiveCredulousClauseFact": RELEASE,
    },
    "C3": {
        "naive": RELEASE,
        "convention": UNKNOWN,
        "conventionCoupled": UNKNOWN,
        "conventionClauseFact": UNKNOWN,
        "naiveClauseFact": UNKNOWN,
        "naiveCredulousClauseFact": RELEASE,
    },
    "C4": {
        "naive": RELEASE,
        "convention": RELEASE,
        "conventionCoupled": UNKNOWN,
        "conventionClauseFact": NO_MATCH,
        "naiveClauseFact": UNKNOWN,
        "naiveCredulousClauseFact": RELEASE,
    },
    "C5": {
        "naive": MISSING,
        "convention": MISSING,
        "conventionCoupled": MISSING,
        "conventionClauseFact": MISSING,
        "naiveClauseFact": MISSING,
        "naiveCredulousClauseFact": MISSING,
    },
    "C6": {
        "naive": RELEASE,
        "convention": RELEASE,
        "conventionCoupled": RELEASE,
        "conventionClauseFact": RELEASE,
        "naiveClauseFact": UNKNOWN,
        "naiveCredulousClauseFact": RELEASE,
    },
}

# The measurement ADR-0003 fixed before the cases were built. `unattested` is
# not a coupling verdict but the honest label for C6: a clause CAN catch that
# fixture (`isTrue /signatoryHadDelegatedAuthority`); what no clause reaches is
# whether the field it would read is true.
EXPECTED_COUPLING = {
    "C0": "none",
    "C1": "pack-independent",
    "C2": "pack-independent",
    "C3": "pack-independent",
    "C4": "pack-coupled",
    "C5": "none",
    "C6": "unattested",
}

EXPECTED_AVAILABILITY = {
    "C0": "present",
    "C1": "present",
    "C2": "present",
    "C3": "present",
    "C4": "present",
    "C5": "absent",
    "C6": "present",
}

# The third README table, hand-written from the requirement's own description:
# "The data-sharing agreement with this counterparty, executed by both parties
# and current, whose executed schedule grants onward transfer …". This is what
# makes `unsupported_release` refereed rather than hand-set.
EXPECTED_DEMANDS = {
    #      onFile withCpty executed current grants
    "C0": (True, True, True, True, True),
    "C1": (True, True, False, True, True),
    "C2": (True, False, True, True, True),
    "C3": (True, True, True, False, True),
    "C4": (True, True, True, True, False),
    "C5": (False, True, False, False, False),
    "C6": (True, True, False, True, True),
}

# The per-clause coupling measurement, hand-written: the artifact pointers each
# clause's own `when` resolves, unioned over every case in the set. The README
# states the coupling verdict clause by clause; this is that statement as data.
EXPECTED_CLAUSE_READS = {
    "convention": {
        "subject": ["/counterpartyLegalName", "/status"],
        "incomplete": ["/sections/executionBlock", "/status"],
        "freshness": ["/observedAt", "/status"],
        "resolved": ["/status"],
        "absent": ["/checkedSuccessfully", "/counterpartyLegalName", "/status"],
        "unknown": [],
    },
    "convention-coupled": {
        "subject": ["/counterpartyLegalName", "/status"],
        "incomplete": ["/sections/executionBlock", "/status"],
        "freshness": ["/observedAt", "/status"],
        "grant": ["/executedGrants/onwardTransfer", "/status"],
        "resolved": ["/status"],
        "absent": ["/checkedSuccessfully", "/counterpartyLegalName", "/status"],
        "unknown": [],
    },
}

DIVERGENCE_CAPABLE = ("C1", "C2", "C3", "C4")


def cases_by_id():
    return {case["id"]: case for case in replay.load_cases()}


def readme():
    with open(os.path.join(HERE, "README.md"), encoding="utf-8") as handle:
        return handle.read()


class FrozenCases(unittest.TestCase):
    def test_the_case_set_is_exactly_the_frozen_seven(self):
        self.assertEqual(sorted(cases_by_id()), sorted(EXPECTED))

    def test_every_frozen_cell_reproduces(self):
        self.assertEqual(replay.check(), [])

    def test_every_case_file_carries_the_whole_record(self):
        for name, case in sorted(cases_by_id().items()):
            for member in (
                "id",
                "name",
                "summary",
                "artifact",
                "params",
                "packDemand",
                "requirementDemands",
                "requirementSatisfied",
                "catchingClause",
                "naiveAvailability",
                "derived",
                "expected",
            ):
                self.assertIn(member, case, "%s is missing %r" % (name, member))
            self.assertEqual(
                sorted(case["expected"]), sorted(replay.COMBINATIONS), name
            )

    def test_no_fixture_is_internally_impossible(self):
        # A retained document cannot be observed before it was signed. C3's
        # fixture failed this and was corrected before the first commit; the
        # README records the correction and this test keeps it corrected.
        for name, case in sorted(cases_by_id().items()):
            signed = derive.instant(
                derive.get(case["artifact"], "/sections/executionBlock/signedAt")
            )
            observed = derive.instant(derive.get(case["artifact"], "/observedAt"))
            if signed is None or observed is None:
                continue
            self.assertLessEqual(signed, observed, "%s: signed after it was observed" % name)


class EveryTableCell(unittest.TestCase):
    """The hand-written oracle: the disposition tables, cell by cell."""

    def test_recomputed_dispositions_match_the_hand_written_table(self):
        for name, case in sorted(cases_by_id().items()):
            got = replay.dispositions(case)
            for combination, expected in sorted(EXPECTED[name].items()):
                self.assertEqual(
                    cell(got[combination]),
                    expected,
                    "%s / %s" % (name, combination),
                )

    def test_frozen_dispositions_match_the_hand_written_table(self):
        for name, case in sorted(cases_by_id().items()):
            for combination, expected in sorted(EXPECTED[name].items()):
                self.assertEqual(
                    cell(case["expected"][combination]),
                    expected,
                    "%s / %s (frozen)" % (name, combination),
                )

    def test_naive_availability_matches_the_hand_written_table(self):
        for name, case in sorted(cases_by_id().items()):
            got = naive.naive_availability(case["artifact"], replay.REQUIREMENT_ID)
            self.assertEqual(
                got, {replay.REQUIREMENT_ID: EXPECTED_AVAILABILITY[name]}, name
            )
            self.assertEqual(got, case["naiveAvailability"], "%s (frozen)" % name)


class TheRequirementDemands(unittest.TestCase):
    """`unsupported_release` is refereed, not hand-set.

    The headline measure asks whether a row released on evidence the
    requirement's own description does not cover. That used to rest on a boolean
    written by hand into each case with no oracle. It is now computed from the
    artifact and the acquisition parameters, and asserted here against a
    hand-written decomposition of the requirement's English description.
    """

    def test_every_demand_matches_the_hand_written_table(self):
        for name, case in sorted(cases_by_id().items()):
            got = replay.requirement_demands(case)
            expected = dict(
                zip([key for key, _ in replay.REQUIREMENT_DEMANDS], EXPECTED_DEMANDS[name])
            )
            self.assertEqual(got, expected, name)

    def test_frozen_demands_match_the_recomputed_ones(self):
        for name, case in sorted(cases_by_id().items()):
            self.assertEqual(case["requirementDemands"], replay.requirement_demands(case), name)
            self.assertEqual(
                case["requirementSatisfied"], replay.requirement_satisfied(case), name
            )

    def test_only_the_complete_control_satisfies_the_requirement(self):
        satisfied = [
            name
            for name, case in sorted(cases_by_id().items())
            if replay.requirement_satisfied(case)
        ]
        self.assertEqual(satisfied, ["C0"])

    def test_each_case_fails_exactly_the_demand_its_name_claims(self):
        # The case set is not rigged by overlapping failures: apart from the
        # genuinely-absent control, each divergence-capable case and each
        # ceiling control fails exactly one of the five demands.
        expected_failures = {
            "C0": [],
            "C1": ["executedByBothParties"],
            "C2": ["withThisCounterparty"],
            "C3": ["current"],
            "C4": ["grantsOnwardTransfer"],
            "C5": ["onFile", "executedByBothParties", "current", "grantsOnwardTransfer"],
            "C6": ["executedByBothParties"],
        }
        for name, case in sorted(cases_by_id().items()):
            demands = replay.requirement_demands(case)
            failed = [key for key, _ in replay.REQUIREMENT_DEMANDS if not demands[key]]
            self.assertEqual(failed, expected_failures[name], name)


class TheMeasurement(unittest.TestCase):
    """ADR-0003 fixed the reported number as the count of pack-coupled catches."""

    def test_every_coupling_verdict_is_from_the_closed_set(self):
        for name, case in sorted(cases_by_id().items()):
            self.assertIn(case["catchingClause"]["coupling"], replay.COUPLING_VALUES, name)

    def test_coupling_verdicts_match_the_hand_written_table(self):
        for name, case in sorted(cases_by_id().items()):
            self.assertEqual(case["catchingClause"]["coupling"], EXPECTED_COUPLING[name], name)

    def test_exactly_one_pack_coupled_catch_among_the_divergence_capable_cases(self):
        cases = cases_by_id()
        coupled = [
            name
            for name in DIVERGENCE_CAPABLE
            if cases[name]["catchingClause"]["coupling"] == "pack-coupled"
        ]
        self.assertEqual(coupled, ["C4"])

    def test_c4_is_the_only_case_both_arms_release_that_the_requirement_refuses(self):
        cases = cases_by_id()
        both = []
        for name in DIVERGENCE_CAPABLE:
            got = replay.dispositions(cases[name])
            if replay.unsupported_release(
                cases[name], got["naive"]
            ) and replay.unsupported_release(cases[name], got["convention"]):
                both.append(name)
        self.assertEqual(both, ["C4"])


class CouplingPerClause(unittest.TestCase):
    """The coupling verdict is stated per clause, so it is checked per clause.

    A rule's `basis` is cumulative over clauses 0 … matchIndex, so no statement
    about a whole rule can be read off it. `replay.clause_reads` runs each clause
    on its own and unions the result over every case, which is exactly the
    granularity the README's sentences use.
    """

    def test_each_clause_reads_what_the_hand_written_table_says(self):
        for rule_name, expected in sorted(EXPECTED_CLAUSE_READS.items()):
            got = replay.clause_reads(rule_name)
            self.assertEqual(got, {k: sorted(v) for k, v in expected.items()}, rule_name)

    def test_no_clause_of_the_pack_independent_rule_reads_the_grant(self):
        # Clause granularity, from each clause's own basis: this is the sentence
        # the README carries, and it is true of `when` conditions specifically.
        reads = replay.clause_reads("convention")
        offenders = [reason for reason, pointers in reads.items() if GRANT_POINTER in pointers]
        self.assertEqual(offenders, [])

    def test_exactly_one_clause_of_the_coupled_rule_reads_the_grant(self):
        reads = replay.clause_reads("convention-coupled")
        offenders = sorted(
            reason for reason, pointers in reads.items() if GRANT_POINTER in pointers
        )
        self.assertEqual(offenders, ["grant"])

    def test_the_catching_clauses_for_c1_c2_c3_read_only_pack_independent_pointers(self):
        # A required-section check, a subject match and a freshness window --
        # each reusable across every pack that consumes this artifact type, and
        # each parameterised by the acquisition rather than by the pack.
        reads = replay.clause_reads("convention")
        pack_independent = {
            "/status",
            "/counterpartyLegalName",
            "/sections/executionBlock",
            "/observedAt",
            "/checkedSuccessfully",
        }
        for reason in ("subject", "incomplete", "freshness"):
            self.assertLessEqual(set(reads[reason]), pack_independent, reason)

    def test_the_pack_independent_rule_transports_the_whole_artifact_not_a_chosen_field(self):
        # The other half of the clause-granular claim: the `resolved` clause's
        # fact transport. `from: ""` is the whole artifact, so the projection
        # names no field and encodes no knowledge of what any pack will ask.
        self.assertEqual(replay.fact_sources("convention"), [""])
        self.assertEqual(replay.fact_sources("convention-coupled"), [""])
        for name in ("agreement.rule.json", "agreement-coupled.rule.json"):
            with open(os.path.join(HERE, "rules", name), encoding="utf-8") as handle:
                raw = handle.read()
            self.assertNotIn("/agreement/executedGrants", raw, name)

    def test_the_pack_independent_rule_never_names_the_grant_anywhere(self):
        # Stronger than basis and stronger than pointers: the string does not
        # occur in the file at all, in a `when`, in a fact entry, or in prose.
        with open(os.path.join(HERE, "rules", "agreement.rule.json"), encoding="utf-8") as handle:
            plain = handle.read()
        with open(
            os.path.join(HERE, "rules", "agreement-coupled.rule.json"), encoding="utf-8"
        ) as handle:
            coupled = handle.read()
        self.assertNotIn("onwardTransfer", plain)
        self.assertIn("onwardTransfer", coupled)

    def test_c4s_two_rules_take_the_paths_the_readme_says_they_take(self):
        case = cases_by_id()["C4"]
        self.assertEqual(case["derived"]["convention"]["reason"], "resolved")
        self.assertEqual(case["derived"]["convention-coupled"]["reason"], "grant")
        self.assertNotIn(GRANT_POINTER, case["derived"]["convention"]["basis"])
        self.assertIn(GRANT_POINTER, case["derived"]["convention-coupled"]["basis"])


class TheNaiveArm(unittest.TestCase):
    def test_the_naive_arm_consults_no_content_whatever(self):
        # C0, C4 and C6 differ only in content -- the executed grant and the
        # signatory's authority -- and the naive arm cannot tell them apart.
        cases = cases_by_id()
        states = {
            name: naive.naive_availability(
                cases[name]["artifact"], replay.REQUIREMENT_ID
            )
            for name in ("C0", "C1", "C2", "C3", "C4", "C6")
        }
        self.assertEqual(
            list(states.values()),
            [{replay.REQUIREMENT_ID: "present"}] * len(states),
        )

    def test_the_plain_naive_arm_derives_no_facts(self):
        # Scope: this is a claim about `naive_facts`, which models groundings 1
        # and 3 (an evidence-only graph edge, a hand-authored availability
        # fixture). Grounding 2 emits facts, and `credulous_facts` models it.
        for case in replay.load_cases():
            self.assertEqual(naive.naive_facts(case["artifact"]), {})

    def test_the_credulous_naive_arm_asserts_the_packs_fact_from_existence_alone(self):
        # C4's artifact says the grant is false and C0's says it is true; the
        # credulous arm emits `true` for both, because it read neither.
        cases = cases_by_id()
        asserted = {"agreement": {"executedGrants": {"onwardTransfer": True}}}
        for name in ("C0", "C1", "C2", "C3", "C4", "C6"):
            self.assertEqual(naive.credulous_facts(cases[name]["artifact"]), asserted, name)
        self.assertEqual(naive.credulous_facts(cases["C5"]["artifact"]), {})
        self.assertIs(
            derive.get(cases["C4"]["artifact"], GRANT_POINTER), False
        )


class Controls(unittest.TestCase):
    def test_c0_control_the_arms_agree_so_the_set_is_not_rigged(self):
        got = replay.dispositions(cases_by_id()["C0"])
        self.assertEqual(cell(got["naive"]), cell(got["convention"]))
        self.assertEqual(cell(got["naive"]), RELEASE)

    def test_c5_control_divergence_is_confined_to_the_present_branch(self):
        got = replay.dispositions(cases_by_id()["C5"])
        distinct = {cell(disposition) for disposition in got.values()}
        self.assertEqual(distinct, {MISSING})

    def test_c6_control_no_lever_available_today_raises_the_ceiling(self):
        # Complete, executed, current, right counterparty, and the grant the
        # question turns on IS present -- signed by someone without authority.
        # Every arm and every probe that receives an asserted availability state
        # still releases, which is the ADR-0002 ceiling written as a row.
        got = replay.dispositions(cases_by_id()["C6"])
        for combination in (
            "naive",
            "convention",
            "conventionCoupled",
            "conventionClauseFact",
            "naiveCredulousClauseFact",
        ):
            self.assertEqual(cell(got[combination]), RELEASE, combination)

    def test_c6s_catch_is_available_and_its_truth_is_not(self):
        # The label correction: `unreachable` was wrong. A clause CAN catch this
        # fixture -- the field is right there -- and it would be pack-independent
        # in shape. What no clause reaches is whether the field is true.
        case = cases_by_id()["C6"]
        self.assertEqual(case["catchingClause"]["coupling"], "unattested")
        self.assertIs(
            derive.get(case["artifact"], "/signatoryHadDelegatedAuthority"), False
        )
        catching = {
            "ruleVersion": "1",
            "parameters": {},
            "clauses": [
                {
                    "when": {"op": "not", "of": {"op": "isTrue", "field": "/signatoryHadDelegatedAuthority"}},
                    "claim": {"facts": [], "evidence": {replay.REQUIREMENT_ID: "unknown"}, "acquisitionStatus": "unknown"},
                    "reason": "authority",
                },
                {
                    "when": {"op": "always"},
                    "claim": {"facts": [], "evidence": {replay.REQUIREMENT_ID: "present"}, "acquisitionStatus": "resolved"},
                    "reason": "resolved",
                },
            ],
        }
        claim = derive.derive(catching, case["artifact"], {})
        self.assertEqual(claim["reason"], "authority")


class TheClauseFactProbe(unittest.TestCase):
    """Does a pack-side lever for C4 already exist in Core? (ADR-0003's stopping rule.)"""

    def test_the_fact_conditioned_pack_refuses_c4_with_no_vocabulary_change(self):
        got = replay.dispositions(cases_by_id()["C4"])
        self.assertEqual(cell(got["convention"]), RELEASE)
        self.assertEqual(cell(got["conventionClauseFact"]), NO_MATCH)

    def test_the_fact_route_needs_no_pack_knowledge_in_the_acquisition_layer(self):
        # The caveat that flips the verdict, demonstrated rather than asserted:
        # the column that refuses C4 is produced by `agreement.rule.json`, whose
        # clauses read no pointer this pack chose and whose fact transport is a
        # whole-artifact projection. The pack-coupled knowledge lives in the
        # pack's `fact` condition and nowhere in the derivation.
        self.assertEqual(replay.COMBINATIONS["conventionClauseFact"][0], "convention")
        self.assertEqual(replay.fact_sources("convention"), [""])
        reads = replay.clause_reads("convention")
        self.assertEqual(
            [reason for reason, pointers in reads.items() if GRANT_POINTER in pointers], []
        )
        pack = replay.load_pack("release-clause-fact")
        conditions = pack["rules"][0]["when"]["conditions"]
        self.assertEqual(
            [c["path"] for c in conditions if c["op"] == "fact"],
            ["/agreement" + GRANT_POINTER],
        )
        self.assertEqual(cell(replay.dispositions(cases_by_id()["C4"])["conventionClauseFact"]), NO_MATCH)

    def test_the_fact_conditioned_pack_fails_closed_against_omission(self):
        # Half of the asymmetry that decides the verdict. Under the evidence-only
        # pack an acquisition layer that never checks sufficiency fails OPEN (a
        # silent release); under the fact-conditioned pack the same OMISSION
        # fails CLOSED, because the fact the pack names is simply not there and
        # an unresolved pointer is `unknown`.
        cases = cases_by_id()
        for name in ("C0", "C4", "C6"):
            got = replay.dispositions(cases[name])
            self.assertEqual(cell(got["naive"]), RELEASE, name)
            self.assertEqual(cell(got["naiveClauseFact"]), UNKNOWN, name)

    def test_the_fact_conditioned_pack_still_fails_open_against_assertion(self):
        # The other half, which bounds the first. An acquisition layer that
        # ASSERTS the fact it never checked -- the shape the Slack demo's
        # drafting contract already permits -- releases on every row the plain
        # naive arm released on, C4 included. The fact route closes the omission
        # mode and does not touch the fabrication mode; §3.5 says no vocabulary
        # can, which is why the deliverable is guidance.
        cases = cases_by_id()
        for name in ("C0", "C1", "C2", "C3", "C4", "C6"):
            got = replay.dispositions(cases[name])
            self.assertEqual(cell(got["naive"]), RELEASE, name)
            self.assertEqual(cell(got["naiveCredulousClauseFact"]), RELEASE, name)

    def test_the_probe_cannot_distinguish_unsupported_from_unknown(self):
        # The residual an interchange form would address, stated as a test: a
        # pack that never got the sufficiency fact and a pack whose agreement is
        # genuinely unknown reach the identical disposition.
        cases = cases_by_id()
        unsupplied = replay.dispositions(cases["C4"])["naiveClauseFact"]
        genuinely_unknown = replay.dispositions(cases["C2"])["conventionClauseFact"]
        self.assertEqual(cell(unsupplied), cell(genuinely_unknown))


class PacksAndRules(unittest.TestCase):
    def test_both_packs_are_admitted_by_the_evaluator(self):
        for name in ("release-evidence-only", "release-clause-fact"):
            pack = replay.load_pack(name)
            self.assertEqual(pack["specVersion"], "0.2.0-draft")
            # A non-conformant pack raises rather than returning a disposition.
            replay.evaluate(pack, {}, {replay.REQUIREMENT_ID: "present"})

    def test_the_two_packs_differ_only_in_the_release_rule(self):
        evidence_only = replay.load_pack("release-evidence-only")
        clause_fact = replay.load_pack("release-clause-fact")
        for member in ("evidenceRequirements", "outcomes", "escalation"):
            self.assertEqual(evidence_only[member], clause_fact[member], member)
        self.assertNotEqual(evidence_only["rules"], clause_fact["rules"])

    def test_the_coupled_rule_adds_exactly_one_clause(self):
        base = replay.load_rule("convention")["clauses"]
        coupled = replay.load_rule("convention-coupled")["clauses"]
        self.assertEqual(len(coupled), len(base) + 1)
        added = [clause for clause in coupled if clause not in base]
        self.assertEqual([clause["reason"] for clause in added], ["grant"])

    def test_no_rule_uses_an_op_outside_the_shipped_vocabulary(self):
        # The finding this component records rather than fixes: the derivation
        # rule vocabulary has no content predicate, so nothing here may quietly
        # invent one.
        shipped = {
            "always",
            "exists",
            "equals",
            "equalsParam",
            "isTrue",
            "isDecimalString",
            "freshWithin",
            "all",
            "any",
            "not",
        }

        def ops(condition):
            found = {condition["op"]}
            if condition["op"] in ("all", "any"):
                for child in condition["of"]:
                    found |= ops(child)
            elif condition["op"] == "not":
                found |= ops(condition["of"])
            return found

        for name in ("convention", "convention-coupled"):
            for clause in replay.load_rule(name)["clauses"]:
                self.assertLessEqual(ops(clause["when"]), shipped, name)


class TheReadmeTables(unittest.TestCase):
    """`replay.py --table` promises the prose cannot drift from the data.

    Nothing asserted that until now, so the promise was one edit away from being
    false. Each table block the replay builds must appear verbatim in README.md.
    """

    def test_every_table_the_replay_builds_appears_verbatim_in_the_readme(self):
        text = readme()
        for block in replay.tables():
            self.assertIn(block, text, block.splitlines()[0])

    def test_the_readme_has_no_other_case_tables(self):
        # A stale table left behind would still let the assertion above pass.
        text = readme()
        headers = [line for line in text.splitlines() if line.startswith("| # |")]
        self.assertEqual(
            sorted(headers), sorted(block.splitlines()[0] for block in replay.tables())
        )


class FixturesAreSynthetic(unittest.TestCase):
    def test_no_fixture_names_a_real_counterparty_or_carries_real_data(self):
        # TESTING.md's data prohibition: every fixture here is invented. The
        # names are the repository's standing synthetic ones and the pack id is
        # under example.test.
        allowed = {"Northwind Analytics Ltd", "Contoso Data Services GmbH"}
        for case in replay.load_cases():
            name = case["artifact"].get("counterpartyLegalName")
            self.assertIn(name, allowed, case["id"])
        for pack_name in ("release-evidence-only", "release-clause-fact"):
            self.assertTrue(
                replay.load_pack(pack_name)["id"].startswith("https://example.test/"),
                pack_name,
            )

    def test_the_frozen_cases_are_serialized_the_way_they_were_frozen(self):
        for path in replay.case_paths():
            with open(path, encoding="utf-8") as handle:
                raw = handle.read()
            reserialized = (
                json.dumps(
                    json.loads(raw), indent=2, ensure_ascii=False, sort_keys=True
                )
                + "\n"
            )
            self.assertEqual(raw, reserialized, os.path.basename(path))


if __name__ == "__main__":
    unittest.main()
