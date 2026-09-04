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

from test_batch import (HARNESS, REGISTRY, STUDY, StandInStudy,
                        write_plan)
import pilot_fixture

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
    partition that must reconcile. ROUND-2 FINDING R2-7 put the per-slot ROWS
    beneath the cells, and the sealed deriver reconciles each cell to its rows
    — so an edit here moves the rows too, and a case that wants a cell to
    CONTRADICT its rows says so with `rows=False`."""
    rows_follow = per_arm_edits.pop("rows", True)
    per_arm = {arm: {"calls": 12, "attempted": 12, "apparatusExcluded": 0,
                     "apparatusCodes": {}, "perfect": 8, "identityPass": 10,
                     "codes": []}
               for arm in ("A", "B", "C")}
    for arm, edit in per_arm_edits.items():
        per_arm[arm].update(edit)
    slots = []
    if rows_follow:
        for arm in ("A", "B", "C"):
            cell = per_arm[arm]
            index = 0
            for _ in range(cell["apparatusExcluded"]):
                index += 1
                slots.append({"slot": "calibration/%s/arm-%s/run-%03d"
                                      % (label, arm, index), "arm": arm,
                              "code": None,
                              "apparatusCode": "engine-invocation-refused",
                              "goldPerfect": False, "identityPass": None})
            for scored in range(cell["calls"]):
                index += 1
                slots.append({"slot": "calibration/%s/arm-%s/run-%03d"
                                      % (label, arm, index), "arm": arm,
                              "code": None, "apparatusCode": None,
                              "goldPerfect": scored < cell["perfect"],
                              "identityPass": scored < cell["identityPass"]})
            if cell["apparatusExcluded"]:
                cell["apparatusCodes"] = {"engine-invocation-refused":
                                          cell["apparatusExcluded"]}
    return {"label": label, "citable": False, "perArm": per_arm,
            "slots": slots}


# --- the registered numbers, bound to the registration's own bytes -----------

class TheRegisteredPilot(unittest.TestCase):

    def test_the_per_arm_count_is_the_registrations_own_twelve(self):
        """§2a.2's sentence, the driver's constant and the registry's member
        are one registration in three places."""
        self.assertIn("Pilot N: **12/arm**", prereg_text())
        self.assertEqual(batch.PILOT_RUNS_PER_ARM, 12)
        self.assertEqual(registry()["calibration"]["pilotPerArm"], 12)
        self.assertEqual(batch.PILOT_CALL_CAP, 36)
        # ROUND-2 FINDING R2-10: the second number the amended §2a.2 names.
        self.assertEqual(batch.PILOT_ATTEMPT_CAP_PER_ARM, 21)
        self.assertEqual(batch.PILOT_ATTEMPT_CAP, 63)
        self.assertEqual(registry()["calibration"]["attemptCapPerArm"], 21)
        self.assertEqual(registry()["calibration"]["scoredPerArm"], 12)
        self.assertIn("at most 21 attempts per arm",
                      prereg_text().replace("\n", " "))

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

    def test_no_carrier_promises_a_second_pilot(self):
        """§2a.6 as amended (round 2, R2-12): one pilot, terminal. The struck
        rule's phrases may appear in PREREGISTRATION.md ONLY inside the marked
        amendment block that quotes it, and in NO code or record carrier.
        Names the strings rather than a generic phrase — the failure mode
        R2-17 documents for a currency test that cannot discriminate.

        MUTATION: restore any one carrier's sentence — this fails."""
        phrases = ("maximum over all pilots", "tightest over all pilots",
                   "Re-piloting is monotone", "requiring a re-pilot under C5")
        # The registration is hard-wrapped prose inside a quoted block, so a
        # phrase can straddle a "\n> " break: unwrap before searching.
        text = prereg_text().replace("\n> ", " ").replace("\n", " ")
        block_start = text.index("AMENDED (round 2, R2-12) — the first "
                                 "printing's rule, struck and kept")
        block_end = text.index("## 3. Arms", block_start)
        outside = text[:block_start] + text[block_end:]
        block = text[block_start:block_end]
        for phrase in phrases[:3]:
            self.assertIn(phrase, block, phrase)
        # §2a.5's clause lives ONLY as its own strike-through, outside the
        # §2a.6 block; everything else appears nowhere outside the block.
        self.assertEqual(outside.count("requiring a re-pilot under C5"), 1)
        self.assertIn("~~requiring a re-pilot under C5~~", outside)
        stray = outside.replace("~~requiring a re-pilot under C5~~", "")
        for phrase in phrases:
            self.assertNotIn(phrase, stray, phrase)
        for rel in ("calibration/derive_floor.py", "harness/batch.py",
                    "harness/make_manifest.py", "DEVIATIONS.md",
                    "harness/SCAFFOLD.md"):
            with open(os.path.join(STUDY, rel), "rb") as handle:
                body = handle.read().decode("utf-8")
            for phrase in phrases:
                self.assertNotIn(phrase, body, (rel, phrase))
        self.assertIn("There is no second pilot.", text)
        self.assertIn("batch.py abandon --label", text)

    def test_calibration_invalid_is_terminal(self):
        """R2-12's test 2. NON-DISCRIMINATING TODAY and labelled so: C4 is
        unimplemented (R2-11), so this asserts an absence — the gate's name is
        in the registered list and no module reaches a re-pilot verdict. It
        becomes a real test once R2-11 lands."""
        from e4lib import decision
        self.assertIn("c4-transfer-calibration", decision.CONTROL_GATES)
        for root, dirs, files in os.walk(HARNESS):
            dirs[:] = [d for d in dirs if d != "tests"]   # production only
            for name in files:
                if not name.endswith(".py"):
                    continue
                with open(os.path.join(root, name), "rb") as handle:
                    self.assertNotIn(b"re-pilot verdict", handle.read(),
                                     name)


# --- the schedule and the slot shape -----------------------------------------

