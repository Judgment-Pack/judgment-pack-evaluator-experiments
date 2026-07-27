#!/usr/bin/env python3
"""Tests for the redaction operator.

These cover the properties the escalation metric rests on: determinism under a fixed seed,
exact one-answerable/one-redacted pairing, the removed pointer being genuinely absent from
the redacted twin and present in its answerable counterpart, no pair whose two variants are
identical, and each of the four guards (presence, participation, locality, non-redundancy)
actually firing.

They deliberately do NOT test the substantive content of loadbearing_map.json -- whether
"maximum_salary_for_player_7_to_9_year_service" really needs the years-of-service fact is a
claim about the CBA, argued in REDACTION.md and auditable against the rule text quoted in
the map, not something a unit test can settle. They also do not require pipeline/out/facts
to exist; every fixture is synthesised in a temp directory.

Run: python -m unittest discover -s pipeline/tests   (or pytest pipeline/tests)
"""

from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PIPELINE))

import redact  # noqa: E402

MAP_PATH = PIPELINE / "loadbearing_map.json"
SEED = 20260727

DEFAULT_RULES = [
    "salary_cap_no_exceed_without_exception",
    "maximum_salary_for_player_7_to_9_year_service",
    "contract_length_at_most_4_year_except_qualifying_veteran_free_agent_5_year",
    "salary_increase_and_decrease_ratio_for_qualiyfing_or_early_qualifying_veteran_free_agent",
]


def player(salary="20000000", team="A", year="2016", pct="5") -> dict:
    return {
        "contract": {
            "annual_change_applies_to": "all_years",
            "annual_change_direction": "increase",
            "annual_change_pct": pct,
            "first_year_salary": salary,
            "salary_kind": "explicit",
            "signed_during": {"kind": "moratorium_period", "year": "2020"},
            "signed_with_team": team,
            "years": "4",
        },
        "draft": {"age_at_draft": "19", "pick": "3", "round": "1", "team": "C", "year": year},
    }


def make_doc(
    instance_id: str = "t_0#001",
    answer: bool = True,
    illegal: str | None = "A",
    problematic: str | None = "A",
    rules: list[str] | None = None,
) -> dict:
    gold: dict = {"answer": answer,
                  "relevant_rules": list(DEFAULT_RULES if rules is None else rules)}
    if illegal is not None:
        gold["illegal_operation"] = illegal
    if problematic is not None:
        gold["problematic_team"] = problematic
    return {
        "contract_version": "facts/v1",
        "instance_id": instance_id,
        "facts": {
            "derived": {},
            "teams": {"A": {"salary": "170000000"}, "B": {"salary": "120000000"}},
            "players": {"A": player(), "B": player("15000000", "B", "2014"), "Z": player()},
            "operations": [
                {
                    "contract": {
                        "annual_change_applies_to": "all_years",
                        "annual_change_direction": "increase",
                        "annual_change_pct": "5",
                        "first_cap_year": "2024-2025",
                        "first_year_salary": "35000000",
                        "salary_kind": "explicit",
                        "years": "3",
                    },
                    "label": "A",
                    "parsed": True,
                    "player": "A",
                    "raw": "A. Team A signs a 3-year contract with Player A providing "
                           "annual salary $35,000,000 and 5% increase per year.",
                    "team": "A",
                    "type": "sign",
                }
            ],
        },
        "gold": gold,
        "provenance": {"source": "rulearena", "commit": "3b9e225", "file": "t_0.json",
                       "index": 1},
    }


