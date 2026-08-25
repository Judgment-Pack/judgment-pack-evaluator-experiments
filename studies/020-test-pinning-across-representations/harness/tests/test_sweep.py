#!/usr/bin/env python3
"""The pre-pilot effort sweep — PREREGISTRATION.md §2.1, rulings M-8/M-20/M-24/M-25.

§2.1 registered a sweep the harness had no mode for: `n = 3/arm across three
settings — 27 calls`, run through this apparatus and never outside it, published
in full, `citable: false`, outside every population, with a per-setting abort
rule and a call cap. `batch.py sweep` is that mode, and this file is where each
registered sentence is driven rather than restated.

FOUR THINGS THIS FILE IS CAREFUL ABOUT, because each of them is a way a suite
can pass while the thing it names does not work:

1. **The registered SET is bound in three places at once** — §2.1's own
   paragraph, `harness/PINS.json`'s `sweep.settings` and `batch.SWEEP_SETTINGS`.
   A test that read the constant and asserted the constant would pass under any
   edit at all, so the constant is read against the registration's BYTES,
   currency-style, exactly as `test_prereg_currency.py` binds the study's other
   registered numbers.

2. **The abort rule is driven, both clauses, through the stand-in CLI** — not
   asserted about a hand-built dictionary alone. A unit case over synthetic
   calls pins the arithmetic (and reproduces §2.1's own printed 51.46 h figure
   from the registration's own triple, so the driver and the table agree on what
   "beyond 72 h" means); the end-to-end cases then make the real driver make
   real wrapper calls and stop where the rule says.

3. **The occupancy gate is driven in BOTH directions.** "The sweep root is
   outside `arms/`, so R10-1 cannot see it" is a claim about
   `make_manifest.prior_authoring_problems()`, and a test that only built a
   sweep tree and saw the gate pass would pass equally if the gate were broken
   for every tree. So the same fixture builds an `arms/<ARM>/authoring` tree and
   requires the refusal.

4. **The witness resolution is driven on transcripts that differ in the one way
   that matters.** M-24's two branches turn on a NON-NULL member inside a
   `turn_context` payload. Three synthetic transcripts: one with a non-null
   member there (gate-5 branch), one with the member present and NULL — 019's
   actual state, and the reason M-24 is a ruling — and one with a non-null
   member in a record that is not a `turn_context`, which is real evidence and
   is NOT a gate-5 witness, because gate 5 is a `turn_context` gate.
"""
from __future__ import annotations
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

import batch
import integrity
import make_manifest

from test_batch import (HARNESS, REGISTRY, STUDY, HAVE_TOOLS,
                        RUNNING_REGISTERED, StandInStudy, write_plan)

PREREG = os.path.join(STUDY, "PREREGISTRATION.md")


def prereg_text() -> str:
    with open(PREREG, "rb") as handle:
        return handle.read().decode("utf-8")


def registry() -> dict:
    with open(REGISTRY) as handle:
        return json.load(handle)


# --- the registered constants, bound to the registration's own bytes ---------

class TheRegisteredSet(unittest.TestCase):
    """§2.1's swept SET, registered 2026-08-24 before the sweep, in the three
    places it is carried — and the three must be one registration."""

    def test_the_settings_constant_is_the_registrations_own_three(self):
        """CURRENCY-STYLE: read out of §2.1's bytes, not out of the constant.

        The registration names the three tiers inside a block quote of its own,
        so the assertion can be made against the sentence a reader would read
        rather than against a phrase this test chose."""
        # Unwrapped first: the registration is prose and its block quote is
        # hard-wrapped, so the sentence a reader reads spans two lines.
        text = prereg_text().replace("\n> ", " ")
        quoted = re.search(
            r"\*\*The swept set is the pinned CLI's own named "
            r"reasoning-effort tiers ([^*]+), in that order\.\*\*", text)
        self.assertIsNotNone(
            quoted, "§2.1 no longer carries the dated swept-set registration in "
                    "the shape this test reads it in")
        named = tuple(name.strip(" `")
                      for name in quoted.group(1).replace("and ", "").split(","))
        self.assertEqual(named, batch.SWEEP_SETTINGS)

    def test_the_registration_is_dated_and_is_before_the_sweep(self):
        """A decision recorded after the durations were seen is a picked set and
        not a swept one, so the DATE and the word `before` are part of what is
        registered."""
        text = prereg_text()
        self.assertIn("registered 2026-08-24, before the sweep", text)
        self.assertIn("Naming three tiers is not choosing one", text)

    def test_the_chosen_condition_todo_is_filled(self):
        """The set was registered before the sweep; the CHOICE was made from
        the sweep's published output by the named rule, and every carrier of
        the condition agrees: the preregistration's fill, the sweep registry
        block, and the effort pin."""
        text = prereg_text()
        self.assertIn("FILLED, 2026-08-24 — the registered compute condition",
                      text)
        self.assertIn("operable-condition-match", text)
        self.assertEqual(registry()["sweep"]["chosenSetting"], "low")
        self.assertEqual(registry()["codex"]["reasoningEffort"], "low")
        # `batch.n` is the third carrier of the same fact. Pre-fill it held
        # 019's count as a PORT CARRY and this assertion read that sentence;
        # §2.1's fill registered N = 60 (the branch §5.6's simulations price)
        # with the order re-derived at 60 rounds, and the note's flip sentence
        # is what this assertion reads now. `tests/test_schedule.py`'s
        # `test_the_registry_says_its_round_count_is_registered_at_sixty`
        # drives the rest of it.
        self.assertIn("REGISTERED AT N = 60/ARM",
                      registry()["batch"]["note"])

    def test_the_registry_and_the_driver_carry_one_set(self):
        pins = registry()
        self.assertEqual(pins["sweep"]["settings"], list(batch.SWEEP_SETTINGS))
        self.assertEqual(pins["sweep"]["perArm"], batch.SWEEP_PER_ARM)
        self.assertEqual(pins["sweep"]["callCap"], batch.SWEEP_CALL_CAP)
        self.assertEqual(pins["sweep"]["budgetHours"], batch.SWEEP_BUDGET_HOURS)
        self.assertEqual(pins["sweep"]["budgetProjectionN"],
                         batch.SWEEP_BUDGET_PROJECTION_N)
        self.assertEqual(pins["sweep"]["root"],
                         os.path.basename(batch.SWEEP_ROOT))
        self.assertIs(pins["sweep"]["citable"], False)

    def test_the_cap_is_derived_and_is_the_registered_twenty_seven(self):
        """§2.1 registers `3 settings × 3/arm — 27 calls`. The cap is COMPUTED
        from the set and the per-arm count, so a fourth setting cannot leave the
        registered arithmetic behind while the number stays 27."""
        self.assertEqual(batch.SWEEP_CALL_CAP, 27)
        self.assertEqual(
            batch.SWEEP_CALL_CAP,
            len(batch.SWEEP_SETTINGS) * len(batch.ARMS) * batch.SWEEP_PER_ARM)
        self.assertIn("27 calls", prereg_text())

    def test_the_uncapped_tiers_are_named_and_gated_by_the_deviation_clause(self):
        text = prereg_text()
        self.assertIn("`xhigh`, `max` and `ultra` are therefore **not swept**",
                      text)
        self.assertIn("DEVIATIONS.md", text)
        for tier in ("xhigh", "max", "ultra"):
            self.assertNotIn(tier, batch.SWEEP_SETTINGS)
        self.assertIn("a **budget** decision and not an availability one", text)

    def test_the_effort_flag_spelling_is_resolved_and_is_two_members(self):
        """The empirical resolution of §2.1's spelling TODO: the pinned CLI has
        no reasoning-effort flag, so the seat is `-c` plus a config KEY. Two
        members, because one cannot carry `FLAG` and `KEY=VALUE` both."""
        codex = registry()["codex"]
        self.assertEqual(codex["reasoningEffortFlag"], "-c")
        self.assertEqual(codex["reasoningEffortConfigKey"],
                         "model_reasoning_effort")
        self.assertIn("2026-08-24", codex["reasoningEffortFlagProvenance"])
        self.assertIn("no reasoning-effort flag",
                      codex["reasoningEffortFlagProvenance"])
        text = prereg_text()
        self.assertIn("`-c model_reasoning_effort=<tier>`", text)
        self.assertIn("**CLOSED, 2026-08-24**", text)

    def test_the_witness_half_of_that_todo_is_closed(self):
        """A spelling was resolvable from `--help`; the witness needed a call,
        and the sweep's step zero supplied it: branch `gate-5-extension`,
        recorded in the pin and filled into the preregistration, with the
        gate's extension landing in the same change set."""
        text = prereg_text()
        self.assertIn("The WITNESS half is **CLOSED, 2026-08-24", text)
        self.assertIn("gate-5-extension", text)
        self.assertEqual(registry()["codex"]["reasoningEffortWitness"],
                         "gate-5-extension")