class TheSchedule(unittest.TestCase):

    def test_it_is_thirty_six_calls_arm_interleaved_a_first_when_all_clean(self):
        """The fixed order is the all-clean case of R2-10's round robin, and
        every entry carries the batch's five schedule keys (R2-8) so the
        primary path's `stamp_slot()` / `seal_slot()` / `ledger_record()` are
        reused verbatim."""
        entries = batch.pilot_schedule()
        self.assertEqual(len(entries), 36)
        self.assertEqual([entry["arm"] for entry in entries],
                         ["A", "B", "C"] * 12)
        for key in batch.SCHEDULE_KEYS:
            self.assertIn(key, entries[0])
        self.assertEqual(entries[0]["globalIndex"], 1)
        self.assertEqual(entries[0]["slotIndex"], 1)
        self.assertEqual(entries[-1], {"arm": "C", "runIndex": 12,
                                       "slotIndex": 12, "round": 12,
                                       "position": 3, "globalIndex": 36,
                                       "indexWithinPilot": 36})

    def test_a_refused_attempt_draws_another_for_that_arm(self):
        """ROUND-2 FINDING R2-10's rule, driven: the round robin keeps calling
        an arm until it holds 12 wrapper-clean calls, and the refused attempt
        keeps its slot index — nothing is re-spent under an existing name.

        MUTATION: make `pilot_next_entry()` count every attempt as clean —
        arm A stops at 12 attempts with 11 clean and the assertion fails."""
        records = []
        while True:
            entry = batch.pilot_next_entry(records)
            if entry is None:
                break
            code = ("call-nonzero-exit"
                    if entry["arm"] == "A" and entry["slotIndex"] == 3
                    else None)
            records.append({"arm": entry["arm"], "code": code,
                            "slotIndex": entry["slotIndex"]})
        status = batch.pilot_status(records)
        self.assertEqual(len(records), 37)
        self.assertEqual(status["perArm"]["A"],
                         {"attempted": 13, "wrapperClean": 12})
        self.assertEqual(status["perArm"]["B"],
                         {"attempted": 12, "wrapperClean": 12})
        self.assertEqual(status["short"], [])
        self.assertTrue(status["complete"])
        a_slots = [record["slotIndex"] for record in records
                   if record["arm"] == "A"]
        self.assertEqual(a_slots, list(range(1, 14)))

    def test_an_arm_short_at_the_cap_ends_the_pilot_short(self):
        """§2a.2 as amended: at most 21 attempts per arm; an arm still short
        is named in `short` and the pilot is COMPLETE (nothing more to call)
        — the driver then refuses to publish rates."""
        records = []
        while True:
            entry = batch.pilot_next_entry(records)
            if entry is None:
                break
            records.append({"arm": entry["arm"],
                            "code": ("call-timeout" if entry["arm"] == "C"
                                     else None)})
        status = batch.pilot_status(records)
        self.assertEqual(status["perArm"]["C"],
                         {"attempted": 21, "wrapperClean": 0})
        self.assertEqual(status["short"], ["C"])
        self.assertTrue(status["complete"])

    def test_the_replay_refuses_a_deleted_duplicated_or_reordered_record(self):
        """ROUND-2 FINDING R2-7's mechanism: the order is DERIVED from the
        records' own codes, so the ledger can be authenticated without a
        constant to compare against.

        MUTATION: sort the records by globalIndex before replaying — the
        reordered case passes and this test fails, which is exactly why
        `load_ledger()` refuses rather than re-sorts."""
        label = "2026-08-24-pilot"
        records = []
        previous = None
        while True:
            entry = batch.pilot_next_entry(records)
            if entry is None:
                break
            record = {key: entry[key] for key in batch.SCHEDULE_KEYS}
            record.update({"path": os.path.relpath(
                batch.pilot_slot_path(label, entry["arm"], entry["slotIndex"]),
                batch.STUDY), "code": None, "wrapperExit": 0,
                "manifestSha256": "sha256:" + "0" * 64,
                "previousSha256": previous})
            previous = batch.record_digest(record)
            records.append(record)
        batch.pilot_replay(records, label)
        deleted = records[:5] + records[6:]
        with self.assertRaisesRegex(batch.BatchError, "diverges"):
            batch.pilot_replay(deleted, label)
        duplicated = records[:6] + [records[5]] + records[6:]
        with self.assertRaisesRegex(batch.BatchError, "diverges"):
            batch.pilot_replay(duplicated, label)
        reordered = list(records)
        reordered[3], reordered[4] = reordered[4], reordered[3]
        with self.assertRaisesRegex(batch.BatchError, "diverges"):
            batch.pilot_replay(reordered, label)
        extra = records + [dict(records[-1], globalIndex=37)]
        with self.assertRaisesRegex(batch.BatchError, "past the end|after the "
                                    "round robin"):
            batch.pilot_replay(extra, label)

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

    def test_a_cell_that_contradicts_its_rows_is_refused(self):
        """ROUND-2 FINDING R2-7's headline, at the contract: an honest NO-GO
        record (arm A identity 5/12) whose counter is rewritten to 6 now
        contradicts the rows beneath it.

        MUTATION: drop the per-arm recount loop in `validate_record()` — the
        rewritten record passes and this test fails, which is the byte-for-byte
        state the reviewer executed."""
        honest = pilot_record(A={"identityPass": 5})
        self.floor.validate_record(honest)
        rewritten = pilot_record(A={"identityPass": 5})
        rewritten["perArm"]["A"]["identityPass"] = 6
        with self.assertRaisesRegex(self.floor.FloorError,
                                    "recount|disagrees"):
            self.floor.validate_record(rewritten)
        # …and a record with no rows at all is refused outright.
        bare = pilot_record(rows=False)
        with self.assertRaisesRegex(self.floor.FloorError, "no per-slot rows"):
            self.floor.validate_record(bare)

    def test_a_stale_embedded_verdict_is_refused(self):
        """R2-7: an embedded `derived` block that is not its own recomputation
        is stale or edited. MUTATION: drop the embedded-derived equality — a
        record carrying a foreign block passes."""
        record = pilot_record()
        record["derived"] = self.floor.derive(record)
        self.floor.validate_record(record)
        record["derived"]["perArm"]["A"]["identityFloor"] = 0.99
        with self.assertRaisesRegex(self.floor.FloorError, "stale or edited"):
            self.floor.validate_record(record)

    def test_a_duplicated_slot_row_is_refused(self):
        record = pilot_record()
        record["slots"].append(dict(record["slots"][0]))
        record["perArm"]["A"]["attempted"] += 1
        record["perArm"]["A"]["calls"] += 1
        with self.assertRaisesRegex(self.floor.FloorError, "twice"):
            self.floor.validate_record(record)

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
        # The stand-in registry fills EVERY freeze pin with a digest string,
        # and since round 2 the five calibration members are freeze pins — a
        # filled label is "a pilot that has run". This fixture is the pilot
        # that has NOT run yet, so its own lifecycle pins are null.
        pilot_fixture.reset_calibration_pins(pins)
        self.write_pins(pins)
        self.golden_from_a_real_call()

    def golden_from_a_real_call(self) -> None:
        """ROUND-2 FINDING R2-8: the golden capture is a PRECONDITION of the
        pilot, so the fixture makes one — one probe call, its own
        `context.json` becomes the golden — the derivation the recapture
        command performs, reduced to the one capture these cases need."""
        slot = os.path.join(self.root, "seed", "capture-001")
        status, code, stderr = batch.invoke(slot, self.scratch, self.pins_path,
                                            self.cli, "probe", batch.PROBE_ARM,
                                            self.probe_prompt)
        self.assertEqual((status, code), (0, None), stderr)
        with open(os.path.join(slot, "context.json")) as handle:
            self.write_golden(json.load(handle)["entries"])
        # `write_golden()` rewrote the registry; the declaration and the
        # pre-pilot lifecycle state must survive.
        pins = json.loads(json.dumps(self.pins))
        pins["calibration"]["minimumViable"] = 0.20
        pins["calibration"]["minimumViableBasis"] = "identityFloor"
        pilot_fixture.reset_calibration_pins(pins)
        self.write_pins(pins)

    def plan(self, *steps):
        """Rewrite the stand-in CLI's plan and reset its counter, so the next
        wrapper call is step 0 — without touching the pinned binary."""
        write_plan(self.cli_dir, list(steps))
        counter = os.path.join(self.cli_dir, "counter")
        if os.path.exists(counter):
            os.unlink(counter)

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
        """§2a.6 as amended (R2-12): one pilot, TERMINAL — the message no
        longer offers a DEVIATIONS.md branch, because there is none."""
        pins = json.loads(json.dumps(self.pins))
        pins["calibration"]["label"] = "2026-08-20-pilot"
        self.write_pins(pins)
        with self.assertRaisesRegex(batch.BatchError, "terminal"):
            self.preflight()

    def test_a_spent_pilot_tree_is_terminal(self):
        """R2-12 re-pointed: the existing-tree rule keys on EVIDENCE of a spent
        pilot — a ledger with at least one wrapper-clean call. A bare directory
        no longer counts (see the abandon cases), so this fixture writes the
        evidence.

        MUTATION: revert the rule to `os.listdir()` — the bare-directory case
        below refuses with the terminal message and
        `test_a_label_that_spent_nothing_names_the_abandon_path` fails."""
        pilot_fixture.build(self.study, "2026-08-20-pilot", self.pins)
        with self.assertRaisesRegex(batch.BatchError, "TERMINAL"):
            self.preflight()

    def test_a_label_that_spent_nothing_names_the_abandon_path(self):
        """A bare directory, or a label under which every call was refused,
        spent nothing and is not the one pilot — but it occupies the subtree,
        and before R2-12 a `--label` typo the wrapper refused every call under
        bricked the study. The refusal names the registered way out."""
        os.makedirs(os.path.join(self.calibration_root, "2026-08-20-pilot"))
        with self.assertRaisesRegex(batch.BatchError, "abandon --label"):
            self.preflight()

    def test_the_golden_capture_is_a_precondition_of_the_pilot(self):
        """ROUND-2 FINDING R2-8: `transcript_check.check()` runs gate 4 — the
        golden pre-prompt context — unconditionally, so a pilot bound with no
        golden would file every slot as unreadable apparatus. The capture
        precedes the pilot (§2a.2 as amended).

        MUTATION: drop `require_golden()` from `pilot_preflight()` — this
        refusal disappears, and the end-to-end case that binds slots then
        sees 36 apparatus codes where it expects none."""
        pins = json.loads(json.dumps(self.pins))
        pins["golden"]["sha256"] = None
        self.write_pins(pins)
        with self.assertRaisesRegex(batch.BatchError, "golden"):
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
    wrapper bytes, real slots, real ledger — and, after ROUND-2 FINDING R2-8,
    real seals and a real chain."""

    PLAN = [{"completion": "an answer"}] * 80

    def pilot(self, *extra):
        return batch.main(["batch.py", "pilot", "--scratch-parent",
                           self.scratch, "--pins", self.pins_path,
                           "--cli-override", self.cli, "--label", self.LABEL]
                          + list(extra))

    def ledger(self):
        with open(os.path.join(self.calibration_root, self.LABEL,
                               batch.PILOT_LEDGER_NAME)) as handle:
            return json.load(handle)

    def test_a_dry_run_plans_the_all_clean_order_and_makes_none(self):
        self.assertEqual(self.pilot("--dry-run"), 0)
        self.assertFalse(os.path.isdir(os.path.join(self.calibration_root,
                                                    self.LABEL)))

    def test_the_pilot_runs_into_the_registered_tree_sealed_and_chained(self):
        """R2-8's test 1: every slot carries the seal and the transcript
        verdict; every CALL.json carries the three schedule stamps; the ledger
        replays and its chain verifies. This test FAILED on the tree before the
        repair — the pilot wrote none of it — which is the mutation check
        already run. MUTATION: delete the `seal_slot()` call from
        `run_pilot()` — the manifest assertion fails."""
        self.assertEqual(self.pilot(), 0)
        body = self.ledger()
        self.assertEqual(body["callsMade"], 36)
        self.assertTrue(body["complete"])
        self.assertEqual(body["short"], [])
        self.assertIs(body["citable"], False)
        self.assertEqual(body["label"], self.LABEL)
        self.assertEqual([record["arm"] for record in body["records"]],
                         ["A", "B", "C"] * 12)
        self.assertEqual(body["perArm"]["A"],
                         {"attempted": 12, "wrapperClean": 12})
        batch.pilot_replay(body["records"], self.LABEL)
        self.assertIsNotNone(body["pinsSha256"])
        self.assertEqual(body["goldenSha256"], self.pins["golden"]["sha256"])
        for record in body["records"]:
            slot = os.path.join(self.study, record["path"])
            self.assertTrue(os.path.isfile(os.path.join(slot,
                                                        batch.MANIFEST_NAME)))
            self.assertTrue(os.path.isfile(os.path.join(slot,
                                                        batch.TRANSCRIPT_NAME)))
            entry = {key: record[key] for key in batch.SCHEDULE_KEYS}
            self.assertEqual(batch.verify_seal_of(slot, entry),
                             record["manifestSha256"])
            with open(os.path.join(slot, "CALL.json")) as handle:
                call = json.load(handle)
            for member in ("globalIndex", "round", "position"):
                self.assertEqual(call[member], record[member])
            self.assertEqual(call["pinLabel"], "PILOT")
            self.assertIs(call["citable"], False)
            self.assertEqual(call["pinsSha256"].split(":")[-1],
                             body["pinsSha256"].split(":")[-1])
            self.assertEqual(call["reasoningEffort"],
                             self.pins["codex"]["reasoningEffort"])
            with open(os.path.join(slot, batch.TRANSCRIPT_NAME)) as handle:
                self.assertTrue(json.load(handle)["admissible"])
        table = open(os.path.join(self.calibration_root, self.LABEL,
                                  batch.PILOT_TABLE_NAME)).read()
        self.assertIn("citable: false", table)
        self.assertIn("| 36 | C | 012 |", table)
        self.assertIn("sealed and the ledger is chained", table)

    def test_a_refused_call_is_recorded_sealed_and_another_is_drawn(self):
        """R2-8's test 2 with R2-10's rule: attempt 7 (arm A's third) exits
        non-zero; the slot carries REFUSAL.json, is sealed and chained under
        `call-nonzero-exit`, and the round robin draws a 13th attempt for arm A
        so the pilot still ends with 12 clean per arm.

        MUTATION: remove the `refuse_slot()` call — the refused slot has no
        REFUSAL.json, `slot_outcome()` refuses it as non-terminal, and the
        replay assertion fails."""
        plan = [{"completion": "an answer"}] * 80
        plan[6] = {"completion": "partial", "exit": 3}
        self.plan(*plan)
        self.assertEqual(self.pilot(), 0)
        body = self.ledger()
        self.assertEqual(body["callsMade"], 37)
        self.assertEqual(body["perArm"]["A"],
                         {"attempted": 13, "wrapperClean": 12})
        refused = [record for record in body["records"]
                   if record["code"] is not None]
        self.assertEqual(len(refused), 1)
        self.assertEqual(refused[0]["code"], "call-nonzero-exit")
        self.assertEqual((refused[0]["arm"], refused[0]["slotIndex"]), ("A", 3))
        slot = os.path.join(self.study, refused[0]["path"])
        self.assertTrue(os.path.isfile(os.path.join(slot, "REFUSAL.json")))
        self.assertFalse(os.path.isfile(os.path.join(slot, "completion.txt")))
        entry = {key: refused[0][key] for key in batch.SCHEDULE_KEYS}
        self.assertEqual(batch.verify_seal_of(slot, entry),
                         refused[0]["manifestSha256"])
        batch.pilot_replay(body["records"], self.LABEL)
        self.assertTrue(os.path.isdir(os.path.join(
            self.calibration_root, self.LABEL, "arm-A", "run-013")))

    def test_a_tool_using_author_stays_in_the_pilots_denominator(self):
        """R2-8's discriminating case. The wrapper exits 0 and writes NO
        completion for a tool-using author, by design; the binding files it
        `author-protocol-violation`, an AUTHORING outcome; the slot is sealed
        and counts as wrapper-clean. Then `pilot_rates` scores it inside
        `calls == 12` as goldPerfect False / identity not asked — never as the
        apparatus code `slot-shape`, which would delete from the denominator
        exactly the runs §3's no-tools instruction exists to catch.

        MUTATION: put the completion-presence check AHEAD of the transcript
        read in `pilot_rates.slot_pre_step()` — the slot becomes `slot-shape`
        and `calls` drops to 11."""
        import pilot_rates
        import sweep_rates
        plan = [{"completion": "an answer"}] * 80
        plan[3] = {"completion": "an artifact", "tool_call": True}
        self.plan(*plan)
        self.assertEqual(self.pilot(), 0)
        body = self.ledger()
        self.assertEqual(body["callsMade"], 36)
        record = body["records"][3]
        self.assertIsNone(record["code"])
        slot = os.path.join(self.study, record["path"])
        self.assertFalse(os.path.isfile(os.path.join(slot, "completion.txt")))
        with open(os.path.join(slot, batch.TRANSCRIPT_NAME)) as handle:
            sealed = json.load(handle)
        self.assertEqual((sealed["side"], sealed["code"]),
                         ("authoring", "author-protocol-violation"))
        # Score through the real pre-step with a canned scorer for the clean
        # slots — the engines are not under test here, the pre-step is.
        real = sweep_rates.score_slot
        def score(tools, arm, slot_dir, gold, guard, workdir, **kwargs):
            if kwargs.get("prior_code") is not None:
                return real(tools, arm, slot_dir, gold, guard, workdir,
                            **kwargs)
            return {"slot": os.path.relpath(slot_dir, self.study), "arm": arm,
                    "code": None, "apparatusCode": None, "goldPerfect": True,
                    "goldFailures": 0, "identityPass": True,
                    "identityWhy": None, "suitePresent": True}
        with mock.patch.object(sweep_rates, "score_slot", score), \
                mock.patch.object(pilot_rates, "STUDY", self.study), \
                mock.patch.object(pilot_rates, "CALIBRATION_ROOT",
                                  self.calibration_root), \
                mock.patch.object(sweep_rates, "STUDY", self.study):
            rates = pilot_rates.pilot_rates(None, self.LABEL, [], os.path.join(
                self.root, "rates-scratch"), self.pins)
        rows = {row["slot"]: row for row in rates["slots"]}
        row = rows[record["path"]]
        self.assertEqual(row["code"], "author-protocol-violation")
        self.assertIsNone(row["apparatusCode"])
        self.assertIs(row["goldPerfect"], False)
        self.assertEqual(row["identityWhy"], "not-asked")
        cell = rates["perArm"][record["arm"]]
        self.assertEqual((cell["attempted"], cell["calls"],
                          cell["apparatusExcluded"]), (12, 12, 0))
        self.assertEqual(cell["codes"], ["author-protocol-violation"])

    def test_a_mutated_transcript_breaks_its_seal(self):
        """R2-8's test 4: a byte appended to a sealed `session.jsonl` — the
        recomputed seal differs and the rates publisher refuses the whole
        publication. MUTATION: hash file CONTENTS only, ignoring the recorded
        length — an append of a byte that keeps the digest is impossible, but
        a same-length rewrite is not; the seal records both, and the test
        asserts the refusal names the seal."""
        import pilot_rates
        self.assertEqual(self.pilot(), 0)
        body = self.ledger()
        slot = os.path.join(self.study, body["records"][0]["path"])
        with open(os.path.join(slot, "session.jsonl"), "ab") as handle:
            handle.write(b"\n")
        entry = {key: body["records"][0][key] for key in batch.SCHEDULE_KEYS}
        with self.assertRaises(batch.BatchError):
            batch.verify_seal_of(slot, entry)
        with mock.patch.object(pilot_rates, "STUDY", self.study), \
                mock.patch.object(pilot_rates, "CALIBRATION_ROOT",
                                  self.calibration_root):
            with self.assertRaisesRegex(pilot_rates.RatesError, "RATES-SEAL"):
                pilot_rates.pilot_rates(None, self.LABEL, [], os.path.join(
                    self.root, "rates-scratch"), self.pins)
        # …and the freeze gate names it too (R2-7 check (c)).
        problems = make_manifest.pilot_ledger_problems(
            __import__("pathlib").Path(self.study), self.LABEL, None)[0]
        self.assertTrue(any("does not verify" in problem or "seal" in problem
                            for problem in problems), problems)

    def test_the_pilot_leaves_nothing_in_the_arms_root(self):
        """The third root's point, §2a.2's first difference: after the calls
        the freeze gate still sees no authoring state — and the seals live
        under calibration/, outside arms/ (R2-8's test 7, asserted rather
        than assumed)."""
        self.assertEqual(self.pilot(), 0)
        for arm in batch.ARMS:
            self.assertFalse(os.path.exists(
                os.path.join(self.arms_root, arm, "authoring")))
        self.assertEqual(make_manifest.prior_authoring_problems(self.study),
                         [])

    def test_a_second_pilot_is_refused_as_terminal(self):
        self.assertEqual(self.pilot(), 0)
        self.assertEqual(self.pilot(), 1)

    def test_a_bricking_label_is_recoverable_by_abandon(self):
        """R2-12's test 4, end to end: every call refused under a label spends
        nothing; the preflight then names `abandon`; `abandon --label` retains
        the tree under `abandoned-<label>/` once DEVIATIONS.md names it; and a
        real pilot then succeeds. MUTATION: let `abandon_pilot()` accept a
        label holding one clean call — the paired negative below must refuse,
        or abandon becomes a way to erase a real pilot."""
        plan = [{"completion": "partial", "exit": 3}] * 80
        self.plan(*plan)
        self.assertEqual(self.pilot(), 3)          # short at the cap, no rates
        body = self.ledger()
        self.assertEqual(body["short"], ["A", "B", "C"])
        self.assertEqual(body["perArm"]["A"]["wrapperClean"], 0)
        self.assertEqual(self.pilot(), 1)          # occupied: names abandon
        deviations = os.path.join(self.study, "DEVIATIONS.md")
        with open(deviations, "w") as handle:
            handle.write("# Deviations\n\nAbandoned pilot label %s: every "
                         "call preflight-refused.\n" % self.LABEL)
        self.assertEqual(batch.main(["batch.py", "abandon", "--label",
                                     self.LABEL, "--pins", self.pins_path]), 0)
        self.assertTrue(os.path.isdir(os.path.join(
            self.calibration_root, "abandoned-" + self.LABEL)))
        self.assertFalse(os.path.exists(os.path.join(self.calibration_root,
                                                     self.LABEL)))
        self.plan(*([{"completion": "an answer"}] * 80))
        self.assertEqual(self.pilot(), 0)
        # The paired negative: a spent pilot cannot be abandoned.
        with self.assertRaisesRegex(batch.BatchError, "TERMINAL"):
            batch.abandon_pilot(self.LABEL)

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
    with a stubbed scorer so no binary runs, like `test_sweep_rates.py`, over
    a SEALED, CHAINED pilot tree (R2-8) whose transcript binding is stubbed
    per slot (`pilot_fixture.stub_transcript()`)."""

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
            pilot_fixture.stub_transcript(),
        ]
        for patched in patches:
            patched.start()
            self.addCleanup(patched.stop)
        self.pins = {"calibration": {"minimumViable": 0.20,
                                     "minimumViableBasis": "identityFloor"},
                     "codex": {"reasoningEffort": "s020-stand-in-effort"},
                     "golden": {"sha256": "sha256:" + "3" * 64}}
        self.tree = self.build_pilot_tree()

    def build_pilot_tree(self, outcomes=None):
        if os.path.isdir(self.calibration):
            shutil.rmtree(self.calibration)
        return pilot_fixture.build(self.root, self.label, self.pins,
                                   outcomes=outcomes)

    def stub_scoring(self, outcomes=None):
        """Admission passes, gold is perfect for arm B only, identity passes
        for arms A and B — a pattern the recount and the floors both see. A
        slot carrying a PRIOR code takes the real early return."""
        outcomes = outcomes or {"A": (False, True), "B": (True, True),
                                "C": (False, False)}
        real = self.sweep_rates.score_slot
        def score(tools, arm, slot_dir, gold, guard, workdir, **kwargs):
            if kwargs.get("prior_code") is not None:
                return real(tools, arm, slot_dir, gold, guard, workdir,
                            **kwargs)
            perfect, identity = outcomes[arm]
            return {"slot": os.path.relpath(slot_dir, self.root), "arm": arm,
                    "code": None, "apparatusCode": None,
                    "goldPerfect": perfect,
                    "goldFailures": 0 if perfect else 3,
                    "identityPass": identity,
                    "identityWhy": None if identity else "kills-reference",
                    "suitePresent": True}
        patched = mock.patch.object(self.sweep_rates, "score_slot", score)
        patched.start()
        self.addCleanup(patched.stop)

    def rates(self):
        return self.pilot_rates.pilot_rates(None, self.label, [], os.path.join(
            self.root, "scratch"), self.pins)

    def test_the_published_record_is_the_derivers_own_contract(self):
        """THE point of the module: what it publishes, the sealed deriver
        accepts — asserted through the deriver's own functions, not a copied
        schema."""
        self.stub_scoring()
        record = self.rates()
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
        self.assertEqual(sorted(row["slot"] for row in record["slots"]),
                         sorted(r["path"] for r in self.tree.records))
        self.assertEqual(record["ledgerPinsSha256"], self.tree.pins_sha256)

    def test_the_go_no_go_is_in_the_record_and_reads_the_declaration(self):
        self.stub_scoring()
        record = self.rates()
        self.assertEqual(round(
            record["derived"]["perArm"]["A"]["identityFloor"], 3), 0.779)
        verdict = record["goNoGo"]
        self.assertFalse(verdict["go"])
        self.assertEqual(verdict["failingArms"], ["C"])
        self.assertIn("ABORT", verdict["consequence"])

    def test_a_short_pilot_publishes_no_rates(self):
        """§2a.1's table prices n=12 apparatus-clean per arm exactly; an arm
        that reached fewer is a DEVIATIONS.md event, not a smaller
        denominator. ROUND-2 FINDING R2-10 moved the refusal from a call COUNT
        to the SCORED count. MUTATION: delete the `complete`/`short` check in
        `pilot_rates()` — a short ledger reaches the per-arm refusal instead;
        both are asserted."""
        self.stub_scoring()
        self.build_pilot_tree(outcomes={"C": ["timeout"] * 21})
        with self.assertRaisesRegex(self.pilot_rates.RatesError,
                                    "PILOT-INCOMPLETE"):
            self.rates()

    def test_a_wrapper_refused_attempt_is_excluded_and_another_was_drawn(self):
        """R2-8/R2-10 together: arm A's third attempt was refused; it sits in
        the ledger and the rows under `call-nonzero-exit` on the APPARATUS
        side, the round robin drew a 13th, and the cell reads attempted 13 /
        calls 12 / excluded 1. MUTATION: revert `per_arm_cell()` to counting
        every row — calls becomes 13 and the deriver refuses the record."""
        self.stub_scoring()
        self.build_pilot_tree(outcomes={"A": ["clean", "clean", "refused"]})
        record = self.rates()
        cell = record["perArm"]["A"]
        self.assertEqual((cell["attempted"], cell["calls"],
                          cell["apparatusExcluded"]), (13, 12, 1))
        self.assertEqual(cell["apparatusCodes"], {"call-nonzero-exit": 1})
        refused = [row for row in record["slots"] if row["apparatusCode"]]
        self.assertEqual(len(refused), 1)
        self.assertEqual(refused[0]["priorCode"], "call-nonzero-exit")
        self.pilot_rates.derive_floor_module().validate_record(record)

    def test_an_apparatus_refusal_at_scoring_leaves_the_denominator(self):
        """ROUND-2 FINDING R2-10, the arithmetic that made the gate a coin
        flip: an engine that never answered used to be counted as an identity
        FAILURE inside a denominator fixed at 12. Here the scorer refuses
        three of arm A's slots at scoring time (`engine-invocation-refused`);
        the cell must read the three as excluded, not as failing suites — and
        the pilot is then SHORT (9 clean scored), so no rates publish."""
        seen = {"A": 0}
        real = self.sweep_rates.score_slot
        def score(tools, arm, slot_dir, gold, guard, workdir, **kwargs):
            if kwargs.get("prior_code") is not None:
                return real(tools, arm, slot_dir, gold, guard, workdir,
                            **kwargs)
            row = {"slot": os.path.relpath(slot_dir, self.root), "arm": arm,
                   "code": None, "apparatusCode": None, "goldPerfect": False,
                   "goldFailures": 3, "identityPass": True,
                   "identityWhy": None, "suitePresent": True}
            if arm == "A" and seen["A"] < 3:
                seen["A"] += 1
                row["apparatusCode"] = "engine-invocation-refused"
                row["identityPass"] = None
            return row
        patched = mock.patch.object(self.sweep_rates, "score_slot", score)
        patched.start()
        self.addCleanup(patched.stop)
        with self.assertRaisesRegex(self.pilot_rates.RatesError,
                                    "PILOT-SHORT arm A reached 9"):
            self.rates()

    def test_a_tool_using_author_is_counted_and_scores_zero(self):
        """R2-8's discriminating case at the unit level: an authoring-side
        transcript verdict on a slot with no completion is COUNTED under its
        code, apparatus clean, scoring zero — not `slot-shape`."""
        self.stub_scoring()
        self.build_pilot_tree(outcomes={"B": ["tool"]})
        record = self.rates()
        cell = record["perArm"]["B"]
        self.assertEqual((cell["attempted"], cell["calls"]), (12, 12))
        self.assertEqual(cell["codes"], ["author-protocol-violation"])
        self.assertEqual(cell["perfect"], 11)
        row = next(r for r in record["slots"]
                   if r["code"] == "author-protocol-violation")
        self.assertIsNone(row["apparatusCode"])
        self.assertEqual(row["transcript"]["side"], "authoring")

    def test_an_unexplained_missing_completion_is_slot_shape(self):
        """The fence stands where no prior code explains the absence — and it
        is APPARATUS discovered at scoring time, which the driver could not
        see: the wrapper exited 0, the round robin counted the call as clean,
        and the arm is therefore SHORT of 12 scored calls. That is the honest
        consequence §2a.2 as amended registers (no rates, a DEVIATIONS.md
        event), not a smaller denominator."""
        self.stub_scoring()
        self.build_pilot_tree(outcomes={"C": ["no-completion"]})
        with self.assertRaisesRegex(self.pilot_rates.RatesError,
                                    "PILOT-SHORT arm C reached 11.*slot-shape"):
            self.rates()

    def test_a_registry_stamp_that_is_not_the_ledgers_is_apparatus(self):
        """R2-8's pre-step order, item 3: `pinsSha256` reconciles to the
        LEDGER HEADER — the registry every call ran under — never to the
        current registry, which §2a.6's ceremony edits after the pilot."""
        self.stub_scoring()
        slot = self.tree.slot_path("A", 2)
        call_path = os.path.join(slot, "CALL.json")
        with open(call_path) as handle:
            call = json.load(handle)
        call["pinsSha256"] = "sha256:" + "f" * 64
        with open(call_path, "w") as handle:
            json.dump(call, handle, indent=2, sort_keys=True)
        # The edit broke the seal — which is the FIRST thing the pre-step
        # sees, and the whole publication refuses.
        with self.assertRaisesRegex(self.pilot_rates.RatesError, "RATES-SEAL"):
            self.rates()

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
    """ROUND-2 FINDING R2-7: the freeze gate AUTHENTICATES the pilot from its
    sealed, chained ledger; a labelled subtree with a two-counter PILOT.json
    and a hand-authored rates record — the reviewer's executed attack — is
    refused by name. Each case asserts a SPECIFIC problem substring; asserting
    only `problems != []` cannot say which check fired."""

    def setUp(self):
        import pilot_rates
        import sweep_rates
        self.pilot_rates = pilot_rates
        self.root = os.path.realpath(
            os.path.join(os.environ.get("TMPDIR", "/tmp"),
                         "pilot-gate-%d" % os.getpid()))
        shutil.rmtree(self.root, ignore_errors=True)
        self.addCleanup(shutil.rmtree, self.root, True)
        os.makedirs(os.path.join(self.root, "harness"))
        self.label = "2026-08-24-pilot"
        self.floor = floor_module()
        self.pins = {"codex": {"reasoningEffort": "s020-stand-in-effort"},
                     "golden": {"sha256": "sha256:" + "3" * 64}}
        patches = [
            mock.patch.object(pilot_rates, "STUDY", self.root),
            mock.patch.object(pilot_rates, "CALIBRATION_ROOT",
                              os.path.join(self.root, "calibration")),
            mock.patch.object(sweep_rates, "STUDY", self.root),
            pilot_fixture.stub_transcript(),
        ]
        for patched in patches:
            patched.start()
            self.addCleanup(patched.stop)
        self.scorer = {"A": (False, True), "B": (True, True),
                       "C": (False, True)}
        real = sweep_rates.score_slot
        def score(tools, arm, slot_dir, gold, guard, workdir, **kwargs):
            if kwargs.get("prior_code") is not None:
                return real(tools, arm, slot_dir, gold, guard, workdir,
                            **kwargs)
            perfect, identity = self.scorer[arm]
            return {"slot": os.path.relpath(slot_dir, self.root), "arm": arm,
                    "code": None, "apparatusCode": None,
                    "goldPerfect": perfect, "goldFailures": 0,
                    "identityPass": identity, "identityWhy": None,
                    "suitePresent": True}
        patched = mock.patch.object(sweep_rates, "score_slot", score)
        patched.start()
        self.addCleanup(patched.stop)
        self.tree = pilot_fixture.build(self.root, self.label, self.pins)
        self.publish()
        self.artifacts = pilot_fixture.write_analysis_artifacts(self.root,
                                                                self.label)
        self.write_pins()

    def publish(self):
        """`pilot_rates.py --write`'s effect: the record, from the real
        publisher over the sealed tree."""
        record = self.pilot_rates.pilot_rates(
            None, self.label, [], os.path.join(self.root, "scratch"),
            {"calibration": {"minimumViable": 0.20,
                             "minimumViableBasis": "identityFloor"},
             "codex": self.pins["codex"], "golden": self.pins["golden"]})
        self.write_record(record)

    def record_path(self):
        return os.path.join(self.root, "calibration", self.label,
                            "PILOT-RATES.json")

    def write_record(self, record):
        with open(self.record_path(), "w") as handle:
            json.dump(record, handle, indent=2, sort_keys=True)
            handle.write("\n")
        self.record = record

    def write_pins(self, **edits):
        import hashlib
        with open(self.record_path(), "rb") as handle:
            digest = "sha256:%s" % hashlib.sha256(handle.read()).hexdigest()
        # The pin is the record's OWN embedded floors when it carries them
        # (a forged record cannot be re-derived: the sealed deriver refuses
        # it), else the honest derivation.
        derived = self.record.get("derived") or self.floor.derive(self.record)
        calibration = {
            "label": self.label,
            "outputSha256": digest,
            "derivedFloor": json.loads(json.dumps(derived)),
            "minimumViable": 0.20,
            "minimumViableBasis": "identityFloor",
            # ROUND 2 (R2-11, R2-13): the two analysis artifacts are pinned
            # too, and the gate requires them.
            "c4ReferenceSha256": self.artifacts["C4-REFERENCE.json"],
            "dispersionSha256": self.artifacts["PILOT-DISPERSION.json"],
        }
        calibration.update(edits)
        with open(os.path.join(self.root, "harness", "PINS.json"),
                  "w") as handle:
            json.dump({"calibration": calibration, "codex": self.pins["codex"],
                       "golden": self.pins["golden"]}, handle)

    def problems(self):
        return make_manifest.calibration_problems(self.root)

    def assert_problem(self, needle):
        problems = self.problems()
        self.assertTrue(any(needle in problem for problem in problems),
                        "no problem names %r in %r" % (needle, problems))
        return problems

    def test_a_registered_pilot_output_passes(self):
        self.assertEqual(self.problems(), [])

    def test_a_pilot_that_never_ran_is_refused(self):
        """THE test that would have caught R2-7: the reviewer's fixture — a
        two-counter PILOT.json and a hand-authored rates record with matching
        pins — must be refused by name. MUTATION: restore
        `if not (here/"PILOT.json").is_file()` as the only ledger check in
        `calibration_record_problems()` — this passes the gate."""
        here = os.path.join(self.root, "calibration", self.label)
        shutil.rmtree(here)
        os.makedirs(here)
        with open(os.path.join(here, "PILOT.json"), "w") as handle:
            json.dump({"callsMade": 36, "callsRegistered": 36}, handle)
        self.write_record(pilot_record(self.label))
        self.write_pins()
        # (the analysis artifacts are gone with the tree; the ledger refusal
        # is named FIRST, which is the point)
        self.assert_problem("no chained records")

    def test_a_deleted_slot_is_refused(self):
        shutil.rmtree(self.tree.slot_path("A", 7))
        self.assert_problem("not a directory on disk")

    def test_a_duplicated_slot_is_refused(self):
        shutil.copytree(self.tree.slot_path("A", 7),
                        self.tree.slot_path("A", 13))
        self.assert_problem("the ledger does not name it")

    def test_a_reordered_ledger_is_refused(self):
        """MUTATION: sort `records` by globalIndex before replaying — this
        passes, which is exactly why `load_ledger()` refuses rather than
        re-sorts."""
        ledger = self.tree.ledger()
        ledger["records"][3], ledger["records"][4] = \
            ledger["records"][4], ledger["records"][3]
        with open(os.path.join(self.root, "calibration", self.label,
                               "PILOT.json"), "w") as handle:
            json.dump(ledger, handle)
        self.assert_problem("diverges")

    def test_a_mutated_call_json_breaks_the_seal(self):
        slot = self.tree.slot_path("A", 1)
        path = os.path.join(slot, "CALL.json")
        with open(path) as handle:
            call = json.load(handle)
        call["reasoningEffort"] = "high"
        with open(path, "w") as handle:
            json.dump(call, handle, indent=2, sort_keys=True)
        self.assert_problem("does not verify")

    def test_a_resealed_slot_is_still_refused(self):
        """Mutating CALL.json AND regenerating that slot's manifest: the seal
        now verifies against the slot, but not against the LEDGER's recorded
        digest. MUTATION: compare the manifest to itself instead of to
        `manifestSha256` — this passes. The previous case alone does not
        discriminate re-sealing; both are required."""
        slot = self.tree.slot_path("A", 1)
        path = os.path.join(slot, "CALL.json")
        with open(path) as handle:
            call = json.load(handle)
        call["reasoningEffort"] = "high"
        with open(path, "w") as handle:
            json.dump(call, handle, indent=2, sort_keys=True)
        os.unlink(os.path.join(slot, batch.MANIFEST_NAME))
        entry = {key: self.tree.records[0][key] for key in batch.SCHEDULE_KEYS}
        batch.seal_slot(slot, entry)
        self.assert_problem("re-sealed")

    def test_a_rewritten_counter_contradicts_the_ledger(self):
        """THE HEADLINE: an honest NO-GO pilot (arm C identity 5/12), its
        counter moved to 6, output digest and derived floor re-pinned, rows
        left truthful. Must name the disagreement AND must not report GO.
        MUTATION: drop the per-arm reconciliation from `validate_record()` —
        the gate returns [] (the byte-for-byte state the reviewer executed)."""
        self.scorer["C"] = (False, False)
        shutil.rmtree(os.path.join(self.root, "calibration"))
        self.tree = pilot_fixture.build(self.root, self.label, self.pins,
                                        outcomes={"C": ["clean"]})
        # identity passes for 5 of C's 12: stub by row order
        counter = {"C": 0}
        import sweep_rates
        real = sweep_rates.score_slot
        def score(tools, arm, slot_dir, gold, guard, workdir, **kwargs):
            if kwargs.get("prior_code") is not None:
                return real(tools, arm, slot_dir, gold, guard, workdir,
                            **kwargs)
            identity = True
            if arm == "C":
                counter["C"] += 1
                identity = counter["C"] <= 5
            return {"slot": os.path.relpath(slot_dir, self.root), "arm": arm,
                    "code": None, "apparatusCode": None, "goldPerfect": False,
                    "goldFailures": 3, "identityPass": identity,
                    "identityWhy": None, "suitePresent": True}
        with mock.patch.object(sweep_rates, "score_slot", score):
            self.publish()
        self.artifacts = pilot_fixture.write_analysis_artifacts(self.root,
                                                                self.label)
        self.assertFalse(self.record["goNoGo"]["go"])
        self.write_pins()
        self.assert_problem("NO-GO")
        rewritten = json.loads(json.dumps(self.record))
        rewritten["perArm"]["C"]["identityPass"] = 6
        # The sealed deriver itself now refuses to derive from this record
        # (the cell contradicts its rows), so the forger must hand-build the
        # floors — exactly what a re-pin would have to do.
        with self.assertRaisesRegex(self.floor.FloorError, "recount"):
            self.floor.derive(self.floor._strip(rewritten))
        forged = json.loads(json.dumps(self.record["derived"]))
        forged["perArm"]["C"]["identityPass"] = 6
        forged["perArm"]["C"]["identityFloor"] = \
            self.floor.one_sided_lower_bound(6, 12)
        rewritten["derived"] = forged
        rewritten["goNoGo"] = self.floor.go_no_go(forged, 0.20,
                                                  "identityFloor")
        self.assertTrue(rewritten["goNoGo"]["go"])
        self.write_record(rewritten)
        self.write_pins()
        problems = self.assert_problem("recount")
        self.assertFalse(any("GO" in problem and "NO-GO" not in problem
                             for problem in problems))

    def test_a_stale_embedded_verdict_is_refused(self):
        record = json.loads(json.dumps(self.record))
        record["goNoGo"]["go"] = not record["goNoGo"]["go"]
        self.write_record(record)
        self.write_pins()
        self.assert_problem("stale or rewritten verdict")

    def test_a_foreign_label_is_refused(self):
        record = json.loads(json.dumps(self.record))
        record["label"] = "2026-01-01-pilot"
        self.write_record(record)
        self.write_pins()
        self.assert_problem("naming another")

    def test_a_no_go_record_cannot_freeze(self):
        self.write_pins(minimumViable=0.99)
        self.assert_problem("NO-GO")

    def test_a_stale_output_digest_is_a_problem(self):
        self.write_pins(outputSha256="sha256:" + "0" * 64)
        self.assert_problem("outputSha256")

    def test_a_chosen_number_wearing_a_derived_ones_name_is_a_problem(self):
        pinned = json.loads(json.dumps(self.floor.derive(self.record)))
        pinned["perArm"]["A"]["identityFloor"] = 0.9
        self.write_pins(derivedFloor=pinned)
        self.assert_problem("derivedFloor")

    def test_an_unpinned_label_is_a_problem(self):
        self.write_pins(label=None)
        self.assert_problem("calibration.label")

    def test_a_second_label_is_a_problem(self):
        os.makedirs(os.path.join(self.root, "calibration",
                                 "2026-08-25-pilot"))
        self.assert_problem("ONE pilot")

    def test_an_abandoned_label_does_not_count_but_is_checked(self):
        """§2a.6 as amended (R2-12): `abandoned-<label>/` is skipped by the
        one-pilot count, and refused if it hides a clean call."""
        abandoned = os.path.join(self.root, "calibration",
                                 "abandoned-2026-08-20-pilot")
        os.makedirs(abandoned)
        with open(os.path.join(abandoned, "PILOT.json"), "w") as handle:
            json.dump({"records": [{"arm": "A", "code": "call-timeout"}]},
                      handle)
        self.assertEqual(self.problems(), [])
        with open(os.path.join(abandoned, "PILOT.json"), "w") as handle:
            json.dump({"records": [{"arm": "A", "code": None}]}, handle)
        self.assert_problem("spent pilot under a name")

    def test_a_missing_record_is_a_problem(self):
        os.unlink(self.record_path())
        self.assert_problem("PILOT-RATES.json")

    def test_an_undeclared_minimum_is_refused_at_the_gate_too(self):
        self.write_pins(minimumViable=None)
        self.assert_problem("sealed deriver refuses")


if __name__ == "__main__":
    unittest.main()