class Harness(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="redact-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def write(self, docs: list[dict], name: str = "facts") -> Path:
        d = self.tmp / name
        d.mkdir(parents=True, exist_ok=True)
        for i, doc in enumerate(docs):
            (d / f"{i:03d}.json").write_text(json.dumps(doc, indent=2), encoding="utf-8")
        return d

    def go(self, docs: list[dict], seed: int = SEED, tag: str = "out") -> dict:
        facts = self.write(docs, f"facts-{tag}")
        return redact.run(facts, self.tmp / tag, seed, MAP_PATH, examples=2)

    def twins(self, tag: str, row: dict) -> tuple[dict, dict]:
        base = self.tmp / tag
        return (
            json.loads((base / row["answerable_file"]).read_text(encoding="utf-8")),
            json.loads((base / row["redacted_file"]).read_text(encoding="utf-8")),
        )


# --------------------------------------------------------------------------- #
# JSON Pointer plumbing                                                        #
# --------------------------------------------------------------------------- #
class TestPointers(unittest.TestCase):
    def test_escaping_roundtrip(self) -> None:
        for tokens in (["a/b"], ["m~n"], ["facts", "teams", "A/B~C"]):
            self.assertEqual(redact.ptr_tokens(redact.ptr_build(tokens)), tokens)

    def test_get_exists_delete(self) -> None:
        doc = {"facts": {"teams": {"A": {"salary": "1"}}, "list": [{"k": "v"}]}}
        self.assertEqual(redact.ptr_get(doc, "/facts/teams/A/salary"), "1")
        self.assertTrue(redact.ptr_exists(doc, "/facts/list/0/k"))
        self.assertFalse(redact.ptr_exists(doc, "/facts/list/9/k"))
        self.assertEqual(redact.ptr_delete(doc, "/facts/teams/A/salary"), "1")
        self.assertFalse(redact.ptr_exists(doc, "/facts/teams/A/salary"))

    def test_refuses_array_element_deletion(self) -> None:
        doc = {"facts": {"operations": [{"label": "A"}]}}
        with self.assertRaises(ValueError):
            redact.ptr_delete(doc, "/facts/operations/0")
        with self.assertRaises(ValueError):
            redact.ptr_delete(doc, "")

    def test_expand_template_bindings_and_globs(self) -> None:
        doc = make_doc()
        self.assertEqual(
            redact.expand_template(doc, "/facts/teams/{team}/salary"),
            ["/facts/teams/A/salary", "/facts/teams/B/salary"],
        )
        self.assertEqual(
            redact.expand_template(doc, "/facts/operations/{op}/contract/years"),
            ["/facts/operations/0/contract/years"],
        )
        self.assertIn(
            "/facts/players/A/draft/age_at_draft",
            redact.expand_template(doc, "/facts/players/{player}/draft/*age*"),
        )
        self.assertEqual(redact.expand_template(doc, "/facts/teams/{team}/nope"), [])


# --------------------------------------------------------------------------- #
# Pairing, absence, non-identity                                               #
# --------------------------------------------------------------------------- #
class TestPairing(Harness):
    def test_exact_pairing(self) -> None:
        docs = [make_doc(f"t_0#{i:03d}") for i in range(6)]
        man = self.go(docs)
        counts = man["counts"]
        self.assertEqual(counts["pairs_emitted"], 6)
        self.assertEqual(counts["answerable_twins"], counts["redacted_twins"])
        self.assertEqual(counts["twins_emitted"], 2 * counts["pairs_emitted"])
        self.assertEqual(counts["instances_skipped"], 0)

        files = sorted(p.name for p in (self.tmp / "out").glob("*.json"))
        answerable = [f for f in files if f.endswith("__answerable.json")]
        redacted = [f for f in files if f.endswith("__redacted.json")]
        self.assertEqual(len(answerable), len(redacted), "twins must be balanced")
        self.assertEqual(
            {f.replace("__answerable.json", "") for f in answerable},
            {f.replace("__redacted.json", "") for f in redacted},
        )
        self.assertEqual(len(files), 2 * 6 + 1)  # + manifest.json

    def test_pair_ids_and_expected_decisions(self) -> None:
        docs = [make_doc("t_0#001", answer=True), make_doc("t_0#002", answer=False,
                                                           illegal=None, problematic=None)]
        man = self.go(docs)
        seen = {}
        for row in man["pairs"]:
            a, r = self.twins("out", row)
            self.assertEqual(a["pair_id"], r["pair_id"])
            self.assertEqual(a["variant"], "answerable")
            self.assertEqual(r["variant"], "redacted")
            self.assertEqual(r["expected_decision"], "cannot_decide")
            self.assertIsNone(r["expected_answer"])
            self.assertEqual(a["expected_answer"], a["gold"]["answer"])
            self.assertEqual(
                a["expected_decision"], "illegal" if a["gold"]["answer"] else "legal"
            )
            seen[row["pair_id"]] = row
        self.assertEqual(set(seen), {"t_0#001", "t_0#002"})

    def test_removed_pointer_absent_in_redacted_present_in_answerable(self) -> None:
        docs = [make_doc(f"t_0#{i:03d}") for i in range(8)]
        man = self.go(docs)
        for row in man["pairs"]:
            a, r = self.twins("out", row)
            pointer = row["removed_pointer"]
            self.assertTrue(redact.ptr_exists(a, pointer),
                            f"{pointer} should survive in the answerable twin")
            self.assertFalse(redact.ptr_exists(r, pointer),
                             f"{pointer} should be gone from the redacted twin")
            self.assertEqual(
                redact.ptr_get(a, pointer), r["redaction"]["removed_value"],
                "the recorded removed value must be what the answerable twin still holds",
            )

    def test_no_pair_is_identical(self) -> None:
        docs = [make_doc(f"t_0#{i:03d}") for i in range(8)]
        man = self.go(docs)
        self.assertTrue(man["pairs"])
        for row in man["pairs"]:
            a, r = self.twins("out", row)
            self.assertNotEqual(a["facts"], r["facts"])

    def test_exactly_one_fact_removed(self) -> None:
        docs = [make_doc(f"t_0#{i:03d}") for i in range(8)]
        man = self.go(docs)
        for row in man["pairs"]:
            a, r = self.twins("out", row)
            before = {p for p, _ in redact.iter_leaves({"facts": a["facts"]})}
            after = {p for p, _ in redact.iter_leaves({"facts": r["facts"]})}
            self.assertEqual(after - before, set(), "redaction must not add anything")
            missing = before - after
            self.assertTrue(
                len(missing) >= 1 and all(m.startswith(row["removed_pointer"]) for m in missing),
                f"only {row['removed_pointer']} may disappear, got {sorted(missing)}",
            )

    def test_skips_instance_with_no_cited_rules(self) -> None:
        doc = make_doc("t_0#009", rules=[])
        man = self.go([doc])
        self.assertEqual(man["counts"]["pairs_emitted"], 0)
        self.assertEqual(man["counts"]["instances_skipped"], 1)
        self.assertIn("relevant_rules", man["skipped"][0]["reason"])
        self.assertEqual(list((self.tmp / "out").glob("*__*.json")), [],
                         "a skipped instance must not leave a lone twin behind")


# --------------------------------------------------------------------------- #
# Determinism                                                                  #
# --------------------------------------------------------------------------- #
class TestDeterminism(Harness):
    def test_same_seed_same_bytes(self) -> None:
        docs = [make_doc(f"t_0#{i:03d}") for i in range(10)]
        self.go(docs, SEED, "run1")
        self.go(docs, SEED, "run2")
        names = sorted(p.name for p in (self.tmp / "run1").glob("*.json"))
        self.assertTrue(names)
        for name in names:
            first = (self.tmp / "run1" / name).read_bytes()
            second = (self.tmp / "run2" / name).read_bytes()
            if name == "manifest.json":
                # the manifest records its own output directory
                first = first.replace(b"run1", b"RUN").replace(b"facts-run1", b"F")
                second = second.replace(b"run2", b"RUN").replace(b"facts-run2", b"F")
            self.assertEqual(first, second, f"{name} is not byte-identical across runs")

    def test_choice_is_independent_of_corpus_size_and_order(self) -> None:
        docs = [make_doc(f"t_0#{i:03d}") for i in range(10)]
        full = {r["pair_id"]: r["removed_pointer"] for r in self.go(docs, SEED, "full")["pairs"]}
        subset = list(reversed(docs[3:6]))
        part = {r["pair_id"]: r["removed_pointer"]
                for r in self.go(subset, SEED, "part")["pairs"]}
        self.assertTrue(part)
        for pair_id, pointer in part.items():
            self.assertEqual(full[pair_id], pointer,
                             "an instance's chosen fact must not depend on its neighbours")

    def test_a_different_seed_moves_at_least_one_choice(self) -> None:
        docs = [make_doc(f"t_0#{i:03d}") for i in range(20)]
        a = {r["pair_id"]: r["removed_pointer"] for r in self.go(docs, SEED, "sa")["pairs"]}
        b = {r["pair_id"]: r["removed_pointer"] for r in self.go(docs, SEED + 1, "sb")["pairs"]}
        self.assertNotEqual(a, b, "the seed must actually drive selection")


# --------------------------------------------------------------------------- #
# Guards                                                                       #
# --------------------------------------------------------------------------- #
class TestGuards(Harness):
    def test_never_deletes_an_absent_fact(self) -> None:
        docs = [make_doc(f"t_0#{i:03d}") for i in range(12)]
        man = self.go(docs)
        for row in man["pairs"]:
            a, _ = self.twins("out", row)
            self.assertTrue(redact.ptr_exists(a, row["removed_pointer"]))

    def test_never_deletes_a_derived_quantity(self) -> None:
        doc = make_doc("t_0#001")
        doc["facts"]["derived"] = {
            "teams": {"A": {"team_salary_after_operation_A": "205000000"}}
        }
        man = self.go([doc] + [make_doc(f"t_0#{i:03d}") for i in range(2, 14)])
        self.assertTrue(man["pairs"])
        for row in man["pairs"]:
            self.assertFalse(row["removed_pointer"].startswith("/facts/derived"))

    def test_participation_guard_skips_uninvolved_players(self) -> None:
        docs = [make_doc(f"t_0#{i:03d}") for i in range(40)]
        man = self.go(docs)
        for row in man["pairs"]:
            self.assertNotIn("/facts/players/Z/", row["removed_pointer"],
                             "player Z takes part in no operation and decides nothing")

    def test_locality_guard_when_gold_says_illegal(self) -> None:
        docs = []
        for i in range(30):
            d = make_doc(f"t_0#{i:03d}", answer=True, illegal="A", problematic="A")
            d["facts"]["operations"].append({
                "contract": {"first_year_salary": "5000000", "years": "2",
                             "annual_change_pct": "5",
                             "annual_change_direction": "increase",
                             "salary_kind": "explicit"},
                "label": "B", "parsed": True, "player": "B", "raw": "B. Team B signs ...",
                "team": "B", "type": "sign",
            })
            docs.append(d)
        man = self.go(docs)
        self.assertTrue(man["pairs"])
        for row in man["pairs"]:
            self.assertEqual(row["strength_basis"], "localized")
            pointer = row["removed_pointer"]
            self.assertFalse(pointer.startswith("/facts/teams/B/"), pointer)
            self.assertFalse(pointer.startswith("/facts/players/B/"), pointer)
            self.assertFalse(pointer.startswith("/facts/operations/1/"), pointer)

    def test_universal_basis_when_gold_says_legal(self) -> None:
        docs = [make_doc(f"t_0#{i:03d}", answer=False, illegal=None, problematic=None)
                for i in range(6)]
        man = self.go(docs)
        self.assertTrue(man["pairs"])
        for row in man["pairs"]:
            self.assertEqual(row["strength_basis"], "universal")

    def test_derived_supersession_marks_the_twin_weak(self) -> None:
        """Only team.salary is deletable, and derived already publishes the same team."""
        doc = make_doc("t_0#001", answer=False, illegal=None, problematic=None,
                       rules=["traded_player_exception_250k_reduced_first_apron_level"])
        doc["facts"]["operations"][0]["team"] = "A"
        clean = self.go([copy.deepcopy(doc)], SEED, "clean")
        self.assertEqual(clean["pairs"][0]["removed_pointer"], "/facts/teams/A/salary")
        self.assertEqual(clean["pairs"][0]["strength"], "strong")

        doc["facts"]["derived"] = {"teams": {"A": {"team_salary_after_operations": "205000000"}}}
        dirty = self.go([doc], SEED, "dirty")
        row = dirty["pairs"][0]
        self.assertEqual(row["strength"], "weak")
        self.assertFalse(row["in_primary_analysis"])
        self.assertTrue(any("superseded by derived" in w for w in row["weak_reasons"]))
        self.assertEqual(dirty["counts"]["weak_pairs_excluded_from_primary"], 1)
        self.assertEqual(dirty["counts"]["pairs_emitted"], 1,
                         "a weak pair is still emitted, only excluded from the primary set")

    def test_sibling_redundancy_marks_the_twin_weak(self) -> None:
        """salary_kind='explicit' says nothing while first_year_salary sits beside it."""
        doc = make_doc("t_0#001", answer=False, illegal=None, problematic=None,
                       rules=["contract_length_at_most_2_year_minimum_player_salary_exception"])
        del doc["facts"]["operations"][0]["contract"]["years"]
        man = self.go([doc])
        row = man["pairs"][0]
        self.assertEqual(row["removed_pointer"], "/facts/operations/0/contract/salary_kind")
        self.assertEqual(row["strength"], "weak")
        self.assertTrue(any("implied by sibling key" in w for w in row["weak_reasons"]))

    def test_prose_leak_marks_the_twin_weak(self) -> None:
        doc = make_doc("t_0#001", answer=False, illegal=None, problematic=None,
                       rules=["traded_player_exception_250k_reduced_first_apron_level"])
        doc["facts"]["teams"]["A"]["note"] = "team salary is 170000000 before the signing"
        man = self.go([doc])
        row = man["pairs"][0]
        self.assertEqual(row["removed_pointer"], "/facts/teams/A/salary")
        self.assertEqual(row["strength"], "weak")
        self.assertTrue(any("still spelled out" in w for w in row["weak_reasons"]))

    def test_render_excluded_prose_does_not_weaken_the_twin(self) -> None:
        """operations[].raw echoes everything; the render policy is what neutralises it."""
        doc = make_doc("t_0#001", answer=False, illegal=None, problematic=None,
                       rules=["traded_player_exception_250k_reduced_first_apron_level"])
        doc["facts"]["operations"][0]["raw"] = "Team A has a team salary of 170000000."
        man = self.go([doc])
        row = man["pairs"][0]
        self.assertEqual(row["strength"], "strong")
        self.assertEqual(row["echoed_in_render_excluded_fields"],
                         ["/facts/operations/0/raw"])
        _, r = self.twins("out", row)
        self.assertFalse(
            redact.is_renderable("/facts/operations/0/raw", r["render_policy"]),
            "the harness contract must forbid rendering the prose echo",
        )
        self.assertTrue(redact.is_renderable("/facts/teams/A/salary", r["render_policy"]))
        self.assertFalse(redact.is_renderable("/gold/answer", r["render_policy"]))


# --------------------------------------------------------------------------- #
# The map itself is well formed                                                #
# --------------------------------------------------------------------------- #
class TestMap(unittest.TestCase):
    def setUp(self) -> None:
        self.map = json.loads(MAP_PATH.read_text(encoding="utf-8"))

    def test_every_required_role_is_defined(self) -> None:
        roles = set(self.map["roles"])
        for rule_id, rule in self.map["rules"].items():
            self.assertTrue(rule["required_roles"], f"{rule_id} requires nothing")
            for role in rule["required_roles"]:
                self.assertIn(role, roles, f"{rule_id} names undefined role {role}")

    def test_every_rule_carries_its_verbatim_text(self) -> None:
        for rule_id, rule in self.map["rules"].items():
            self.assertTrue(rule["rule_text_verbatim"].strip(), rule_id)
            self.assertTrue(rule["rule_text_source"].strip(), rule_id)

    def test_aliases_resolve(self) -> None:
        for rule_id, rule in self.map["rules"].items():
            canonical = rule.get("alias_of")
            if canonical is not None:
                self.assertIn(canonical, self.map["rules"], rule_id)

    def test_pointer_alternatives_are_well_formed(self) -> None:
        for role, definition in self.map["roles"].items():
            alts = definition["pointer_alternatives"]
            self.assertTrue(alts, role)
            for template in alts:
                self.assertTrue(template.startswith("/facts/"), f"{role}: {template}")
                self.assertFalse(template.startswith("/facts/derived"),
                                 f"{role}: derived values are never deletion candidates")

    def test_covers_every_rule_rulearena_actually_cites(self) -> None:
        problems = (PIPELINE.parent / "rulearena" / "checkout" / "nba" / "annotated_problems")
        if not problems.is_dir():
            self.skipTest("RuleArena checkout not present")
        cited: set[str] = set()
        for name in ("comp_0.json", "comp_1.json", "comp_2.json"):
            for instance in json.loads((problems / name).read_text(encoding="utf-8")):
                cited.update(instance.get("relevant_rules", []))
        self.assertEqual(cited - set(self.map["rules"]), set(),
                         "every gold rule id must have a required-fact entry")


if __name__ == "__main__":
    unittest.main(verbosity=2)