# --- the schedule --------------------------------------------------------------

class TheSweepSchedule(unittest.TestCase):

    def test_it_is_arm_interleaved_with_a_first(self):
        """A first because the abort rule reads "the setting's FIRST arm-A
        call"; interleaved because the projection needs a mean for every arm and
        interleaving reaches one per arm after three calls rather than seven."""
        order = [(entry["arm"], entry["runIndex"])
                 for entry in batch.sweep_schedule("low")]
        self.assertEqual(order, [("A", 1), ("B", 1), ("C", 1),
                                 ("A", 2), ("B", 2), ("C", 2),
                                 ("A", 3), ("B", 3), ("C", 3)])
        self.assertEqual(order[0][0], "A")
        self.assertEqual(order[0][0], batch.ARMS[0])

    def test_the_first_call_of_a_setting_is_its_first_arm_a_call(self):
        """The property the abort rule's first clause stands on, asserted as a
        property rather than read off the list above."""
        entries = batch.sweep_schedule("low")
        first_a = next(entry for entry in entries if entry["arm"] == "A")
        self.assertEqual(first_a["indexWithinSetting"], 1)
        self.assertEqual(entries[0], first_a)

    def test_one_setting_is_nine_calls_and_three_settings_are_the_cap(self):
        self.assertEqual(len(batch.sweep_schedule("low")),
                         len(batch.ARMS) * batch.SWEEP_PER_ARM)
        total = sum(len(batch.sweep_schedule(name))
                    for name in batch.SWEEP_SETTINGS)
        self.assertEqual(total, batch.SWEEP_CALL_CAP)

    def test_the_slot_path_is_the_registered_shape(self):
        label = batch.sweep_label("2026-08-24")
        self.assertEqual(label, "2026-08-24-effort-sweep")
        slot = batch.sweep_slot_path(label, "medium", "B", 2)
        self.assertEqual(
            os.path.relpath(slot, batch.STUDY),
            os.path.join("sweeps", label, "medium", "arm-B", "run-002"))
        self.assertIn(
            "sweeps/<UTC date>-effort-sweep/<setting>/arm-<ARM>/run-NNN",
            prereg_text())

    def test_a_call_at_the_cli_default_lands_under_the_registered_literal(self):
        """A sweep call with no threaded setting is a call at the CLI's own
        default, and it needs a directory name: an empty path component is one
        component fewer, and the wrapper's anchor counts components."""
        label = batch.sweep_label("2026-08-24")
        self.assertIn("/default/",
                      batch.sweep_slot_path(label, None, "A", 1))

    def test_an_unregistered_arm_refuses(self):
        with self.assertRaises(batch.BatchError):
            batch.sweep_slot_path("x-effort-sweep", "low", "D", 1)


# --- M-24's witness resolution -------------------------------------------------

def transcript(path: str, rows: list) -> str:
    with open(path, "wb") as handle:
        for row in rows:
            handle.write((json.dumps(row) + "\n").encode("utf-8"))
    return path


