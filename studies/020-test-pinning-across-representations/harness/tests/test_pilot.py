#!/usr/bin/env python3
"""The pre-freeze calibration pilot — PREREGISTRATION.md §2a, round-1 finding
R1-17.

R1-17's words: "The sealed `calibration/derive_floor.py` and the driver's
calibration mode are also still absent; the existing freeze check merely looks
for a pilot-labelled subtree rather than validating a registered pilot
output." This file drives the landed instrument end to end — the driver mode
(`batch.py pilot`, `PIN_LABEL=PILOT`), the sealed deriver, the rates
publisher, and the freeze gate's record validation — and it is careful about
the same four things `test_sweep.py` is, plus one of its own:

* **The registered numbers are bound to the registration's BYTES** — §2a.2's
  12/arm and §2a.1's own Clopper-Pearson table row, currency-style, so the
  sealed rule reproducing 0.779 / 0.661 / 0.562 is an assertion about the
  PREREGISTRATION and not about whatever the code computes.
* **The ordering gates are driven as refusals**, because each is a registered
  sentence: no pilot call under an undeclared minimum (§2a.4(2)), no second
  pilot (§2a.6), no exemption for the pilot's pin state (§2a.2's fourth
  difference).
* **The contract has ONE reading.** `pilot_rates.py` publishes the record the
  sealed deriver's `validate_record()` accepts, and the freeze gate validates
  through the same function — so the producer/consumer drift R1-13 found
  between `score_run()` and `reviewer.execute()` cannot recur here, and this
  file asserts it with the deriver's own refusals, not with a copied schema.
* **The end-to-end cases make real wrapper calls** through the stand-in CLI:
  real bash, real wrapper bytes, real slots, real ledger.
"""
from __future__ import annotations
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import unittest
from unittest import mock

import batch
import integrity
import make_manifest

from test_batch import (HARNESS, REGISTRY, STUDY, StandInStudy)

PREREG = os.path.join(STUDY, "PREREGISTRATION.md")
DERIVE_FLOOR = os.path.join(STUDY, "calibration", "derive_floor.py")


def prereg_text() -> str:
    with open(PREREG, "rb") as handle:
        return handle.read().decode("utf-8")


def registry() -> dict:
    with open(REGISTRY) as handle:
        return json.load(handle)