class TheWitnessResolution(unittest.TestCase):
    """M-24, driven on synthetic transcripts that differ in the one way the
    ruling turns on."""

    def setUp(self):
        self.root = os.path.join(
            os.path.realpath(os.environ.get("TMPDIR", "/tmp")),
            "s020-witness-%d" % os.getpid())
        os.makedirs(self.root, exist_ok=True)
        self.addCleanup(shutil.rmtree, self.root, True)

    def path(self, name: str) -> str:
        return os.path.join(self.root, name)

    def test_a_non_null_turn_context_member_takes_the_gate_five_branch(self):
        """Branch one. The obligation the sweep publishes with it is the gate-5
        extension — and the sweep publishes it, it does not perform it."""
        session = transcript(self.path("witnessed.jsonl"), [
            {"type": "session_meta", "payload": {"id": "s1"}},
            {"type": "turn_context",
             "payload": {"model": "gpt-5.6-sol", "cwd": "/w",
                         "collaboration_mode": {
                             "settings": {"reasoning_effort": "high"}}}},
        ])
        found = batch.effort_witness(session)
        self.assertEqual(found["branch"], batch.WITNESS_BRANCH_GATE5)
        self.assertEqual(len(found["turnContextOccurrences"]), 1)
        self.assertEqual(found["turnContextOccurrences"][0]["value"], "high")
        self.assertEqual(
            found["turnContextOccurrences"][0]["member"],
            "collaboration_mode.settings.reasoning_effort")
        self.assertIn("transcript gate 5 is EXTENDED", found["obligation"])
        self.assertIn("does not amend the gate", found["obligation"])

    def test_a_null_member_is_not_a_witness_and_takes_the_self_report_branch(self):
        """Branch two, on 019's ACTUAL state: the member is present and holds
        null, which a membership-idiom turn-context binding would refuse every call
        against. Reporting "no occurrences" here would make the next reader
        re-do this work to learn whether it was absent or empty."""
        session = transcript(self.path("null.jsonl"), [
            {"type": "turn_context",
             "payload": {"model": "gpt-5.6-sol", "cwd": "/w",
                         "collaboration_mode": {
                             "settings": {"model": "gpt-5.6-sol",
                                          "reasoning_effort": None}}}},
        ])
        found = batch.effort_witness(session)
        self.assertEqual(found["branch"], batch.WITNESS_BRANCH_SELF_REPORT)
        self.assertEqual(found["turnContextOccurrences"], [])
        self.assertEqual(len(found["nullOccurrences"]), 1)
        self.assertIn("SELF-REPORT", found["obligation"])
        self.assertIn("not independently witnessed", found["obligation"])

    def test_a_non_turn_context_occurrence_is_reported_and_does_not_decide(self):
        """Gate 5 is a `turn_context` gate. A non-null member somewhere else is
        real evidence and is published as such — and it is not silently promoted
        into a witness for a gate that would never read it."""
        session = transcript(self.path("elsewhere.jsonl"), [
            {"type": "turn_context", "payload": {"model": "m", "cwd": "/w"}},
            {"type": "event_msg",
             "payload": {"type": "note", "reasoning_effort": "high"}},
        ])
        found = batch.effort_witness(session)
        self.assertEqual(found["branch"], batch.WITNESS_BRANCH_SELF_REPORT)
        self.assertEqual(len(found["otherOccurrences"]), 1)
        self.assertEqual(found["otherOccurrences"][0]["recordType"], "event_msg")
        self.assertIn("gate 5 is a turn_context gate", found["note"])

    def test_the_search_reaches_a_member_three_levels_down(self):
        """The occurrence M-24 actually found is nested three deep. A top-level
        key scan would have reported "no member names the effort" about a
        transcript that names it."""
        session = transcript(self.path("deep.jsonl"), [
            {"type": "turn_context",
             "payload": {"a": {"b": [{"reasoning_effort": "medium"}]}}},
        ])
        found = batch.effort_witness(session)
        self.assertEqual(found["branch"], batch.WITNESS_BRANCH_GATE5)
        self.assertEqual(found["turnContextOccurrences"][0]["member"],
                         "a.b[0].reasoning_effort")

    def test_an_absent_transcript_refuses_rather_than_resolving_a_branch(self):
        with self.assertRaises(batch.BatchError) as caught:
            batch.effort_witness(self.path("nothing.jsonl"))
        self.assertIn("resolves nothing", str(caught.exception))

    def test_the_reasoning_token_count_is_read_where_the_transcript_carries_it(self):
        """§2.1's publication obligation names the column. It is read by PATH:
        `last_token_usage` carries the same member name for a different
        quantity, and a recursive name search would publish whichever came
        first in dict order."""
        session = transcript(self.path("tokens.jsonl"), [
            {"type": "event_msg",
             "payload": {"type": "token_count",
                         "info": {"last_token_usage":
                                  {"reasoning_output_tokens": 11},
                                  "total_token_usage":
                                  {"reasoning_output_tokens": 1958}}}},
        ])
        self.assertEqual(batch.reasoning_output_tokens(session), 1958)

    def test_a_transcript_without_the_column_publishes_no_number(self):
        """A row with no token count is published as a row with no token count,
        not as a zero."""
        session = transcript(self.path("none.jsonl"), [
            {"type": "turn_context", "payload": {"model": "m"}},
        ])
        self.assertIsNone(batch.reasoning_output_tokens(session))
        self.assertIsNone(batch.reasoning_output_tokens(self.path("gone.jsonl")))


# --- the abort rule, as arithmetic ---------------------------------------------

def synthetic_calls(durations: dict, per_arm: int = 1, code=None) -> list:
    calls, index = [], 0
    for run_index in range(1, per_arm + 1):
        for arm in batch.ARMS:
            index += 1
            calls.append({"setting": "low", "arm": arm, "runIndex": run_index,
                          "indexWithinSetting": index,
                          "durationSeconds": durations[arm], "code": code})
    return calls


class TheAbortRuleArithmetic(unittest.TestCase):
    """Both clauses, at the numbers §2.1 prints."""

    def test_the_projection_reproduces_the_registrations_own_figure(self):
        """§2.1's dual-pricing table prints 51.46 h for the pilot-like triple
        1660.184 + 803.042 + 624.114 s at N = 60/arm. The driver computes the
        projection the same way the registration priced it, so "beyond 72 h"
        means one number to both."""
        triple = {"A": 1660.184, "B": 803.042, "C": 624.114}
        hours = batch.projected_batch_hours(triple, 60)
        self.assertAlmostEqual(hours, 51.46, places=2)
        self.assertIn("51.46 h", prereg_text())

    def test_a_partial_triple_refuses_rather_than_understating_the_batch(self):
        with self.assertRaises(batch.BatchError) as caught:
            batch.projected_batch_hours({"A": 100.0, "B": 100.0}, 60)
        self.assertIn("understating it is the direction that spends",
                      str(caught.exception))

    def test_clause_one_fires_on_the_first_arm_a_call_over_the_ceiling(self):
        calls = [{"setting": "low", "arm": "A", "runIndex": 1,
                  "indexWithinSetting": 1,
                  "durationSeconds": batch.CALL_TIMEOUT_SECONDS + 1,
                  "code": None}]
        verdict = batch.sweep_abort_verdict(calls, 60, "test")
        self.assertEqual(verdict["verdict"], "aborted")
        self.assertEqual(verdict["clause"], "first-arm-A-call-over-ceiling")
        self.assertIs(verdict["abortingCall"], calls[0])

    def test_clause_one_does_not_fire_on_a_later_arm_a_call(self):
        """"FIRST arm-A call" is a registered word. A later arm-A call over the
        ceiling is a slow call and is published as one; it is not this clause."""
        calls = synthetic_calls({"A": 1.0, "B": 1.0, "C": 1.0})
        calls.append({"setting": "low", "arm": "A", "runIndex": 2,
                      "indexWithinSetting": 4,
                      "durationSeconds": batch.CALL_TIMEOUT_SECONDS + 1,
                      "code": None})
        self.assertIsNone(batch.sweep_abort_verdict(calls, 1, "test")["verdict"])

    def test_clause_two_records_out_of_budget_and_names_it_differently(self):
        """Two clauses, two words. `aborted` is a call past the apparatus
        ceiling; `out-of-budget` is arithmetic. One word for both would leave
        the published table unable to say which happened."""
        calls = synthetic_calls({"A": 2000.0, "B": 1500.0, "C": 1500.0})
        verdict = batch.sweep_abort_verdict(calls, 60, "the priced branch")
        self.assertEqual(verdict["verdict"], "out-of-budget")
        self.assertEqual(verdict["clause"], "projected-batch-over-budget")
        self.assertGreater(verdict["projectedBatchHours"],
                           batch.SWEEP_BUDGET_HOURS)

    def test_clause_two_needs_every_arm_before_it_can_fire(self):
        """The projection is over a TRIPLE. Two arms cannot price a batch of
        three, and firing on two would abort settings on an understatement."""
        calls = [call for call in synthetic_calls({"A": 2600.0, "B": 2600.0,
                                                   "C": 1.0})
                 if call["arm"] in ("A", "B")]
        verdict = batch.sweep_abort_verdict(calls, 60, "test")
        self.assertIsNone(verdict["verdict"])
        self.assertIsNone(verdict["projectedBatchHours"])

    def test_a_refused_call_contributes_no_duration_to_a_mean(self):
        """A call that never reached the model is not evidence about what the
        model costs. It is published with its code and it prices nothing."""
        calls = synthetic_calls({"A": 2000.0, "B": 2000.0, "C": 2000.0},
                                code="wrapper-nonzero")
        verdict = batch.sweep_abort_verdict(calls, 60, "test")
        self.assertIsNone(verdict["verdict"])
        self.assertEqual(verdict["perArmMeanSeconds"], {})

    def test_a_setting_within_budget_continues_and_publishes_its_projection(self):
        calls = synthetic_calls({"A": 100.0, "B": 100.0, "C": 100.0})
        verdict = batch.sweep_abort_verdict(calls, 60, "test")
        self.assertIsNone(verdict["verdict"])
        self.assertAlmostEqual(verdict["projectedBatchHours"], 5.0, places=6)

    def test_the_budget_n_is_the_priced_branch_until_batch_n_is_filled(self):
        """Both branches, driven over a registry that has each state. The
        committed registry now carries §7 delta 7's port carry rather than a
        null, so the PRICED branch is exercised over an explicitly emptied copy
        — the rule is about what the driver does with a registry, and a rule
        only ever tested against today's registry is a rule that stops being
        tested the moment the registry moves."""
        pins = registry()
        empty = copy.deepcopy(pins)
        empty["batch"]["n"] = None
        n, source = batch.sweep_budget_n(empty)
        self.assertEqual(n, batch.SWEEP_BUDGET_PROJECTION_N)
        self.assertIn("priced branch", source)
        filled = copy.deepcopy(pins)
        filled["batch"]["n"] = 42
        self.assertEqual(batch.sweep_budget_n(filled), (42, "batch.n"))
        # …and the committed registry takes the second branch, because it has a
        # count. The ledger records WHICH, which is the property that matters.
        self.assertEqual(batch.sweep_budget_n(pins),
                         (pins["batch"]["n"], "batch.n"))


# --- the sweep root and the freeze gates ---------------------------------------