def floor_module():
    spec = importlib.util.spec_from_file_location("derive_floor_under_test",
                                                  DERIVE_FLOOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pilot_record(label="2026-08-24-pilot", **per_arm_edits) -> dict:
    """A record of the registered shape; edits move one arm's counts.

    ROUND-2 FINDING R2-10 amended that shape: the 12 SCORED calls are the
    apparatus-clean ones, drawn from up to 21 attempts per arm, and the three
    population numbers (`attempted`, `calls`, `apparatusExcluded`) are one
    partition that must reconcile."""
    per_arm = {arm: {"calls": 12, "attempted": 12, "apparatusExcluded": 0,
                     "apparatusCodes": [], "perfect": 8, "identityPass": 10}
               for arm in ("A", "B", "C")}
    for arm, edit in per_arm_edits.items():
        per_arm[arm].update(edit)
    return {"label": label, "citable": False, "perArm": per_arm}


# --- the registered numbers, bound to the registration's own bytes -----------

class TheRegisteredPilot(unittest.TestCase):

    def test_the_per_arm_count_is_the_registrations_own_twelve(self):
        """§2a.2's sentence, the driver's constant and the registry's member
        are one registration in three places."""
        self.assertIn("Pilot N: **12/arm**", prereg_text())
        self.assertEqual(batch.PILOT_RUNS_PER_ARM, 12)
        self.assertEqual(registry()["calibration"]["pilotPerArm"], 12)
        self.assertEqual(batch.PILOT_CALL_CAP, 36)

    def test_the_registered_differences_stay_exactly_four(self):
        # Unwrapped first: the registration is hard-wrapped prose.
        self.assertIn("The registered differences between the pilot and the "
                      "primary batch are exactly four",
                      prereg_text().replace("\n", " "))

    def test_the_landed_spellings_are_amended_into_the_registration(self):
        """R1-17's amendment: §2a.2 names the subcommand, the label and the
        record path, so the mode that landed is the mode that is registered."""
        text = prereg_text()
        self.assertIn("`harness/batch.py pilot`", text)
        self.assertIn("`PIN_LABEL=PILOT`", text)
        self.assertIn("PILOT-RATES.json", text)

    def test_the_deriver_is_a_registered_document(self):
        """§2a.4(1): sealed before the pilot runs — it is in the exact-set
        manifest, so `--freeze` refuses while it is absent."""
        self.assertIn("calibration/derive_floor.py",
                      make_manifest.REGISTERED_DOCUMENTS)
        self.assertTrue(os.path.isfile(DERIVE_FLOOR))

    def test_the_registry_carries_the_wrappers_anchor_root(self):
        self.assertEqual(registry()["calibration"]["root"], "calibration")

    def test_the_pilot_label_is_a_registered_third(self):
        self.assertEqual(batch.PIN_LABELS, ("PRIMARY", "SWEEP", "PILOT"))
        self.assertEqual(batch.PILOT_PIN_LABEL, "PILOT")


# --- the schedule and the slot shape -----------------------------------------

class TheSchedule(unittest.TestCase):

    def test_it_is_thirty_six_calls_arm_interleaved_a_first(self):
        entries = batch.pilot_schedule()
        self.assertEqual(len(entries), 36)
        self.assertEqual([entry["arm"] for entry in entries],
                         ["A", "B", "C"] * 12)
        self.assertEqual(entries[0], {"arm": "A", "runIndex": 1,
                                      "indexWithinPilot": 1})
        self.assertEqual(entries[-1], {"arm": "C", "runIndex": 12,
                                       "indexWithinPilot": 36})

    def test_the_slot_path_is_the_registered_shape(self):
        path = batch.pilot_slot_path("2026-08-24-pilot", "B", 7)
        self.assertTrue(path.endswith(
            os.path.join("calibration", "2026-08-24-pilot", "arm-B",
                         "run-007")), path)

    def test_an_unregistered_arm_refuses(self):
        with self.assertRaises(batch.BatchError):
            batch.pilot_slot_path("2026-08-24-pilot", "D", 1)

    def test_the_label_is_dated_and_suffixed(self):
        self.assertEqual(batch.pilot_label("2026-08-24"), "2026-08-24-pilot")
        self.assertRegex(batch.pilot_label(),
                         r"^\d{4}-\d{2}-\d{2}-pilot$")

    def test_a_label_that_reaches_out_of_the_subtree_refuses(self):
        for label in ("..", "a/b", "/tmp/x", ""):
            with self.assertRaises(batch.BatchError):
                batch.pilot_slot_path(label, "A", 1)


# --- the sealed deriver ------------------------------------------------------

class TheDeriver(unittest.TestCase):
    """`calibration/derive_floor.py`, driven against §2a.1's own table."""

    def setUp(self):
        self.floor = floor_module()

    def test_the_rule_reproduces_the_registrations_own_table_row(self):
        """CURRENCY, and the mutation check for the whole arithmetic: §2a.1's
        table registers the n=12 row as 0.779 / 0.661 / 0.562, and the sealed
        rule must land on those digits from the raw counts. A deriver whose
        alpha, sidedness or exactness drifted reproduces none of them."""
        text = prereg_text()
        self.assertIn("| **12** | **0.779** | **0.661** | 0.562 |", text)
        derived = self.floor.derive(pilot_record(
            A={"perfect": 12}, B={"perfect": 11}, C={"perfect": 10}))
        self.assertEqual(round(derived["perArm"]["A"]["perfectFloor"], 3),
                         0.779)
        self.assertEqual(round(derived["perArm"]["B"]["perfectFloor"], 3),
                         0.661)
        self.assertEqual(round(derived["perArm"]["C"]["perfectFloor"], 3),
                         0.562)

    def test_a_zero_count_floors_at_zero_and_the_floor_is_monotone(self):
        derived = self.floor.derive(pilot_record(A={"perfect": 0}))
        self.assertEqual(derived["perArm"]["A"]["perfectFloor"], 0.0)
        floors = [self.floor.derive(pilot_record(A={"perfect": k}))
                  ["perArm"]["A"]["perfectFloor"] for k in range(13)]
        self.assertEqual(floors, sorted(floors))
        self.assertLess(floors[11], floors[12])

    def test_both_floors_are_emitted_for_every_arm(self):
        derived = self.floor.derive(pilot_record())
        for arm in ("A", "B", "C"):
            cell = derived["perArm"][arm]
            self.assertIn("perfectFloor", cell)
            self.assertIn("identityFloor", cell)
            self.assertLess(cell["perfectFloor"], cell["identityFloor"])

    def test_the_record_contract_refuses_each_departure(self):
        cases = [
            ("citable-true", dict(pilot_record(), citable=True)),
            ("citable-absent", {"perArm": pilot_record()["perArm"]}),
            ("missing-arm", {"citable": False, "perArm": {
                "A": {"calls": 12, "perfect": 1, "identityPass": 1},
                "B": {"calls": 12, "perfect": 1, "identityPass": 1}}}),
            ("extra-arm", {"citable": False, "perArm": dict(
                pilot_record()["perArm"],
                D={"calls": 12, "perfect": 1, "identityPass": 1})}),
            ("wrong-n", pilot_record(A={"calls": 11})),
            ("count-over-n", pilot_record(A={"perfect": 13})),
            ("negative-count", pilot_record(B={"identityPass": -1})),
            ("boolean-count", pilot_record(C={"perfect": True})),
            ("float-count", pilot_record(C={"perfect": 8.0})),
        ]
        for name, record in cases:
            with self.assertRaises(self.floor.FloorError, msg=name):
                self.floor.validate_record(record)

    def test_the_go_no_go_compares_declared_against_derived(self):
        derived = self.floor.derive(pilot_record())  # identityFloor 0.560
        go = self.floor.go_no_go(derived, 0.3, "identityFloor")
        self.assertTrue(go["go"])
        self.assertEqual(go["failingArms"], [])
        no = self.floor.go_no_go(derived, 0.6, "identityFloor")
        self.assertFalse(no["go"])
        self.assertEqual(no["failingArms"], ["A", "B", "C"])
        self.assertIn("ABORT", no["consequence"])
        self.assertIn("does not descope", no["consequence"])

    def test_the_declaration_is_validated_not_defaulted(self):
        """§2a.4(2): an absent declaration is a refusal, never a zero — a
        defaulted minimum would make every pilot a GO."""
        derived = self.floor.derive(pilot_record())
        with self.assertRaises(self.floor.FloorError):
            self.floor.go_no_go(derived, None, "identityFloor")
        with self.assertRaises(self.floor.FloorError):
            self.floor.go_no_go(derived, True, "identityFloor")
        with self.assertRaises(self.floor.FloorError):
            self.floor.go_no_go(derived, 0.3, "meanRate")


# --- the driver's ordering gates ---------------------------------------------

class ThePilotFixture(StandInStudy):
    """The stand-in study with the pilot's own seats added: a patched
    `CALIBRATION_ROOT`, the sealed deriver copied in, and the §2a.4(2)
    declaration filled — each case then removes the one thing it is about."""

    LABEL = "2026-08-24-pilot"

    def setUp(self):
        super().setUp()
        self.calibration_root = os.path.join(self.study, "calibration")
        self.patch("CALIBRATION_ROOT", self.calibration_root)
        os.makedirs(self.calibration_root)
        shutil.copyfile(DERIVE_FLOOR, os.path.join(self.calibration_root,
                                                   "derive_floor.py"))
        pins = json.loads(json.dumps(self.pins))
        pins["calibration"]["minimumViable"] = 0.20
        pins["calibration"]["minimumViableBasis"] = "identityFloor"
        self.write_pins(pins)

    def preflight(self, pins_path=None, label=None):
        label = label or self.LABEL
        slots = [batch.pilot_slot_path(label, entry["arm"], entry["runIndex"])
                 for entry in batch.pilot_schedule()]
        return batch.pilot_preflight(label, slots, self.scratch,
                                     pins_path or self.pins_path, self.cli)


class ThePilotPreflight(ThePilotFixture):

    def test_the_filled_fixture_passes(self):
        self.assertEqual(self.preflight()["calibration"]["pilotPerArm"], 12)

    def test_an_undeclared_minimum_refuses_before_any_call(self):
        """§2a.4(2), enforced: the declaration precedes the pilot. Mutation
        check for the ordering gate itself — drop the preflight's
        `minimumViable` clause and this passes a pilot 019 would have run."""
        pins = json.loads(json.dumps(self.pins))
        pins["calibration"]["minimumViable"] = None
        self.write_pins(pins)
        with self.assertRaisesRegex(batch.BatchError, "minimumViable"):
            self.preflight()

    def test_an_undeclared_basis_refuses_too(self):
        pins = json.loads(json.dumps(self.pins))
        pins["calibration"]["minimumViableBasis"] = None
        self.write_pins(pins)
        with self.assertRaisesRegex(batch.BatchError, "minimumViableBasis"):
            self.preflight()

    def test_an_absent_deriver_refuses(self):
        """§2a.4(1): sealed BEFORE the pilot runs."""
        os.unlink(os.path.join(self.calibration_root, "derive_floor.py"))
        with self.assertRaisesRegex(batch.BatchError, "derive_floor"):
            self.preflight()

    def test_a_filled_label_pin_is_a_pilot_that_has_run(self):
        pins = json.loads(json.dumps(self.pins))
        pins["calibration"]["label"] = "2026-08-20-pilot"
        self.write_pins(pins)
        with self.assertRaisesRegex(batch.BatchError, "DEVIATIONS"):
            self.preflight()

    def test_an_existing_pilot_tree_is_a_pilot_that_has_run(self):
        os.makedirs(os.path.join(self.calibration_root, "2026-08-20-pilot"))
        with self.assertRaisesRegex(batch.BatchError, "one pilot|ONE pilot"):
            self.preflight()

    def test_the_pilot_claims_no_effort_exemption(self):
        """§2a.2's fourth difference is the design-time rule APPLYING: a null
        effort refuses the pilot outright, where the sweep is exempt."""
        pins = json.loads(json.dumps(self.pins))
        pins["codex"]["reasoningEffort"] = None
        self.write_pins(pins)
        with self.assertRaisesRegex(batch.BatchError, "NO exemption"):
            self.preflight()

    def test_a_registry_count_drift_refuses(self):
        pins = json.loads(json.dumps(self.pins))
        pins["calibration"]["pilotPerArm"] = 11
        self.write_pins(pins)
        with self.assertRaisesRegex(batch.BatchError, "pilotPerArm"):
            self.preflight()

    def test_a_computed_rate_ends_all_calling(self):
        os.makedirs(batch.ATTEMPT_ROOT)
        with self.assertRaisesRegex(batch.BatchError, "after a rate"):
            self.preflight()

    def test_the_sixty_fourth_attempt_is_refused_by_arithmetic(self):
        """ROUND-2 FINDING R2-10 moved the cap from CALLS to ATTEMPTS: the 12
        scored calls per arm are drawn from at most 21 attempts, so 63 is the
        registered ceiling and 64 is refused by arithmetic rather than by
        policy."""
        slots = [batch.pilot_slot_path(self.LABEL, "A", index)
                 for index in range(1, 65)]
        with self.assertRaisesRegex(batch.BatchError, "64 attempts"):
            batch.pilot_preflight(self.LABEL, slots, self.scratch,
                                  self.pins_path, self.cli)

    def test_a_label_that_is_not_a_calendar_date_refuses(self):
        """ROUND-2 FINDING R2-9: `--label` was checked for SHAPE and traversal
        and never for being a date, so `0000-99-99-pilot` passed every guard —
        and the wrapper's own anchor gate only checks the digit shape, so both
        halves of the agreement would have agreed on a nonsense date.

        MUTATION: delete `require_pilot_label()`'s `date.fromisoformat` block —
        the first case passes and this test fails."""
        for label in ("0000-99-99-pilot", "2026-02-30-pilot", "20260824-pilot",
                      "2026-8-4-pilot", "not-a-date-pilot", "2026-08-24"):
            with self.assertRaises(batch.BatchError, msg=label):
                batch.require_pilot_label(label)
        # …and a real past date in canonical spelling is accepted.
        self.assertEqual(batch.require_pilot_label("2026-08-24-pilot"),
                         "2026-08-24-pilot")

    def test_a_future_dated_label_refuses(self):
        import datetime as _dt
        ahead = (_dt.datetime.now(_dt.timezone.utc).date()
                 + _dt.timedelta(days=1)).isoformat()
        with self.assertRaisesRegex(batch.BatchError, "dated after today"):
            batch.require_pilot_label("%s-pilot" % ahead)

    def test_a_non_finite_declaration_cannot_spend_a_call(self):
        """ROUND-2 FINDING R2-9's lethal case, driven end to end. JSON has no
        `NaN` literal and Python's decoder accepts one anyway; every
        `floor < NaN` comparison is False, so a total collapse in all three
        arms would have returned GO — the gate reporting a pass exactly when
        the study died.

        MUTATION 1: remove `parse_constant` from the registry readers — the
        registry loads and the refusal moves to `validate_declaration()`,
        which this test also accepts, so BOTH halves are asserted separately
        below. MUTATION 2: delete `validate_declaration()`'s `isfinite` branch
        — the second assertion fails."""
        pins = json.loads(json.dumps(self.pins))
        self.write_pins(pins)
        with open(self.pins_path, encoding="utf-8") as handle:
            raw = handle.read()
        raw = raw.replace('"minimumViable": 0.2', '"minimumViable": NaN')
        with open(self.pins_path, "w", encoding="utf-8") as handle:
            handle.write(raw)
        # The registry READER refuses it first (integrity's one seat), and
        # `main()` routes both refusal types to the same message.
        with self.assertRaises((batch.BatchError, integrity.IntegrityError)):
            self.preflight()
        # …and the sealed deriver refuses it directly, so the fence holds even
        # for a caller that never went through a registry reader.
        floor = floor_module()
        with self.assertRaisesRegex(floor.FloorError, "non-finite"):
            floor.validate_declaration(float("nan"), "identityFloor")
        for bad in (0.0, -0.1, 1.5, True, "0.2", None):
            with self.assertRaises(floor.FloorError, msg=repr(bad)):
                floor.validate_declaration(bad, "identityFloor")
        with self.assertRaises(floor.FloorError):
            floor.validate_declaration(0.20, "banana")

    def test_a_declaration_that_is_not_the_registered_one_refuses(self):
        """R2-9: the ordering gate proved only that SOMETHING was declared.
        §2a.4(2) registers 0.20 on the identity floor, and the driver refuses
        a registry that says otherwise.

        MUTATION: drop the two declaration rows from the registry-agreement
        loop — a pilot spends 63 calls under an unregistered threshold and
        this test fails."""
        # From a pristine copy each time: `write_pins()` also updates
        # `self.pins`, so a second edit layered on the first would name the
        # first member's refusal and the loop would prove one case twice.
        pristine = json.loads(json.dumps(self.pins))
        for member, value in (("minimumViable", 0.35),
                              ("minimumViableBasis", "perfectFloor")):
            pins = json.loads(json.dumps(pristine))
            pins["calibration"][member] = value
            self.write_pins(pins)
            with self.assertRaisesRegex(batch.BatchError, member):
                self.preflight()


class ThePilotEndToEnd(ThePilotFixture):
    """`batch.py pilot` against the stand-in CLI: real driver, real bash, real
    wrapper bytes, real slots, real ledger."""

    PLAN = [{"completion": "an answer"}] * 40

    def pilot(self, *extra):
        return batch.main(["batch.py", "pilot", "--scratch-parent",
                           self.scratch, "--pins", self.pins_path,
                           "--cli-override", self.cli, "--label", self.LABEL]
                          + list(extra))

    def ledger(self):
        with open(os.path.join(self.calibration_root, self.LABEL,
                               batch.PILOT_LEDGER_NAME)) as handle:
            return json.load(handle)

    def test_a_dry_run_plans_thirty_six_calls_and_makes_none(self):
        self.assertEqual(self.pilot("--dry-run"), 0)
        self.assertFalse(os.path.isdir(os.path.join(self.calibration_root,
                                                    self.LABEL)))

    def test_the_pilot_runs_thirty_six_calls_into_the_registered_tree(self):
        self.assertEqual(self.pilot(), 0)
        body = self.ledger()
        self.assertEqual(body["callsMade"], 36)
        self.assertEqual(body["callsRegistered"], 36)
        self.assertIs(body["citable"], False)
        self.assertEqual([call["arm"] for call in body["calls"]],
                         ["A", "B", "C"] * 12)
        self.assertEqual(body["record"]["mode"], "pilot")
        self.assertEqual(body["record"]["runsPerArm"], 12)
        for call in body["calls"]:
            self.assertEqual(call["code"], None, call)
            self.assertIs(call["citable"], False)
            self.assertTrue(call["slot"].startswith(
                "calibration/" + self.LABEL))
        with open(os.path.join(self.study, body["calls"][0]["slot"],
                               "CALL.json")) as handle:
            record = json.load(handle)
        self.assertEqual(record["pinLabel"], "PILOT")
        self.assertIs(record["citable"], False)
        # The registry's OWN effort value, not a literal: the pilot runs the
        # pinned condition or it does not run.
        self.assertEqual(record["reasoningEffort"],
                         self.pins["codex"]["reasoningEffort"])
        table = open(os.path.join(self.calibration_root, self.LABEL,
                                  batch.PILOT_TABLE_NAME)).read()
        self.assertIn("citable: false", table)
        self.assertIn("| 36 | C | 012 |", table)

    def test_the_pilot_leaves_nothing_in_the_arms_root(self):
        """The third root's point, §2a.2's first difference: after 36 calls
        the freeze gate still sees no authoring state."""
        self.assertEqual(self.pilot(), 0)
        for arm in batch.ARMS:
            self.assertFalse(os.path.exists(
                os.path.join(self.arms_root, arm, "authoring")))
        self.assertEqual(make_manifest.prior_authoring_problems(self.study),
                         [])

    def test_a_second_pilot_is_refused(self):
        self.assertEqual(self.pilot(), 0)
        self.assertEqual(self.pilot(), 1)

    def test_a_threaded_setting_is_refused_under_the_pilot_label(self):
        with self.assertRaisesRegex(batch.BatchError, "sweep setting"):
            batch.invoke("slot", self.scratch, self.pins_path, self.cli,
                         "registered", "A",
                         os.path.join(self.study, "arms", "A", "PROMPT.txt"),
                         pin_label="PILOT", sweep_effort="low")

    def test_the_wrapper_refuses_a_pilot_slot_outside_the_anchor(self):
        """The wrapper's own half of the agreement: a PILOT call aimed at the
        arms tree is refused by the anchor rule, with the registered shape in
        the message."""
        slot = os.path.join(self.study, "arms", "A", "authoring", "run-001")
        environment = dict(
            os.environ, PYTHON_BIN=sys.executable,
            PROMPT_KIND="registered", ISOLATION="isolated", GOLDEN_SHA256="",
            PIN_LABEL="PILOT", SWEEP_EFFORT="",
            PYTHONDONTWRITEBYTECODE="1")
        completed = subprocess.run(
            ["bash", batch.SCRIPT, self.scratch, slot, self.pins_path, "A",
             os.path.join(self.study, "arms", "A", "PROMPT.txt"), self.cli],
            env=environment, capture_output=True, text=True)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("calibration/<UTC date>-pilot/arm-A", completed.stderr)

    def test_an_unrecognised_label_names_all_three(self):
        with self.assertRaisesRegex(batch.BatchError,
                                    "PRIMARY, SWEEP, PILOT"):
            batch.invoke("slot", self.scratch, self.pins_path, self.cli,
                         "registered", "A",
                         os.path.join(self.study, "arms", "A", "PROMPT.txt"),
                         pin_label="FLIGHT")


# --- the rates record and its one contract -----------------------------------

class TheRatesRecord(unittest.TestCase):
    """`pilot_rates.py` builds the record `derive_floor.py` validates — driven
    with a stubbed admission so no binary runs, like `test_sweep_rates.py`."""

    def setUp(self):
        import pilot_rates
        import sweep_rates
        self.pilot_rates = pilot_rates
        self.sweep_rates = sweep_rates
        self.root = os.path.realpath(
            os.path.join(os.environ.get("TMPDIR", "/tmp"),
                         "pilot-rates-%d" % os.getpid()))
        shutil.rmtree(self.root, ignore_errors=True)
        os.makedirs(self.root)
        self.addCleanup(shutil.rmtree, self.root, True)
        self.label = "2026-08-24-pilot"
        self.calibration = os.path.join(self.root, "calibration")
        patches = [
            mock.patch.object(pilot_rates, "STUDY", self.root),
            mock.patch.object(pilot_rates, "CALIBRATION_ROOT",
                              self.calibration),
            mock.patch.object(sweep_rates, "STUDY", self.root),
        ]
        for patched in patches:
            patched.start()
            self.addCleanup(patched.stop)
        self.pins = {"calibration": {"minimumViable": 0.20,
                                     "minimumViableBasis": "identityFloor"}}
        self.build_pilot_tree()

    def build_pilot_tree(self, calls=36, per_arm=None):
        """`per_arm` gives an arm more ATTEMPTS than the registered 12 — the
        state R2-10's amended §2a.2 makes lawful, where the scored 12 are drawn
        from up to 21 attempts and the excluded ones stay on disk."""
        here = os.path.join(self.calibration, self.label)
        wanted = dict(per_arm or {"A": 12, "B": 12, "C": 12})
        rows = []
        index = 0
        made = {arm: 0 for arm in ("A", "B", "C")}
        for run_index in range(1, max(wanted.values()) + 1):
            for arm in ("A", "B", "C"):
                if made[arm] >= wanted[arm] or index >= calls:
                    continue
                index += 1
                made[arm] += 1
                slot = os.path.join(here, "arm-%s" % arm,
                                    "run-%03d" % run_index)
                os.makedirs(slot)
                with open(os.path.join(slot, "completion.txt"), "w") as handle:
                    handle.write("POLICY:\n```rego\nx\n```\nTESTS:\n"
                                 "```rego\ny\n```\n")
                rows.append({"arm": arm, "runIndex": run_index,
                             "indexWithinPilot": index,
                             "slot": os.path.relpath(slot, self.root)})
        with open(os.path.join(here, "PILOT.json"), "w") as handle:
            json.dump({"callsMade": len(rows), "callsRegistered": 36,
                       "complete": True,
                       "citable": False, "calls": rows}, handle)
        with open(os.path.join(here, "PILOT.md"), "w") as handle:
            handle.write("# Pre-freeze calibration pilot\n")

    def stub_scoring(self):
        """Admission passes, gold is perfect for arm B only, identity passes
        for arms A and B — a pattern the recount and the floors both see."""
        outcomes = {"A": (False, True), "B": (True, True), "C": (False, False)}
        def score(tools, arm, slot_dir, gold, guard, workdir):
            perfect, identity = outcomes[arm]
            return {"slot": os.path.relpath(slot_dir, self.root), "arm": arm,
                    "code": None, "goldPerfect": perfect,
                    "goldFailures": 0 if perfect else 3,
                    "identityPass": identity,
                    "identityWhy": None if identity else "kills-reference",
                    "suitePresent": True}
        patched = mock.patch.object(self.sweep_rates, "score_slot", score)
        patched.start()
        self.addCleanup(patched.stop)

    def test_the_published_record_is_the_derivers_own_contract(self):
        """THE point of the module: what it publishes, the sealed deriver
        accepts — asserted through the deriver's own functions, not a copied
        schema."""
        self.stub_scoring()
        record = self.pilot_rates.pilot_rates(None, self.label, [], os.path.join(
            self.root, "scratch"), self.pins)
        floor = self.pilot_rates.derive_floor_module()
        floor.validate_record(record)
        self.assertEqual(record["perArm"]["A"],
                         {"attempted": 12, "calls": 12, "apparatusExcluded": 0,
                          "apparatusCodes": {}, "perfect": 0,
                          "identityPass": 12, "codes": []})
        self.assertEqual(record["perArm"]["B"]["perfect"], 12)
        self.assertEqual(record["perArm"]["C"]["identityPass"], 0)
        self.assertIs(record["citable"], False)
        self.assertIn("no kill quantity", record["obligation"])

    def test_the_go_no_go_is_in_the_record_and_reads_the_declaration(self):
        self.stub_scoring()
        record = self.pilot_rates.pilot_rates(None, self.label, [], os.path.join(
            self.root, "scratch"), self.pins)
        self.assertEqual(round(
            record["derived"]["perArm"]["A"]["identityFloor"], 3), 0.779)
        verdict = record["goNoGo"]
        self.assertFalse(verdict["go"])
        self.assertEqual(verdict["failingArms"], ["C"])
        self.assertIn("ABORT", verdict["consequence"])

    def test_an_incomplete_pilot_publishes_no_rates(self):
        """§2a.1's table prices n=12 apparatus-clean per arm exactly; an arm
        that reached fewer is a DEVIATIONS.md event, not a smaller
        denominator. ROUND-2 FINDING R2-10 moved the refusal from a call
        COUNT to the SCORED count, because the two stopped being the same
        number the moment attempts could be replaced.

        MUTATION: delete the `calls != PILOT_CALLS_PER_ARM` raise in
        `pilot_rates()` — an 11-call arm publishes a floor derived at the
        wrong n and this test fails."""
        shutil.rmtree(self.calibration)
        self.build_pilot_tree(calls=35)
        self.stub_scoring()
        with self.assertRaisesRegex(self.pilot_rates.RatesError,
                                    "PILOT-SHORT"):
            self.pilot_rates.pilot_rates(None, self.label, [], os.path.join(
                self.root, "scratch"), self.pins)

    def test_an_apparatus_refusal_leaves_the_denominator_it_used_to_fail_in(
            self):
        """ROUND-2 FINDING R2-10, the arithmetic that made the gate a coin
        flip. An engine that never answered used to be counted as an
        identity FAILURE inside a denominator fixed at 12 — so six genuine
        passes plus six engine no-answers scored 6/12 and the floor was
        derived from a number the apparatus produced. §1a says the
        denominator is "attempted runs whose apparatus succeeded".

        Here arm A holds 12 clean calls and 3 apparatus-refused ones. The
        cell must read attempted 15, calls 12, apparatusExcluded 3 — and the
        identity count must be over the 12, not the 15.

        MUTATION: revert `per_arm_cell()` to counting over every row — calls
        becomes 15, the deriver refuses the record (calls != 12), and this
        test fails at the first assertion."""
        outcomes = {"A": (False, True), "B": (True, True), "C": (False, False)}
        refused = {"A": 3}
        seen = {"A": 0}
        def score(tools, arm, slot_dir, gold, guard, workdir):
            record = {"slot": os.path.relpath(slot_dir, self.root),
                      "arm": arm, "code": None, "apparatusCode": None,
                      "goldPerfect": False, "goldFailures": 3,
                      "identityPass": False, "identityWhy": None,
                      "suitePresent": True}
            if arm in refused and seen[arm] < refused[arm]:
                seen[arm] += 1
                record["apparatusCode"] = "engine-invocation-refused"
                record["identityPass"] = None
                return record
            perfect, identity = outcomes[arm]
            record["goldPerfect"] = perfect
            record["identityPass"] = identity
            return record
        patched = mock.patch.object(self.sweep_rates, "score_slot", score)
        patched.start()
        self.addCleanup(patched.stop)
        shutil.rmtree(self.calibration)
        self.build_pilot_tree(calls=39, per_arm={"A": 15, "B": 12, "C": 12})
        record = self.pilot_rates.pilot_rates(None, self.label, [], os.path.join(
            self.root, "scratch"), self.pins)
        cell = record["perArm"]["A"]
        self.assertEqual(cell["attempted"], 15)
        self.assertEqual(cell["calls"], 12)
        self.assertEqual(cell["apparatusExcluded"], 3)
        self.assertEqual(cell["apparatusCodes"],
                         {"engine-invocation-refused": 3})
        self.assertEqual(cell["identityPass"], 12)
        # …and the sealed deriver accepts it, which is the whole point: the
        # record reconciles as one partition.
        self.pilot_rates.derive_floor_module().validate_record(record)

    def test_publishing_over_an_existing_ledger_is_refused(self):
        with open(os.path.join(self.calibration, self.label,
                               "PILOT-RATES.json"), "w") as handle:
            handle.write("{}")
        with self.assertRaisesRegex(self.pilot_rates.RatesError,
                                    "RATES-EXISTS"):
            self.pilot_rates.main(["--label", self.label, "--write"])

    def test_the_module_reaches_no_kill_machinery(self):
        """The registered scope, asserted at the source exactly as
        `test_sweep_rates.py` asserts it for the sweep's publisher."""
        with open(os.path.join(HARNESS, "pilot_rates.py"), "r",
                  encoding="utf-8") as handle:
            source = handle.read()
        for token in ("kill_rates", "kill_of", "survivorsPaired",
                      "mutant_kill", "load_mutants", "build_pairing"):
            self.assertNotIn(token, source)


# --- the freeze gate validates, it does not merely find ----------------------

class TheFreezeGateValidation(unittest.TestCase):
    """R1-17's sentence about `make_manifest.py`, driven: each departure from
    a registered pilot output is a named problem."""

    def setUp(self):
        self.root = os.path.realpath(
            os.path.join(os.environ.get("TMPDIR", "/tmp"),
                         "pilot-gate-%d" % os.getpid()))
        shutil.rmtree(self.root, ignore_errors=True)
        self.addCleanup(shutil.rmtree, self.root, True)
        self.label = "2026-08-24-pilot"
        os.makedirs(os.path.join(self.root, "calibration", self.label))
        os.makedirs(os.path.join(self.root, "harness"))
        self.floor = floor_module()
        record = pilot_record(self.label)
        self.write_record(record)
        with open(os.path.join(self.root, "calibration", self.label,
                               "PILOT.json"), "w") as handle:
            json.dump({"callsMade": 36, "callsRegistered": 36}, handle)
        self.write_pins()

    def write_record(self, record):
        path = os.path.join(self.root, "calibration", self.label,
                            "PILOT-RATES.json")
        with open(path, "w") as handle:
            json.dump(record, handle, indent=2, sort_keys=True)
            handle.write("\n")
        self.record = record

    def write_pins(self, **edits):
        import hashlib
        record_path = os.path.join(self.root, "calibration", self.label,
                                   "PILOT-RATES.json")
        with open(record_path, "rb") as handle:
            digest = "sha256:%s" % hashlib.sha256(handle.read()).hexdigest()
        calibration = {
            "label": self.label,
            "outputSha256": digest,
            "derivedFloor": json.loads(json.dumps(
                self.floor.derive(self.record))),
            "minimumViable": 0.20,
            "minimumViableBasis": "identityFloor",
        }
        calibration.update(edits)
        with open(os.path.join(self.root, "harness", "PINS.json"),
                  "w") as handle:
            json.dump({"calibration": calibration}, handle)

    def problems(self):
        return make_manifest.calibration_problems(self.root)

    def test_a_registered_pilot_output_passes(self):
        self.assertEqual(self.problems(), [])

    def test_a_tampered_count_is_refused_by_the_sealed_deriver(self):
        """The pins were made over the honest record; the record's BYTES then
        move. The deriver's refusal is the first problem and returns early, so
        it — not the digest mismatch behind it — is what the gate names."""
        path = os.path.join(self.root, "calibration", self.label,
                            "PILOT-RATES.json")
        with open(path, "w") as handle:
            json.dump(pilot_record(self.label, A={"perfect": 13}), handle)
        problems = self.problems()
        self.assertTrue(any("sealed deriver refuses" in problem
                            for problem in problems), problems)

    def test_a_no_go_record_cannot_freeze(self):
        self.write_pins(minimumViable=0.99)
        problems = self.problems()
        self.assertTrue(any("NO-GO" in problem for problem in problems),
                        problems)

    def test_a_stale_output_digest_is_a_problem(self):
        self.write_pins(outputSha256="sha256:" + "0" * 64)
        problems = self.problems()
        self.assertTrue(any("outputSha256" in problem for problem in problems),
                        problems)

    def test_a_chosen_number_wearing_a_derived_ones_name_is_a_problem(self):
        pinned = json.loads(json.dumps(self.floor.derive(self.record)))
        pinned["perArm"]["A"]["identityFloor"] = 0.9
        self.write_pins(derivedFloor=pinned)
        problems = self.problems()
        self.assertTrue(any("derivedFloor" in problem for problem in problems),
                        problems)

    def test_an_unpinned_label_is_a_problem(self):
        self.write_pins(label=None)
        problems = self.problems()
        self.assertTrue(any("calibration.label" in problem
                            for problem in problems), problems)

    def test_a_second_label_is_a_problem(self):
        os.makedirs(os.path.join(self.root, "calibration",
                                 "2026-08-25-pilot"))
        problems = self.problems()
        self.assertTrue(any("ONE pilot" in problem for problem in problems),
                        problems)

    def test_a_missing_record_is_a_problem(self):
        os.unlink(os.path.join(self.root, "calibration", self.label,
                               "PILOT-RATES.json"))
        problems = self.problems()
        self.assertTrue(any("PILOT-RATES.json" in problem
                            for problem in problems), problems)

    def test_an_undeclared_minimum_is_refused_at_the_gate_too(self):
        self.write_pins(minimumViable=None)
        problems = self.problems()
        self.assertTrue(any("sealed deriver refuses" in problem
                            for problem in problems), problems)


if __name__ == "__main__":
    unittest.main()