class TheSweepRootAndTheOccupancyGate(unittest.TestCase):
    """R10-1's `prior_authoring_problems()`, driven in BOTH directions.

    A test that built a sweep tree and saw the gate pass would pass equally if
    the gate were broken for every tree, so the same fixture builds an
    `arms/<ARM>/authoring` tree and requires the refusal."""

    def setUp(self):
        self.root = os.path.realpath(
            os.path.join(os.environ.get("TMPDIR", "/tmp"),
                         "s020-occupancy-%d" % os.getpid()))
        shutil.rmtree(self.root, ignore_errors=True)
        os.makedirs(self.root)
        self.addCleanup(shutil.rmtree, self.root, True)
        subprocess.run(["git", "init", "-q", self.root], check=True)

    def test_the_two_roots_are_one_name_in_both_modules(self):
        self.assertEqual(make_manifest.SWEEP_ROOT,
                         os.path.basename(batch.SWEEP_ROOT))
        self.assertEqual(os.path.dirname(batch.SWEEP_ROOT), batch.STUDY)
        self.assertNotEqual(batch.SWEEP_ROOT, batch.ARMS_ROOT)
        self.assertNotEqual(batch.SWEEP_ROOT, batch.CALIBRATION_ROOT)

    def test_the_occupancy_gate_does_not_reach_the_sweep_root(self):
        """The whole reason the sweep is not in `arms/`. It is STRUCTURAL — the
        gate derives its paths from `authoring_state_paths()`, which walks
        `slot_path()` under `ARMS_ROOT` — so this needs no exclusion entry, and
        this case is what says so about the code rather than about the comment."""
        slot = os.path.join(self.root, make_manifest.SWEEP_ROOT,
                            "2026-08-24-effort-sweep", "low", "arm-A",
                            "run-001")
        os.makedirs(slot)
        with open(os.path.join(slot, "CALL.json"), "w") as handle:
            json.dump({"citable": False}, handle)
        self.assertEqual(make_manifest.prior_authoring_problems(self.root), [])

    def test_no_registered_authoring_path_lies_under_the_sweep_root(self):
        """Said as a property of the gate's own path list, so a future change to
        `authoring_state_paths()` that swept the sweep root in would fail HERE
        and not silently at a freeze."""
        directories, files = make_manifest.authoring_state_paths()
        for relative in tuple(directories) + tuple(files):
            self.assertFalse(
                relative == make_manifest.SWEEP_ROOT
                or relative.startswith(make_manifest.SWEEP_ROOT + "/"),
                relative)

    def test_an_arms_authoring_tree_still_refuses_the_freeze(self):
        """The other direction. R10-1 is not weakened by the sweep's permission:
        the state the round-10 reviewer constructed still refuses."""
        os.makedirs(os.path.join(self.root, "arms", "A", "authoring", "run-001"))
        problems = make_manifest.prior_authoring_problems(self.root)
        self.assertTrue(problems)
        self.assertIn("arms/A/authoring", problems[0])

    def test_a_sweep_tree_and_an_arms_tree_together_refuse_for_the_arms_tree(self):
        """The one that matters for an operator who ran the sweep and then, by
        mistake, a batch: the refusal must name the `arms/` tree and not be
        withheld because a permitted tree is also present."""
        os.makedirs(os.path.join(self.root, make_manifest.SWEEP_ROOT,
                                 "2026-08-24-effort-sweep", "low", "arm-A",
                                 "run-001"))
        os.makedirs(os.path.join(self.root, "arms", "B", "authoring"))
        problems = make_manifest.prior_authoring_problems(self.root)
        self.assertEqual(len(problems), 1)
        self.assertIn("arms/B/authoring", problems[0])

    def test_the_manifest_covers_no_byte_under_the_sweep_root(self):
        """ADR 0004's exact set reaches no byte under `sweeps/`, which is what
        makes `require_lawful_destination()` permit it — the same construction
        that permits `arms/`, `controls/` and `results/`."""
        relative = make_manifest.SWEEP_ROOT + "/2026-08-24-effort-sweep/x.json"
        self.assertFalse(batch.covered_by_manifest(relative))
        self.assertFalse(batch.covered_by_manifest(make_manifest.SWEEP_ROOT))
        self.assertNotIn(make_manifest.SWEEP_ROOT,
                         make_manifest.manifest_entries())
        batch.require_lawful_destination(
            os.path.join(batch.SWEEP_ROOT, "2026-08-24-effort-sweep"),
            "the sweep root")

    def test_the_sweep_root_is_permitted_and_is_not_required(self):
        """Unlike `calibration/`, whose absence REFUSES the freeze because §2a
        registers the pilot as a precondition. Nothing registers the sweep's
        tree as one, and a gate no section states would be the harness
        legislating."""
        os.makedirs(os.path.join(self.root, "calibration", "pilot-001"))
        self.assertEqual(make_manifest.calibration_problems(self.root), [])
        self.assertFalse(
            os.path.isdir(os.path.join(self.root, make_manifest.SWEEP_ROOT)))
        self.assertEqual(make_manifest.prior_authoring_problems(self.root), [])


# --- PIN_LABEL and the setting, threaded ---------------------------------------

class SweepThreading(StandInStudy):
    """`PIN_LABEL` and `SWEEP_EFFORT` reach the wrapper from the driver and from
    nowhere else, and the registered SET is enforced at both ends."""

    def test_the_driver_refuses_a_setting_outside_the_registered_three(self):
        with self.assertRaises(batch.BatchError) as caught:
            batch.invoke(os.path.join(self.root, "x", "run-001"), self.scratch,
                         self.pins_path, self.cli, "probe", batch.PROBE_ARM,
                         self.probe_prompt, pin_label=batch.SWEEP_LABEL,
                         sweep_effort="ultra")
        self.assertIn("is not one of the registered sweep settings",
                      str(caught.exception))
        self.assertIn("DEVIATIONS.md", str(caught.exception))

    def test_the_driver_refuses_a_setting_under_the_primary_label(self):
        """One label wide, at the driver as well as at the wrapper. A primary
        call runs the registry's `codex.reasoningEffort` or it does not run."""
        with self.assertRaises(batch.BatchError) as caught:
            batch.invoke(os.path.join(self.root, "x", "run-001"), self.scratch,
                         self.pins_path, self.cli, "probe", batch.PROBE_ARM,
                         self.probe_prompt, pin_label="PRIMARY",
                         sweep_effort="low")
        self.assertIn("travels under SWEEP alone", str(caught.exception))

    def test_the_environment_member_is_set_unconditionally(self):
        """Like `PIN_LABEL`, and for its reason: a sweep an operator's shell
        could configure is the sweep run outside the harness (§2a.1) wearing the
        harness's own name. The member is overwritten on EVERY call, including
        primary ones, so a stray export cannot survive into a wrapper."""
        seen = {}

        def spy(argv, env=None, **kwargs):
            seen.update(env or {})
            raise SystemExit("stopped before the call")

        with unittest.mock.patch("subprocess.run", spy):
            os.environ[batch.SWEEP_EFFORT_ENV] = "high"
            try:
                with self.assertRaises(SystemExit):
                    batch.invoke(os.path.join(self.root, "y", "run-001"),
                                 self.scratch, self.pins_path, self.cli,
                                 "probe", batch.PROBE_ARM, self.probe_prompt)
            finally:
                os.environ.pop(batch.SWEEP_EFFORT_ENV, None)
        self.assertEqual(seen["PIN_LABEL"], "PRIMARY")
        self.assertEqual(seen[batch.SWEEP_EFFORT_ENV], "")


@unittest.skipUnless(RUNNING_REGISTERED and HAVE_TOOLS,
                     "the wrapper refuses an interpreter harness/PINS.json does "
                     "not register, and needs bash, git and timeout(1)")
class SweepThreadingThroughTheWrapper(StandInStudy):
    """The same width, through the REAL bash, against the committed wrapper."""

    PLAN = [{"completion": "ready"}] * 6

    def call(self, name, setting, pin_label=batch.SWEEP_LABEL, registry=None):
        slot = os.path.join(self.root, name, "capture-001")
        return batch.invoke(slot, self.scratch, registry or self.pins_path,
                            self.cli, "probe", batch.PROBE_ARM,
                            self.probe_prompt, pin_label=pin_label,
                            sweep_effort=setting), slot

    def call_json(self, slot):
        with open(os.path.join(slot, "CALL.json")) as handle:
            return json.load(handle)

    def test_the_threaded_setting_reaches_the_cli_as_the_resolved_spelling(self):
        """The empirical resolution, end to end: the pinned CLI has no
        reasoning-effort flag, so the argv pair is `-c model_reasoning_effort=<tier>`
        and NOT `-c <tier>`, which this build would read as a malformed
        override. Positionally, because `-c` also carries `mcp_servers={}`."""
        pins = json.loads(json.dumps(self.pins))
        pins["codex"]["reasoningEffort"] = None
        registry_path = self.alternate_registry("sweep-setting.json", **pins)
        (status, code, stderr), slot = self.call("setting", "medium",
                                                 registry=registry_path)
        self.assertEqual((status, code), (0, None), stderr)
        record = self.call_json(slot)
        self.assertEqual(record["reasoningEffort"], "medium")
        self.assertEqual(record["reasoningEffortFlag"], "-c")
        self.assertEqual(record["reasoningEffortConfigKey"],
                         "model_reasoning_effort")
        self.assertEqual(record["reasoningEffortArg"],
                         "model_reasoning_effort=medium")
        self.assertEqual(record["reasoningEffortSource"], "sweep-setting")
        self.assertEqual(record["pinLabel"], "SWEEP")
        self.assertIs(record["citable"], False)
        self.assertEqual(record["argv"][3:7],
                         ["-m", "s020-stand-in-model", "-c",
                          "model_reasoning_effort=medium"])
        self.assertEqual(record["argv"][7], "--sandbox")

    def test_the_wrapper_refuses_a_setting_outside_the_registered_set(self):
        """Both ends, because either alone is a hole. The driver's refusal is
        reachable only through the driver; a wrapper that would run an
        unregistered tier is a wrapper the cap clause cannot bind."""
        environment = dict(os.environ)
        environment.update({"PYTHON_BIN": sys.executable,
                            "PROMPT_KIND": "probe", "ISOLATION": "isolated",
                            "GOLDEN_SHA256": "", "PIN_LABEL": "SWEEP",
                            "SWEEP_EFFORT": "ultra",
                            "PYTHONDONTWRITEBYTECODE": "1"})
        finished = subprocess.run(
            ["bash", batch.SCRIPT, self.scratch,
             os.path.join(self.root, "ultra", "capture-001"), self.pins_path,
             batch.PROBE_ARM, self.probe_prompt, self.cli],
            env=environment, capture_output=True, text=True)
        self.assertEqual(finished.returncode, 1)
        self.assertIn("registered sweep.settings", finished.stderr)

    def test_the_wrapper_refuses_a_setting_under_the_primary_label(self):
        environment = dict(os.environ)
        environment.update({"PYTHON_BIN": sys.executable,
                            "PROMPT_KIND": "probe", "ISOLATION": "isolated",
                            "GOLDEN_SHA256": "", "PIN_LABEL": "PRIMARY",
                            "SWEEP_EFFORT": "low",
                            "PYTHONDONTWRITEBYTECODE": "1"})
        finished = subprocess.run(
            ["bash", batch.SCRIPT, self.scratch,
             os.path.join(self.root, "primary", "capture-001"), self.pins_path,
             batch.PROBE_ARM, self.probe_prompt, self.cli],
            env=environment, capture_output=True, text=True)
        self.assertEqual(finished.returncode, 1)
        self.assertIn("under PIN_LABEL=PRIMARY", finished.stderr)

    def test_a_sweep_call_with_no_setting_still_records_the_default_state(self):
        """The state 019's registration already had: the exemption without a
        threaded setting is a call at the CLI's own default, and the slot says
        so rather than looking like a registered one."""
        pins = json.loads(json.dumps(self.pins))
        pins["codex"]["reasoningEffort"] = None
        registry_path = self.alternate_registry("sweep-default.json", **pins)
        (status, code, stderr), slot = self.call("default", None,
                                                 registry=registry_path)
        self.assertEqual((status, code), (0, None), stderr)
        record = self.call_json(slot)
        self.assertIsNone(record["reasoningEffort"])
        self.assertIsNone(record["reasoningEffortArg"])
        self.assertEqual(record["reasoningEffortSource"], "sweep-default")
        self.assertIs(record["citable"], False)


# --- the sweep, end to end ------------------------------------------------------

@unittest.skipUnless(RUNNING_REGISTERED and HAVE_TOOLS,
                     "the wrapper refuses an interpreter harness/PINS.json does "
                     "not register, and needs bash, git and timeout(1)")
class TheSweepEndToEnd(StandInStudy):
    """`batch.py sweep` against the stand-in CLI: real driver, real bash, real
    wrapper bytes, real slots, real ledger."""

    PLAN = [{"completion": "an answer"}] * 30
    LABEL = "2026-08-24-effort-sweep"

    def setUp(self):
        super().setUp()
        self.sweep_root = os.path.join(self.study, "sweeps")
        self.patch("SWEEP_ROOT", self.sweep_root)
        pins = json.loads(json.dumps(self.pins))
        # The sweep is a PRE-FREEZE mode and its own preflight reads the
        # design-time pins alone, so the fixture's filled freeze set is beside
        # the point here; what it must carry is the null effort the exemption is
        # about, and a registry whose `sweep` block is the committed one.
        pins["codex"]["reasoningEffort"] = None
        self.write_pins(pins)

    def sweep(self, *extra, settings="low"):
        return batch.main(["batch.py", "sweep", "--scratch-parent", self.scratch,
                           "--pins", self.pins_path, "--cli-override", self.cli,
                           "--label", self.LABEL, "--settings", settings]
                          + list(extra))

    def ledger(self):
        with open(os.path.join(self.sweep_root, self.LABEL,
                               batch.SWEEP_LEDGER_NAME)) as handle:
            return json.load(handle)

    def table(self):
        with open(os.path.join(self.sweep_root, self.LABEL,
                               batch.SWEEP_TABLE_NAME)) as handle:
            return handle.read()

    def test_one_setting_runs_nine_calls_into_the_registered_tree(self):
        self.assertEqual(self.sweep(), 0)
        body = self.ledger()
        self.assertEqual(len(body["settings"]), 1)
        calls = body["settings"][0]["calls"]
        self.assertEqual(len(calls), len(batch.ARMS) * batch.SWEEP_PER_ARM)
        self.assertEqual([call["arm"] for call in calls],
                         ["A", "B", "C"] * batch.SWEEP_PER_ARM)
        self.assertEqual(body["settings"][0]["outcome"], "swept")
        for call in calls:
            self.assertEqual(call["code"], None, call)
            self.assertIs(call["citable"], False)
            self.assertTrue(call["slot"].startswith("sweeps/" + self.LABEL))
            self.assertTrue(os.path.isfile(
                os.path.join(self.study, call["slot"], "CALL.json")))

    def test_every_retained_slot_is_stamped_uncitable_at_the_swept_setting(self):
        self.assertEqual(self.sweep(), 0)
        for call in self.ledger()["settings"][0]["calls"]:
            with open(os.path.join(self.study, call["slot"],
                                   "CALL.json")) as handle:
                record = json.load(handle)
            self.assertIs(record["citable"], False)
            self.assertEqual(record["pinLabel"], "SWEEP")
            self.assertEqual(record["reasoningEffort"], "low")
            self.assertEqual(record["reasoningEffortArg"],
                             "model_reasoning_effort=low")

    def test_the_sweep_leaves_nothing_in_the_arms_root(self):
        """The point of the third root: after 27 calls the freeze gate still
        sees no authoring state."""
        self.assertEqual(self.sweep(), 0)
        for arm in batch.ARMS:
            self.assertFalse(os.path.exists(
                os.path.join(self.arms_root, arm, "authoring")))
        self.assertFalse(os.path.exists(
            os.path.join(self.arms_root, batch.LEDGER_NAME)))
        self.assertEqual(make_manifest.prior_authoring_problems(self.study), [])

    def test_the_ledger_and_the_table_are_both_published_and_both_say_uncitable(self):
        self.assertEqual(self.sweep(), 0)
        body = self.ledger()
        self.assertIs(body["citable"], False)
        self.assertEqual(body["registeredSettings"], list(batch.SWEEP_SETTINGS))
        self.assertEqual(body["callCap"], batch.SWEEP_CALL_CAP)
        table = self.table()
        self.assertIn("`citable: false`", table)
        self.assertIn("Outside every population", table)
        self.assertIn("| arm | run | duration s | completion bytes | "
                      "reasoning tokens | exit | code | timed out |", table)
        for arm in batch.ARMS:
            self.assertIn("| %s | 1 |" % arm, table)

    def test_the_table_publishes_a_duration_and_a_completion_size_per_call(self):
        self.assertEqual(self.sweep(), 0)
        for call in self.ledger()["settings"][0]["calls"]:
            self.assertGreater(call["durationSeconds"], 0)
            self.assertEqual(call["completionBytes"], len("an answer"))

    def test_step_zero_records_the_witness_branch_the_first_call_produced(self):
        """Driven on 019's own `turn_context` shape — no effort member in any
        spelling (the `no_effort_witness` plan knob; R1-12 made the DEFAULT
        stand-in witness like the real CLI, so the self-report branch is now
        opted into rather than ambient) — so the branch that fires here is the
        one M-24 predicts for that apparatus."""
        write_plan(self.cli_dir,
                   [{"completion": "an answer", "no_effort_witness": True}] * 30)
        self.assertEqual(self.sweep(), 0)
        witness = self.ledger()["witnessResolution"]
        self.assertEqual(witness["branch"], batch.WITNESS_BRANCH_SELF_REPORT)
        self.assertTrue(witness["resolvedFrom"].endswith("arm-A/run-001"))
        self.assertIn("SELF-REPORT", witness["obligation"])
        self.assertIn("Branch: `%s`" % batch.WITNESS_BRANCH_SELF_REPORT,
                      self.table())

    def test_the_publication_happens_after_every_call_and_not_at_the_end(self):
        """A sweep killed part way through has published what it spent. Driven
        by making the fifth call raise and requiring the first four on disk."""
        real = batch.invoke
        state = {"calls": 0}

        def counted(*args, **kwargs):
            state["calls"] += 1
            if state["calls"] > 4:
                raise batch.BatchError("stopped after four calls")
            return real(*args, **kwargs)

        self.patch("invoke", counted)
        self.assertEqual(self.sweep(), 1)
        body = self.ledger()
        self.assertEqual(len(body["settings"][0]["calls"]), 4)

    def test_a_dry_run_plans_the_calls_and_spends_none(self):
        self.assertEqual(self.sweep("--dry-run", settings="low,medium,high"), 0)
        self.assertFalse(os.path.exists(os.path.join(self.sweep_root,
                                                     self.LABEL)))

    def test_a_second_sweep_under_one_label_refuses(self):
        self.assertEqual(self.sweep(), 0)
        self.assertEqual(self.sweep(), 1)

    def test_an_unregistered_setting_refuses_before_a_call(self):
        self.assertEqual(self.sweep(settings="ultra"), 1)
        self.assertFalse(os.path.exists(os.path.join(self.sweep_root,
                                                     self.LABEL)))


@unittest.skipUnless(RUNNING_REGISTERED and HAVE_TOOLS,
                     "the wrapper refuses an interpreter harness/PINS.json does "
                     "not register, and needs bash, git and timeout(1)")
class TheAbortRuleThroughTheStandIn(TheSweepEndToEnd):
    """Both clauses, driven by the real driver making real wrapper calls.

    The ceiling and the budget are the registered numbers; a test cannot spend
    2700 s or 72 h to reach them, so the CONSTANTS are moved and the RULE is the
    committed one. Moving the threshold is not the same as stubbing the rule:
    every line of `sweep_abort_verdict()`, `run_sweep()`'s break and the
    publication of the aborting call are the ones production runs."""

    PLAN = [{"completion": "an answer", "sleep": 2}] + \
           [{"completion": "an answer"}] * 30

    def test_clause_one_aborts_the_setting_after_the_first_arm_a_call(self):
        """The first arm-A call runs past the ceiling; the setting is aborted
        AFTER that call, and the call is published with it."""
        self.patch("CALL_TIMEOUT_SECONDS", 1)
        self.assertEqual(self.sweep(), 0)
        setting = self.ledger()["settings"][0]
        self.assertEqual(setting["outcome"], "aborted")
        self.assertEqual(setting["clause"], "first-arm-A-call-over-ceiling")
        self.assertEqual(setting["callsMade"], 1)
        self.assertEqual(setting["calls"][0]["arm"], "A")
        self.assertIsNotNone(setting["abortingCall"])
        self.assertEqual(setting["abortingCall"]["arm"], "A")
        self.assertIn("aborted", self.table())
        self.assertIn("| A | 1 |", self.table())

    def test_an_aborted_setting_does_not_stop_the_next_one(self):
        """§2.1 aborts a SETTING. The sweep goes on to the next, and the
        published table carries both."""
        self.patch("CALL_TIMEOUT_SECONDS", 1)
        self.assertEqual(self.sweep(settings="low,medium"), 0)
        outcomes = {row["setting"]: row["outcome"]
                    for row in self.ledger()["settings"]}
        self.assertEqual(outcomes["low"], "aborted")
        self.assertIn("medium", outcomes)

    def test_clause_two_stops_a_setting_after_one_call_per_arm(self):
        """"Is not swept further" is only a rule if it can still stop
        something: under the interleaved order the projection is computable
        after three calls, so an out-of-budget setting costs three and not
        nine."""
        # BOTH places, because the sweep's own preflight refuses a registry that
        # disagrees with the driver's constants — which is itself the guarantee
        # working, and is why this case has to move the number in two places
        # rather than one.
        self.patch("SWEEP_BUDGET_HOURS", 0)
        pins = json.loads(json.dumps(self.pins))
        pins["sweep"]["budgetHours"] = 0
        self.write_pins(pins)
        self.assertEqual(self.sweep(), 0)
        setting = self.ledger()["settings"][0]
        self.assertEqual(setting["outcome"], "out-of-budget")
        self.assertEqual(setting["clause"], "projected-batch-over-budget")
        self.assertEqual(setting["callsMade"], len(batch.ARMS))
        self.assertEqual(sorted(setting["perArmMeanSeconds"]),
                         sorted(batch.ARMS))
        self.assertGreater(setting["projectedBatchHours"], 0)
        self.assertIn("out-of-budget", self.table())


# --- the sweep's own preflight -------------------------------------------------

class TheSweepPreflight(StandInStudy):
    """What the sweep checks before it spends, and what it deliberately does
    not — the two differ because the sweep runs at a different point in the
    ceremony and pretending otherwise would make it un-runnable."""

    def setUp(self):
        super().setUp()
        self.sweep_root = os.path.join(self.study, "sweeps")
        self.patch("SWEEP_ROOT", self.sweep_root)
        self.label = "2026-08-24-effort-sweep"

    def preflight(self, pins_path=None):
        slots = [batch.sweep_slot_path(self.label, "low", "A", 1)]
        return batch.sweep_preflight(self.label, slots, self.scratch,
                                     pins_path or self.pins_path, self.cli)

    def refusal(self, pins) -> str:
        path = self.alternate_registry("sweep-preflight.json", **pins)
        with self.assertRaises(batch.BatchError) as caught:
            self.preflight(path)
        return str(caught.exception)

    def test_the_committed_sweep_block_passes(self):
        self.assertIsInstance(self.preflight(), dict)

    def test_a_null_model_refuses_because_the_exemption_is_one_value_wide(self):
        """M-25's own sentence, enforced: `codex.reasoningEffort` alone is
        exempt, `codex.model` is never exempt, and 019's pilot's defining defect
        was a call whose model nothing recorded."""
        pins = json.loads(json.dumps(self.pins))
        pins["codex"]["model"] = None
        message = self.refusal(pins)
        self.assertIn("codex.model is never exempt", message)
        self.assertIn("model", message)

    def test_a_null_effort_does_not_refuse_because_that_is_the_exemption(self):
        """The other half of the same sentence. A gate that refused the sweep's
        own input would forbid the procedure that produces it."""
        pins = json.loads(json.dumps(self.pins))
        pins["codex"]["reasoningEffort"] = None
        path = self.alternate_registry("null-effort.json", **pins)
        self.assertIsInstance(self.preflight(path), dict)

    def test_a_null_batch_n_does_not_refuse_because_it_is_the_output(self):
        """`check_registry()` refuses a null `batch.n`, and the sweep must not:
        requiring it would be requiring the answer before the question."""
        pins = json.loads(json.dumps(self.pins))
        pins["batch"]["n"] = None
        pins["batch"]["slots"] = None
        pins["batch"]["order"] = None
        path = self.alternate_registry("null-n.json", **pins)
        self.assertIsInstance(self.preflight(path), dict)

    def test_a_registry_disagreeing_about_the_set_refuses(self):
        """One registration in two places is only safe if a drift refuses."""
        for member, value in (("settings", ["low", "medium", "xhigh"]),
                              ("perArm", 5),
                              ("callCap", 99),
                              ("root", "arms"),
                              ("budgetHours", 1),
                              ("budgetProjectionN", 1)):
            pins = json.loads(json.dumps(self.pins))
            pins["sweep"][member] = value
            message = self.refusal(pins)
            self.assertIn("sweep.%s" % member, message)
            self.assertIn("not run under a disagreement", message)

    def test_a_registry_that_does_not_say_uncitable_refuses(self):
        pins = json.loads(json.dumps(self.pins))
        pins["sweep"]["citable"] = True
        self.assertIn("citable: false", self.refusal(pins))

    def test_a_plan_over_the_cap_refuses(self):
        slots = [batch.sweep_slot_path(self.label, "low", "A", index)
                 for index in range(1, batch.SWEEP_CALL_CAP + 2)]
        with self.assertRaises(batch.BatchError) as caught:
            batch.sweep_preflight(self.label, slots, self.scratch,
                                  self.pins_path, self.cli)
        self.assertIn("caps the sweep at %d" % batch.SWEEP_CALL_CAP,
                      str(caught.exception))
        self.assertIn("DEVIATIONS.md", str(caught.exception))

    def test_an_attempt_root_refuses_a_sweep_too(self):
        """A sweep is a call, and no call is made after a rate has been
        computed."""
        os.makedirs(batch.ATTEMPT_ROOT)
        with self.assertRaises(batch.BatchError) as caught:
            self.preflight()
        self.assertIn("no call is made after a rate", str(caught.exception))

    def test_an_existing_label_refuses_rather_than_interleaving_two_sweeps(self):
        os.makedirs(os.path.join(self.sweep_root, self.label))
        with self.assertRaises(batch.BatchError) as caught:
            self.preflight()
        self.assertIn("one procedure run once", str(caught.exception))

    def test_a_drifted_arm_prompt_refuses_before_any_call(self):
        path = os.path.join(self.study, "arms", "A", "PROMPT.txt")
        with open(path, "a") as handle:
            handle.write("drift\n")
        with self.assertRaises(batch.BatchError) as caught:
            self.preflight()
        self.assertIn("not the pinned", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
