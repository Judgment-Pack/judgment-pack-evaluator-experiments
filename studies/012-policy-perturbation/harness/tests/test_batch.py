#!/usr/bin/env python3
"""The batch driver end to end, against a stand-in CLI and a stand-in operator
HOME — ported from Study 011's `harness/tests/test_batch.py` and adapted to
five arms and §2.8's registered call order (round 3 finding 12).

The real wrapper runs: the same bash, the same `env -i` scrub, the same fresh
HOME and CODEX_HOME per run, the same binary-digest and CLI-version gates (the
stand-in's digest is pinned in a test registry, so the check passes because it
was satisfied and not because it was skipped), the same arm-keyed slot rule,
the same slot retention, and the real §3.2 recapture with the probe prompt.
Only the binary, the operator's home and the directory the wrapper resolves as
its own study are stand-ins — the wrapper's bytes are the committed ones,
reached through a symlink — and none of them reaches a network or a model.
`$HOME` is redirected to a throwaway directory for every case, so the
operator's real credential is never copied anywhere by the suite.

What this proves that a unit test cannot: that a failing run terminates its own
slot with a refusal record and the batch CONTINUES (§2.5's ported difference
from Study 010); that the slots the wrapper writes carry the arm, the arm
prompt digest and the three schedule stamps §2.9 registers, in the arm's own
tree; that resumption by global schedule index merges the ledger rather than
replacing it [D-22]; that a batch killed between a slot's seal and its ledger
append is resumed — and declared short — from the seal the driver itself wrote,
and refuses every wider disagreement (round 6, finding 6); that no slot is
created before the golden capture is registered; that no retained byte carries
the credential; and that §6 C7 retains its three files and deletes the
transcript itself.

Two adaptations to §2.10 [D-23], which are also the two things this file
deliberately does NOT do:

  * **the population root is derived**, so there is no `--slots` to point at a
    throwaway tree — `batch.ARMS_ROOT` and `batch.RESULTS` are patched to this
    test's own root instead, exactly as Study 011's file already patched
    `RESULTS`, and every refusal line under test is the registered one. Round
    9, finding 6 adds a THIRD patched constant, `batch.SCRIPT`, for the same
    reason and not a new one: the wrapper's own slot guard is now anchored at
    the `$STUDY` it resolves from its own location, so a tree the wrapper will
    write into has to BE a study. `fixtures.standin_study()` builds one — the
    committed wrapper reached through a symlink, so the bytes that run are the
    committed bytes and only the path they are invoked by moves — and the test
    therefore moves `$STUDY` rather than giving the wrapper a new input or
    weakening the guard under test;
  * **the scorer takes no registry argument**, so a batch made under a stand-in
    registry cannot be scored: every slot would name a registry that is not the
    committed one and score `registry-mismatch`, which is the guarantee working
    rather than a gap. Study 011's tests that ran the driver's slots on to a
    rate table are therefore not ported; the scorer's own surfaces are tested
    over `fixtures.Population` in `test_admission.py` and `test_verdict_parity.py`.

The last class in the file is §4.3's frozen interval scope — a walk over a
scored population requiring the set of blocks carrying `ci95` to be exactly the
registered list. It lives here because it needs a full scoring and no other
file in the suite walks that surface.
"""
from __future__ import annotations
import ast
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import unittest
from unittest import mock

import batch
import fixtures
import integrity
import score_rates

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(os.path.dirname(HERE))
# The committed wrapper — the bytes every case in this file runs. Each case
# reaches them through the stand-in study's symlink, so what moves is the path
# the wrapper is invoked by and never the bytes (round 9, finding 6).
WRAPPER = os.path.join(STUDY, "transcription", "authoring_call.sh")
REGISTRY = os.path.join(STUDY, "harness", "PINS.json")

# One round of §2.8's registered order — five slots, one per arm, in the order
# the registration puts them (round 1 is W2: B, C, A, D, E). The batch is 150
# slots and no test runs it; every case below runs a bounded prefix through
# `--runs`, which is the registered way to run less than the whole order.
BATCH_RUNS = 5
ENTRIES = batch.schedule_entries()


def arm_completion(arm: str) -> str:
    """A completion at THAT arm's registered edges. The driver judges no
    completion — the scorer does — but a slot whose transcript is at the wrong
    pair would be a fixture that lies about which cell it came from."""
    pair = fixtures.arm_pair(os.path.join(STUDY, "arms"), arm)
    return fixtures.completion(fixtures.full_records(*pair))


# Two probe captures for the §3.2 recapture, then the first round: four runs
# that answer, and a fifth that fails, so every case that runs the whole round
# exercises the registered difference from Study 010 — the slot is refused and
# the batch continues.
PLAN = ([{"completion": "ready"}, {"completion": "ready"}]
        + [{"completion": arm_completion(entry["arm"])}
           for entry in ENTRIES[:BATCH_RUNS - 1]]
        + [{"completion": arm_completion(ENTRIES[BATCH_RUNS - 1]["arm"]),
            "exit": 3}])


def registered_interpreter() -> str:
    """The running interpreter if it is the one §2.10 registers, else "".

    Every case in `Batch` invokes the real wrapper, and the wrapper's FIRST gate
    is the registry's `python` member: `batch.invoke()` passes `sys.executable`
    as `PYTHON_BIN` (§2.7's environment contract, ported unchanged), so under
    any other interpreter every call in this class would be refused by the
    study's own registration rather than by anything under test. The class is
    therefore skipped there and says so, instead of asserting a refusal that
    would be true of a correct driver and a broken one alike.
    `test_an_unregistered_interpreter_never_reaches_a_call` is where that gate
    IS the thing under test, and it runs under the registered one.
    """
    with open(REGISTRY) as handle:
        pins = json.load(handle)
    try:
        return integrity.verify_interpreter(pins)
    except integrity.IntegrityError:
        return ""


RUNNING_REGISTERED = registered_interpreter()


@unittest.skipUnless(
    RUNNING_REGISTERED,
    "the wrapper refuses an interpreter harness/PINS.json does not register "
    "(§2.10), so no wrapper-driven case can run here")
class Batch(unittest.TestCase):

    def setUp(self):
        self.root = fixtures.throwaway_root("s012-batch-")
        self.addCleanup(shutil.rmtree, self.root, True)
        self.scratch = os.path.join(self.root, "scratch")
        os.makedirs(self.scratch)
        # The operator's HOME, stood in for: a credential with a sentinel value
        # and no skills tree. Every wrapper call in this file copies THIS
        # credential, never the real one.
        self.home = fixtures.write_operator_home(os.path.join(self.root, "home"))
        self.environment = mock.patch.dict(os.environ, {"HOME": self.home})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        # [D-23]: the population root is DERIVED and no argument names it, so a
        # test that must not write into the committed arms/ tree points the
        # derived constant at its own root. The refusal lines under test are the
        # registered ones; only the root moves.
        #
        # Round 9, finding 6: the root the wrapper accepts is its OWN
        # `$STUDY/arms`, so the root that moves has to be a study's. The
        # stand-in study runs the committed wrapper through a symlink, and
        # `self.scratch` above stays a SIBLING of it — a scratch inside the
        # study's worktree is refused, by the same registered line.
        self.study = fixtures.standin_study(
            self.root, WRAPPER, os.path.join(STUDY, "harness"))
        self.wrapper_path = os.path.join(self.study, "transcription",
                                         "authoring_call.sh")
        self.patch_constant("SCRIPT", self.wrapper_path)
        self.arms_root = os.path.join(self.study, "arms")
        self.patch_constant("ARMS_ROOT", self.arms_root)
        # The no-new-slots marker is the STUDY's own RESULTS.json (§2.8),
        # pointed at this test's root for the same reason.
        self.patch_constant("RESULTS", os.path.join(self.root, "RESULTS.json"))
        # §6 C7's record is a batch precondition (round 9, finding 3) and its
        # path is canonical, so the constant moves here for the same reason
        # ARMS_ROOT does: no case may write into — or read — the committed
        # controls/ tree.
        self.patch_constant("DEFAULT_NEGATIVE",
                            os.path.join(self.root, "controls-isolation-negative"))
        self.cli_dir = os.path.join(self.root, "cli")
        self.cli = fixtures.write_fake_cli(self.cli_dir, PLAN, sys.executable, HERE)
        self.pins_path = os.path.join(self.root, "PINS.json")
        self.write_pins(self.stand_in_registry())
        self.captures = os.path.join(self.root, "recapture")
        self.golden = os.path.join(self.root, "GOLDEN-CONTEXT.json")

    def patch_constant(self, name: str, value):
        patched = mock.patch.object(batch, name, value)
        patched.start()
        self.addCleanup(patched.stop)

    def stand_in_registry(self) -> dict:
        """The committed registry with exactly three members moved: the stand-in
        binary's digest and version, and the freeze digest §2.10 requires to be
        non-null before any call. Everything the batch checks — N, the slot
        count, the registered order, the five arm prompts — is the committed
        registry's, so these tests run the real preflight and not a relaxed one.
        """
        with open(REGISTRY) as handle:
            pins = json.load(handle)
        pins["codex"]["binarySha256"] = batch._digest(self.cli)
        pins["codex"]["version"] = "codex-cli 0.145.0-fake"
        pins["freeze"]["preregistrationSha256"] = batch._digest(
            os.path.join(STUDY, "PREREGISTRATION.md"))
        return pins

    def write_pins(self, pins: dict) -> None:
        self.pins = pins
        with open(self.pins_path, "w") as handle:
            json.dump(pins, handle, indent=2)

    def alternate_registry(self, name: str, **edits) -> str:
        """A copy of the stand-in registry with one member replaced, written
        beside it. `edits` are top-level members, replaced whole."""
        pins = json.loads(json.dumps(self.pins))
        pins.update(edits)
        path = os.path.join(self.root, name)
        with open(path, "w") as handle:
            json.dump(pins, handle, indent=2)
        return path

    def register_golden(self) -> str:
        """§3.2 step 3, done as registered: the capture's digest replaces the
        null in the registry before the first slot runs."""
        pins = json.loads(json.dumps(self.pins))
        pins["golden"]["sha256"] = batch._digest(self.golden)
        self.write_pins(pins)
        return pins["golden"]["sha256"]

    def record_negative_control(self, **edits) -> str:
        """§6 C7's step-5 record and its assent, as the ceremony leaves them.

        WRITTEN rather than run: running the real control would consume a
        stand-in-CLI plan entry and shift every other case's PLAN. The
        control's own behaviour is tested against the real command below, and
        `stand_in_registry()` deliberately does not grant the assent — the
        control's own refusal test builds its null case from there.

        Round 10, finding 5: written with the members the REAL writer writes.
        The earlier five-member record was one `batch.capture_isolation_negative`
        could never have produced, so every case standing on this fixture
        admitted a record no run could leave — and a gate reading a member the
        writer had stopped writing would have stayed invisible here.
        """
        pins = json.loads(json.dumps(self.pins))
        pins["isolationNegative"]["assent"] = "granted"
        self.write_pins(pins)
        verdict = {"control": "C7 — the isolation gate's power",
                   "registeredExpectation": "the golden match FAILS",
                   "registeredOutcomes": list(batch.C7_OUTCOMES),
                   "outcome": "refused",
                   "message": "the golden pre-prompt context was not reproduced",
                   "wrapperExit": 0,
                   "wrapperCode": None,
                   "goldenSha256": batch._digest(self.golden),
                   "deletedByCode": {"session.jsonl": "sha256:" + "0" * 64},
                   "assent": "granted",
                   "retention": "This file and a stripped CALL.json are always "
                                "retained, and context.json whenever the call "
                                "produced a comparable context."}
        verdict.update(edits)
        os.makedirs(batch.DEFAULT_NEGATIVE, exist_ok=True)
        path = os.path.join(batch.DEFAULT_NEGATIVE, "VERDICT.json")
        with open(path, "w") as handle:
            json.dump(verdict, handle, indent=2)
        return path

    # -- the registered commands, as an operator would give them -------------

    def run_batch(self, extra=(), pins_path: str = None):
        return batch.main(["batch.py", "run", "--scratch-parent", self.scratch,
                           "--pins", pins_path or self.pins_path,
                           "--golden", self.golden,
                           "--cli-override", self.cli] + list(extra))

    def capture(self, out: str = None, extra=()):
        return batch.main(["batch.py", "capture", "--scratch-parent", self.scratch,
                           "--captures", self.captures, "--out", out or self.golden,
                           "--pins", self.pins_path, "--cli-override", self.cli]
                          + list(extra))

    def shortfall(self, reason: str = "the stand-in CLI batch was cut short on "
                                      "purpose", pins_path: str = None):
        return batch.main(["batch.py", "shortfall", "--reason", reason,
                           "--pins", pins_path or self.pins_path])

    def negative_control(self, out: str, pins_path: str = None):
        return batch.main(["batch.py", "capture-isolation-negative",
                           "--scratch-parent", self.scratch, "--out", out,
                           "--pins", pins_path or self.pins_path,
                           "--golden", self.golden, "--cli-override", self.cli])

    def wrapper(self, slot: str, arm: str, pins_path: str = None,
                cli: str = None, environment: dict = None, script: str = None):
        """One call of the real wrapper, by hand, as an operator would — with
        §2.7's two new arguments, the arm id and the arm's own prompt path.

        `script` names another stand-in study's copy of the same committed
        bytes, for the one case whose subject is the study the wrapper resolves
        for itself rather than the slot it is handed."""
        env = dict(os.environ)
        env["PYTHON_BIN"] = sys.executable
        # The driver subprocess must not write bytecode beside the
        # reviewed sources: the §2.10 gate refuses on a cache, and this
        # child does not inherit pytest's environment (round 5, finding 3).
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env.update(environment or {})
        return subprocess.run(
            ["bash", script or self.wrapper_path, self.scratch, slot,
             pins_path or self.pins_path,
             arm, os.path.join(STUDY, "arms", arm, "PROMPT.txt"),
             cli or self.cli],
            capture_output=True, text=True, env=env)

    def recapture_then_batch(self, extra=("--runs", str(BATCH_RUNS))):
        """The registered order: capture, agree, register the digest, record §6
        C7's control, then the batch."""
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        self.record_negative_control()
        self.assertEqual(self.run_batch(list(extra)), 0)

    # -- reading what the batch left -----------------------------------------

    def slot(self, offset: int) -> str:
        """The on-disk slot for the offset-th entry of the registered order."""
        entry = ENTRIES[offset]
        return os.path.join(self.arms_root, entry["arm"], "authoring",
                            "run-%03d" % entry["slotIndex"])

    def call_record(self, offset: int) -> dict:
        with open(os.path.join(self.slot(offset), "CALL.json")) as handle:
            return json.load(handle)

    def ledger(self) -> dict:
        with open(os.path.join(self.arms_root, "BATCH.json")) as handle:
            return json.load(handle)

    def declaration(self) -> dict:
        with open(os.path.join(self.arms_root, "SHORTFALL.json")) as handle:
            return json.load(handle)

    def calls_made(self) -> str:
        """The stand-in CLI's own call counter — the "before any call was spent"
        half of every refusal that claims it."""
        path = os.path.join(self.cli_dir, "counter")
        if not os.path.exists(path):
            return "0"
        with open(path) as handle:
            return handle.read()

    def dry_run_plan(self, extra) -> list:
        """The slot paths a `--dry-run` invocation says it would create."""
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            self.assertEqual(self.run_batch(list(extra) + ["--dry-run"]), 0)
        return [line.split("would create ", 1)[1].split(" ", 1)[0]
                for line in captured.getvalue().splitlines()
                if "would create " in line]

    def attempt(self, index: int = 1) -> str:
        return os.path.join(self.captures, "attempt-%d" % index)

    # --- the registry the preflight reads (round 3 finding 3) ---------------

    def test_the_committed_registry_passes_the_real_preflight_registry_checks(self):
        """The regression finding 3 named: the driver required `batch.runs` and
        a top-level `schedule.williams`/`schedule.blocks`, none of which the
        registry carries, so every real batch would have refused the moment its
        stage-null members were filled — and nothing noticed, because no test
        ran a preflight against the COMMITTED registry.

        This runs the real check against the real file. It is the whole of
        `preflight()`'s registry reading except the three members that are null
        until their registered moments (`freeze.preregistrationSha256`,
        `golden.sha256`, `isolationNegative.assent`), each of which has its own
        refusal test below —
        `test_a_batch_never_starts_against_an_unfrozen_preregistration`,
        `test_no_slot_is_created_before_the_golden_capture_is_registered`, and
        `test_a_batch_refuses_while_the_registry_records_no_assent`, which is
        the preflight's own refusal on the third and not only the C7 command's
        (round 9, finding 3).
        """
        with open(REGISTRY) as handle:
            committed = json.load(handle)
        batch.check_registry(committed)          # refuses by raising
        order = committed["batch"]["order"]
        self.assertEqual(
            batch.schedule(tuple(order["firstRow"]),
                           tuple(tuple(block) for block in order["blocks"])),
            batch.schedule())

    @staticmethod
    def members_read_by(module, function: str) -> set:
        """The registry member names one function asks for — the constants it
        passes to `.get()`, read off the SOURCE, in the idiom
        `test_admission.py` already uses to hold the shortfall's writer and
        reader to one spelling."""
        with open(module.__file__.replace(".pyc", ".py"), "rb") as handle:
            tree = ast.parse(handle.read().decode("utf-8"))
        asked = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef) or node.name != function:
                continue
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call) \
                        and isinstance(inner.func, ast.Attribute) \
                        and inner.func.attr == "get" and inner.args \
                        and isinstance(inner.args[0], ast.Constant) \
                        and isinstance(inner.args[0].value, str):
                    asked.add(inner.args[0].value)
        return asked

    def test_the_driver_the_scorer_and_the_registry_use_one_spelling(self):
        """The same defect, stated so that a NEW misspelling fails too. Every
        member name `check_registry()` asks the registry for must be a name the
        committed registry actually carries — `runs`, `schedule` and `williams`
        are not, which is why the reviewed draft read four members that could
        never answer — and it must be a name `score_rates.py` asks for as well,
        because the driver and the scorer check one registered order against one
        registry."""
        asked = self.members_read_by(batch, "check_registry")
        self.assertTrue(asked, "check_registry() reads no registry member")
        scorer = self.members_read_by(score_rates, "verify_preconditions")
        self.assertEqual(asked - scorer, set(),
                         "the driver reads registry members the scorer does not")

        def names(node) -> set:
            if isinstance(node, dict):
                found = set(node)
                for value in node.values():
                    found |= names(value)
                return found
            if isinstance(node, list):
                found = set()
                for value in node:
                    found |= names(value)
                return found
            return set()

        with open(REGISTRY) as handle:
            carried = names(json.load(handle))
        self.assertEqual(asked - carried, set(),
                         "the preflight reads registry members that do not exist")

    def test_the_pre_round_three_registry_spelling_refuses(self):
        """The counterfactual, so the fix is pinned rather than merely present:
        a registry carrying the members the reviewed draft read — and not the
        ones the registration registers — is refused rather than accepted."""
        old_spelling = json.loads(json.dumps(self.pins))
        old_spelling["batch"] = {"runs": batch.RUNS_PER_ARM}
        old_spelling["schedule"] = {
            "williams": {name: list(row) for name, row in batch.williams().items()},
            "blocks": [list(block) for block in batch.BLOCK_ORDERS]}
        with self.assertRaises(batch.BatchError) as caught:
            batch.check_registry(old_spelling)
        self.assertIn("batch.order", str(caught.exception))

    def test_a_registry_that_names_another_n_or_another_order_refuses(self):
        for name, member, value, expected in (
                ("n", "n", 25, "batch.n"),
                ("slots", "slots", 125, "batch.slots"),
                ("firstRow", "order", {"firstRow": ["B", "A", "E", "C", "D"],
                                       "blocks": [list(block) for block
                                                  in batch.BLOCK_ORDERS]},
                 "different call order"),
                ("blocks", "order", {"firstRow": list(batch.WILLIAMS_FIRST_ROW),
                                     "blocks": [list(reversed(block)) for block
                                                in batch.BLOCK_ORDERS]},
                 "different call order")):
            pins = json.loads(json.dumps(self.pins))
            pins["batch"][member] = value
            with self.assertRaises(batch.BatchError) as caught:
                batch.check_registry(pins)
            self.assertIn(expected, str(caught.exception), name)

    def test_a_registry_that_shrinks_n_never_reaches_a_call(self):
        """…and the same refusal through the registered command line, before a
        call is spent: [D-1]'s registered alternative of N = 25 is a different
        study, and the 30-round order must not be runnable under it."""
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        spent = self.calls_made()
        pins = json.loads(json.dumps(self.pins))
        pins["batch"]["n"] = 25
        path = os.path.join(self.root, "PINS-n25.json")
        with open(path, "w") as handle:
            json.dump(pins, handle, indent=2)
        self.assertEqual(self.run_batch(["--runs", "1"], pins_path=path), 1)
        self.assertFalse(os.path.exists(self.arms_root))
        self.assertEqual(self.calls_made(), spent)

    # --- the golden gate ----------------------------------------------------

    def test_no_slot_is_created_before_the_golden_capture_is_registered(self):
        # The failure this closes cost fifty real calls in Study 011: the batch
        # ran to completion and only the scorer noticed there was no allowlist.
        self.assertEqual(self.run_batch(["--runs", "1"]), 1)
        self.assertFalse(os.path.exists(self.arms_root))
        self.assertEqual(self.capture(), 0)          # the file exists…
        self.assertEqual(self.run_batch(["--runs", "1"]), 1)   # …unpinned
        self.assertFalse(os.path.exists(self.arms_root))
        self.register_golden()
        self.record_negative_control()
        self.assertEqual(self.run_batch(["--runs", "1"]), 0)
        self.assertTrue(os.path.isdir(self.slot(0)))

    def test_a_golden_that_is_not_the_registered_one_refuses(self):
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        with open(self.golden, "a") as handle:
            handle.write("\n")
        self.assertEqual(self.run_batch(["--runs", "1"]), 1)
        self.assertFalse(os.path.exists(self.arms_root))

    def test_a_batch_never_starts_against_an_unfrozen_preregistration(self):
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        unfrozen = self.alternate_registry(
            "PINS-unfrozen.json",
            freeze=dict(self.pins["freeze"], preregistrationSha256=None))
        self.assertEqual(self.run_batch(["--runs", "1"], pins_path=unfrozen), 1)
        self.assertFalse(os.path.exists(self.arms_root))

    def test_a_golden_capture_is_never_derived_from_batch_slots(self):
        self.recapture_then_batch(extra=["--runs", "1"])
        post_hoc = os.path.join(self.root, "POST-HOC.json")
        self.assertEqual(batch.main(["batch.py", "capture-golden",
                                     "--pins", self.pins_path, "--slots",
                                     os.path.dirname(self.slot(0)),
                                     "--out", post_hoc]), 1)
        self.assertFalse(os.path.exists(post_hoc))

    def test_capture_golden_writes_only_where_it_is_told(self):
        self.assertEqual(self.capture(), 0)
        # The property is that the refused call writes NOTHING — asserted as
        # "the study's own golden is byte-unchanged", not as "absent", because
        # once the study registers its real capture the file exists there
        # legitimately.
        registered = os.path.join(STUDY, "transcription", "GOLDEN-CONTEXT.json")
        before = (open(registered, "rb").read()
                  if os.path.exists(registered) else None)
        self.assertEqual(batch.main(["batch.py", "capture-golden",
                                     "--pins", self.pins_path,
                                     "--slots", self.attempt()]), 1)
        after = (open(registered, "rb").read()
                 if os.path.exists(registered) else None)
        self.assertEqual(before, after)

    def test_a_registered_capture_is_never_rewritten(self):
        self.assertEqual(self.capture(), 0)
        self.assertEqual(batch.main(["batch.py", "capture-golden",
                                     "--pins", self.pins_path, "--slots",
                                     self.attempt(), "--out", self.golden]), 1)

    def test_the_published_marker_refuses_new_slots_and_a_shortfall(self):
        # §2.8's guard, pinned at the patched constant: no slot in any arm and
        # no declaration once a rate has been computed — and the counterfactual
        # in the same test, because a guard that refuses everything proves
        # nothing.
        self.recapture_then_batch(extra=["--runs", "2"])
        with open(batch.RESULTS, "w") as handle:
            handle.write("{}\n")
        self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 1)
        self.assertFalse(os.path.exists(self.slot(2)))
        self.assertEqual(self.shortfall(), 1)
        self.assertFalse(os.path.exists(os.path.join(self.arms_root,
                                                     "SHORTFALL.json")))
        os.unlink(batch.RESULTS)
        self.assertEqual(self.shortfall(), 0)
        self.assertTrue(os.path.exists(os.path.join(self.arms_root,
                                                    "SHORTFALL.json")))

    # --- the ported bytes ---------------------------------------------------

    def test_drifted_ported_bytes_stop_the_batch_the_derivation_and_the_shortfall(self):
        """§6 C1 as a precondition of the CALLS, not only of CI — and of the two
        commands Study 011's round 3 found skipping it, since both feed the
        published arithmetic."""

        def refuse(*arguments, **keywords):
            raise integrity.IntegrityError("harness/policy_mirror.py is sha256:dead…")

        self.recapture_then_batch(extra=["--runs", "1"])
        out = os.path.join(self.root, "DRIFTED.json")
        with mock.patch.object(integrity, "verify", refuse):
            self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 1)
            self.assertEqual(batch.main(["batch.py", "capture-golden",
                                         "--pins", self.pins_path, "--slots",
                                         self.attempt(), "--out", out]), 1)
            self.assertEqual(self.shortfall("drifted bytes"), 1)
        self.assertFalse(os.path.exists(out))
        self.assertFalse(os.path.exists(os.path.join(self.arms_root,
                                                     "SHORTFALL.json")))
        self.assertFalse(os.path.exists(self.slot(1)))

    # --- the run ------------------------------------------------------------

    def test_a_dry_run_creates_nothing(self):
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        # Round 9, finding 3: preflight precedes the dry-run branch, so
        # `--dry-run` refuses until §6 C7's record exists — as it already did
        # for the golden gate.
        self.record_negative_control()
        spent = self.calls_made()
        self.assertEqual(self.dry_run_plan(["--runs", "3"]),
                         [os.path.relpath(self.slot(offset), STUDY)
                          for offset in range(3)])
        self.assertFalse(os.path.exists(self.arms_root))
        self.assertEqual(self.calls_made(), spent)

    def unpinned_cli(self) -> str:
        other = fixtures.write_fake_cli(os.path.join(self.root, "cli2"), PLAN,
                                        sys.executable, HERE)
        with open(other, "a") as handle:
            handle.write("# a different binary\n")
        return other

    def test_a_cli_that_is_not_the_pinned_one_never_reaches_a_call(self):
        code = batch.main(["batch.py", "run", "--scratch-parent", self.scratch,
                           "--pins", self.pins_path, "--golden", self.golden,
                           "--cli-override", self.unpinned_cli(), "--runs", "1"])
        self.assertEqual(code, 1)
        self.assertFalse(os.path.exists(self.arms_root))

    def test_the_wrapper_checks_the_digest_itself_not_only_the_driver(self):
        # The operator can run one call by hand; the pin has to hold there too.
        slot = self.slot(0)
        completed = self.wrapper(slot, ENTRIES[0]["arm"], cli=self.unpinned_cli())
        self.assertEqual(completed.returncode, 1)
        self.assertIn("not the pinned", completed.stderr)
        self.assertFalse(os.path.exists(slot))

    def test_the_cli_version_is_a_pre_call_gate_not_a_later_verdict(self):
        # §2.2 says the study does not run with a substitute; a gate that fires
        # after the call would only let the scorer mark the spent run invalid.
        fixtures.write_cli_version(self.cli_dir, "codex-cli 0.145.0")
        slot = self.slot(0)
        completed = self.wrapper(slot, ENTRIES[0]["arm"])
        self.assertEqual(completed.returncode, 1)
        self.assertIn("not the pinned", completed.stderr)
        self.assertFalse(os.path.exists(slot))
        self.assertEqual(self.calls_made(), "0")

    def test_the_wrapper_refuses_a_slot_that_is_not_the_arms_own_tree(self):
        """§2.7's arm-keyed slot rule, checked by the wrapper itself: an
        off-by-one in the driver's arm sequence would otherwise put a slot in
        another arm's tree silently, and every per-slot check would pass.

        Round 8, finding 6: the guard compared the parent and grandparent
        BASENAMES only, so `<anywhere>/C/authoring/run-001` satisfied it for arm
        C — the slot was not in an arms tree at all — and the slot name was
        unrestricted, so any name the scorer would later collect as a run, or
        one it would not collect at all, could be written under a
        correct-looking parent.

        Round 9, finding 6: four trailing components are a suffix, not a
        location, so `<anywhere>/arms/C/authoring/run-001` passed too. The slot
        must now EQUAL `$STUDY/arms/<ARM>/authoring/run-NNN` for the `$STUDY`
        the wrapper resolves from its own location — which is why these cases
        run under a stand-in study rather than under a bare throwaway root, and
        why `self.root` is now a FOREIGN root: outside the tree the wrapper is
        anchored in, whatever it is spelled like.
        """
        cases = (
            # The original: the right shape, the wrong arm.
            (os.path.join(self.arms_root, "B", "authoring", "run-001"), "C"),
            # The reviewer's case: right arm, right `authoring`, no arms tree.
            (os.path.join(self.root, "C", "authoring", "run-001"), "C"),
            # …and one level further out, where `arms` is the arm's own parent.
            (os.path.join(self.root, "arms", "authoring", "run-001"), "C"),
            # Round 9's case: every registered component, in the registered
            # order, under a root that is not this study's.
            (os.path.join(self.root, "arms", "C", "authoring", "run-001"), "C"),
            # Traversal embedded in an otherwise perfect path: it starts at the
            # anchor and leaves it, and equality is what sees that.
            (os.path.join(self.study, "arms", "C", "authoring", "..", "..",
                          "B", "authoring", "run-001"), "C"),
            # The unrestricted slot name, in the arm's real tree.
            (os.path.join(self.arms_root, "C", "authoring", "scratch"), "C"),
            (os.path.join(self.arms_root, "C", "authoring", "run-1"), "C"),
            (os.path.join(self.arms_root, "C", "authoring", "run-0001"), "C"),
        )
        for stray, arm in cases:
            completed = self.wrapper(stray, arm)
            self.assertEqual(completed.returncode, 1, stray)
            self.assertIn("not under arms/%s/authoring/" % arm,
                          completed.stderr, stray)
            self.assertFalse(os.path.exists(stray), stray)
        # A REPLACED component, which no comparison of the path's own text can
        # see: `arms/E/authoring` is a symlink out of the stand-in study, so
        # the anchor spells right and resolves elsewhere. This is a fixture
        # layout, not an exploit — the wrapper resolves each component of the
        # anchor physically before it makes the next. This case's link sits at
        # the LAST of the three, onto a directory that already exists, so
        # nothing had to be made under it either way; the earlier components,
        # where the ordering is what decides, are round 10 finding 6's
        # `test_a_replaced_ancestor_is_refused_before_anything_is_created`.
        elsewhere = os.path.join(self.root, "elsewhere")
        os.makedirs(elsewhere)
        os.makedirs(os.path.join(self.arms_root, "E"))
        os.symlink(elsewhere, os.path.join(self.arms_root, "E", "authoring"))
        stray = os.path.join(self.arms_root, "E", "authoring", "run-001")
        completed = self.wrapper(stray, "E")
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn("outside this study's tree", completed.stderr)
        self.assertEqual(os.listdir(elsewhere), [])
        self.assertEqual(self.calls_made(), "0")
        # The control, so the guard is not refusing everything: the canonical
        # slot for the arm the driver would name runs to a completed call.
        canonical = self.slot(0)
        completed = self.wrapper(canonical, ENTRIES[0]["arm"])
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(os.path.isfile(os.path.join(canonical, "CALL.json")))

    def test_a_replaced_ancestor_is_refused_before_anything_is_created(self):
        """Round 10, finding 6: resolved BEFORE created, component by component.

        The registered branch named one path and made it with a single
        `mkdir -p`, and `mkdir -p` FOLLOWS a replaced component — so with
        `arms` a symlink out of the study it created the two missing
        descendants under the foreign target, and only then did the physical
        comparison refuse. The wrapper's own comment said the block "creates
        nothing outside the study", which was false of exactly the case the
        comparison exists for. The three components below `$STUDY` are the
        whole of the exposure, and this walks the two the round-9 case cannot
        reach: its link sits at `authoring`, onto a directory that already
        exists, where `mkdir -p` makes nothing whatever the ordering is.

        The assertion that fails against the old ordering and passes against
        this one is `os.listdir(elsewhere) == []`; against the old bytes it
        finds `["E"]` for the first case and `["authoring"]` for the second.
        """
        elsewhere = os.path.join(self.root, "elsewhere-ancestor")
        os.makedirs(elsewhere)
        slot = os.path.join(self.arms_root, "E", "authoring", "run-001")
        # `arms` itself replaced: two directories used to be made out there.
        os.symlink(elsewhere, self.arms_root)
        completed = self.wrapper(slot, "E")
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn("outside this study's tree", completed.stderr)
        self.assertEqual(os.listdir(elsewhere), [])
        self.assertIn("at arms,", completed.stderr)
        self.assertFalse(os.path.exists(slot))
        os.unlink(self.arms_root)
        # …and the arm's own component replaced: one directory, one level down.
        os.makedirs(self.arms_root)
        os.symlink(elsewhere, os.path.join(self.arms_root, "E"))
        completed = self.wrapper(slot, "E")
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn("outside this study's tree", completed.stderr)
        self.assertEqual(os.listdir(elsewhere), [])
        self.assertIn("at E,", completed.stderr)
        self.assertFalse(os.path.exists(slot))
        shutil.rmtree(self.arms_root, ignore_errors=True)
        # A DANGLING link at the last component: absent to `-e` and present to
        # `mkdir`, so the old branch died in `mkdir -p` under `set -e` with no
        # refusal line at all. It is refused by name now, like the slot path
        # one level down.
        os.makedirs(os.path.join(self.arms_root, "E"))
        os.symlink(os.path.join(elsewhere, "gone"),
                   os.path.join(self.arms_root, "E", "authoring"))
        completed = self.wrapper(slot, "E")
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn("refused:", completed.stderr)
        self.assertIn("resolves to nothing at authoring,", completed.stderr)
        self.assertEqual(os.listdir(elsewhere), [])
        self.assertEqual(self.calls_made(), "0")
        # The control, so the descent is not refusing everything: the canonical
        # slot for the arm the driver would name still runs to a completed
        # call, and the descent is what MAKES its three components.
        shutil.rmtree(self.arms_root, ignore_errors=True)
        canonical = self.slot(0)
        completed = self.wrapper(canonical, ENTRIES[0]["arm"])
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(os.path.isfile(os.path.join(canonical, "CALL.json")))

    def test_a_study_outside_a_worktree_refuses_rather_than_degrading(self):
        """The one repair `harness/PORTS.md` registers, asserted rather than
        only written there (round 10, finding 6).

        Study 011 read the repository root with the `rev-parse` nested inside
        the `cd`: a failed one left the substitution empty, `cd ""` succeeded,
        and `GIT_ROOT` silently became the CALLER's directory — so the scratch
        check compared against a directory nobody chose. This study reads the
        toplevel first and refuses an empty one. Production is always in a
        worktree and `standin_study()` runs `git init` for the same reason, so
        this is the only case in the suite that wants the degraded shape, and
        its absence is why this line went two rounds with no test on it.
        """
        outside = fixtures.standin_study(
            os.path.join(self.root, "no-worktree"), WRAPPER,
            os.path.join(STUDY, "harness"), git=False)
        found = subprocess.run(["git", "-C", outside, "rev-parse",
                                "--show-toplevel"],
                               capture_output=True, text=True)
        if found.returncode == 0:
            self.skipTest("this machine's temporary directory is itself inside "
                          "a git worktree (%s), so the shape under test cannot "
                          "be built here" % found.stdout.strip())
        entry = ENTRIES[0]
        slot = os.path.join(outside, "arms", entry["arm"], "authoring",
                            "run-%03d" % entry["slotIndex"])
        completed = self.wrapper(slot, entry["arm"],
                                 script=os.path.join(outside, "transcription",
                                                     "authoring_call.sh"))
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn("is not inside a git worktree", completed.stderr)
        self.assertFalse(os.path.exists(os.path.join(outside, "arms")))
        self.assertEqual(self.calls_made(), "0")

    def test_an_unregistered_interpreter_never_reaches_a_call(self):
        # §2.10 registers the interpreter and the wrapper reads that member
        # before anything is called.
        stub = os.path.join(self.root, "python-stub")
        with open(stub, "w") as handle:
            handle.write('#!/bin/bash\n'
                         'if [[ "$*" == *python_implementation* ]]; then\n'
                         '  echo "PyPy 3.12"\n'
                         '  exit 0\n'
                         'fi\n'
                         'exec %s "$@"\n' % sys.executable)
        os.chmod(stub, 0o755)
        slot = self.slot(0)
        completed = self.wrapper(slot, ENTRIES[0]["arm"],
                                 environment={"PYTHON_BIN": stub})
        self.assertEqual(completed.returncode, 1)
        self.assertIn("not the registered", completed.stderr)
        self.assertFalse(os.path.exists(slot))
        self.assertEqual(self.calls_made(), "0")

    def test_the_slots_are_the_shape_the_scorer_reads(self):
        self.recapture_then_batch()
        for offset in range(BATCH_RUNS - 1):
            for retained in ("CALL.json", "stdout.raw", "stderr.raw",
                             "session.jsonl", "context.json", "completion.txt",
                             "SLOT-MANIFEST.json"):
                self.assertTrue(
                    os.path.isfile(os.path.join(self.slot(offset), retained)),
                    "%s/%s" % (os.path.basename(self.slot(offset)), retained))
        entry = ENTRIES[0]
        call = self.call_record(0)
        self.assertEqual(call["model"], self.pins["codex"]["model"])
        self.assertEqual(call["binarySha256"], self.pins["codex"]["binarySha256"])
        self.assertEqual(call["promptKind"], "registered")
        self.assertEqual(call["pinsSha256"], batch._digest(self.pins_path))
        self.assertEqual(call["goldenSha256"], self.pins["golden"]["sha256"])
        # §2.7's two wrapper stamps: which arm, and which prompt bytes.
        self.assertEqual(call["arm"], entry["arm"])
        self.assertEqual(call["armPromptSha256"],
                         self.pins["arms"][entry["arm"]]["promptSha256"])
        # §2.9's three driver stamps, written before the seal so the seal covers
        # them.
        for member in ("globalIndex", "round", "position", "slotIndex"):
            self.assertEqual(call[member], entry[member], member)
        self.assertTrue(call["homeIsolated"] and call["environmentScrubbed"])
        # C6, credential branch: the isolated home held the .codex directory and
        # the copied credential — recursively, so pollution shows.
        self.assertTrue(call["credentialCopied"])
        self.assertEqual(call["isolatedHomeInventory"], [".codex", ".codex/auth.json"])
        self.assertTrue(call["credentialRemoved"])
        values = call["environmentValues"]
        self.assertNotIn(self.home, values["PATH"])
        self.assertNotIn(os.environ.get("PATH", "@none@"), values["PATH"])
        self.assertTrue(values["PATH"].startswith("/usr/local/sbin:"))
        # TMPDIR is this run's own, under this run's own scratch — not /tmp,
        # which the pinned CLI's sandbox would make writable for every run — and
        # its name carries the ARM as well as the slot.
        self.assertNotEqual(values["TMPDIR"], "/tmp")
        self.assertTrue(values["TMPDIR"].startswith(call["cwd"] + os.sep))
        self.assertIn("s012-authoring-%s-run-%03d" % (entry["arm"], entry["slotIndex"]),
                      values["TMPDIR"])

    def test_a_machine_with_no_operator_credential_still_records_both_branches(self):
        # C6's other branch. Study 011's draft expected an inventory of 0 entries
        # here, a state the wrapper cannot produce, so every slot on a
        # credential-less machine scored isolation-unproven after fifty calls.
        bare = fixtures.write_operator_home(os.path.join(self.root, "bare-home"),
                                            credential=False)
        with mock.patch.dict(os.environ, {"HOME": bare}):
            self.recapture_then_batch(extra=["--runs", "1"])
        call = self.call_record(0)
        self.assertFalse(call["credentialCopied"])
        self.assertFalse(call["credentialRemoved"])
        self.assertEqual(call["isolatedHomeInventory"], [".codex"])

    def test_no_retained_byte_and_no_leftover_carries_the_credential(self):
        self.recapture_then_batch()
        self.assertEqual(self.negative_control(
            os.path.join(self.root, "isolation-negative"),
            pins_path=self.assenting_registry()), 0)
        hits = []
        for root in (self.arms_root, self.captures, self.scratch,
                     os.path.join(self.root, "isolation-negative")):
            for base, _, names in os.walk(root):
                for name in names:
                    path = os.path.join(base, name)
                    if os.path.islink(path):
                        continue
                    with open(path, "rb") as handle:
                        body = handle.read()
                    if fixtures.SENTINEL_TOKEN.encode("utf-8") in body:
                        hits.append(path)
        self.assertEqual(hits, [], "the credential's bytes survived in %r" % hits)
        leftovers = [os.path.join(base, name)
                     for base, _, names in os.walk(self.scratch) for name in names
                     if name == "auth.json"]
        self.assertEqual(leftovers, [])

    def test_a_wrapper_death_after_the_copy_still_removes_the_credential(self):
        # Without a trap, a wrapper killed between the credential copy and the
        # slot seal left the copy under the scratch parent. The stand-in exits 0
        # with a transcript carrying no assistant message, so the wrapper's
        # completion extraction raises under set -e — and the EXIT trap must have
        # removed the copy anyway, however the run ended.
        fixtures.write_plan(self.cli_dir,
                            [{"completion": "ready"}, {"completion": "ready"},
                             {"completion": arm_completion(ENTRIES[0]["arm"]),
                              "no_assistant": True}])
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        self.record_negative_control()
        self.run_batch(["--runs", "1"])   # the run fails; the credential is the
        # outcome under test, not the exit path.
        leftovers = [os.path.join(base, name)
                     for base, _, names in os.walk(self.scratch) for name in names
                     if name == "auth.json"]
        self.assertEqual(leftovers, [], "a wrapper death left the credential copy")
        for root in (self.arms_root, self.scratch):
            for base, _, names in os.walk(root):
                for name in names:
                    path = os.path.join(base, name)
                    if os.path.islink(path):
                        continue
                    with open(path, "rb") as handle:
                        if fixtures.SENTINEL_TOKEN.encode("utf-8") in handle.read():
                            self.fail("credential bytes retained at %r" % path)

    def test_a_signal_during_the_call_still_removes_the_credential(self):
        """The residual Study 011's review found by SIGKILL: an EXIT trap alone
        does not cover a signal. INT, TERM and HUP clean up too — SIGKILL cannot
        be covered by any process, and §2.9 says so rather than claiming
        "however it dies"."""
        import signal
        import time

        fixtures.write_plan(self.cli_dir, [{"completion": "ready", "sleep": 30}])
        slot = self.slot(0)
        environment = dict(os.environ)
        environment["PYTHON_BIN"] = sys.executable
        process = subprocess.Popen(
            ["bash", self.wrapper_path, self.scratch, slot, self.pins_path,
             ENTRIES[0]["arm"],
             os.path.join(STUDY, "arms", ENTRIES[0]["arm"], "PROMPT.txt"),
             self.cli],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment,
            start_new_session=True)
        self.addCleanup(process.wait)
        try:
            copies = []
            deadline = time.time() + 30
            while time.time() < deadline and not copies:
                copies = [os.path.join(base, name)
                          for base, _, names in os.walk(self.scratch)
                          for name in names if name == "auth.json"]
                if not copies:
                    time.sleep(0.05)
            self.assertTrue(copies, "the wrapper never copied the credential")
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        finally:
            process.wait(timeout=60)
        self.assertNotEqual(process.returncode, 0)
        leftovers = [os.path.join(base, name)
                     for base, _, names in os.walk(self.scratch)
                     for name in names if name == "auth.json"]
        self.assertEqual(leftovers, [], "SIGTERM left the credential copy on disk")

    # --- the §3.2 recapture -------------------------------------------------

    def test_the_recapture_uses_the_probe_prompt_and_agrees_with_itself(self):
        self.assertEqual(self.capture(), 0)
        with open(self.golden) as handle:
            golden = json.load(handle)
        self.assertEqual(golden["capturedFrom"], ["capture-001", "capture-002"])
        self.assertEqual(golden["capturedIn"], "attempt-1")
        self.assertTrue(golden["entries"])
        for name in golden["capturedFrom"]:
            with open(os.path.join(self.attempt(), name, "CALL.json")) as handle:
                call = json.load(handle)
            self.assertEqual(call["promptKind"], "probe")
            self.assertEqual(call["promptSha256"], self.pins["probePrompt"]["sha256"])
            # [D-8]: the capture is made under NO arm, which is what lets one
            # capture serve all five.
            self.assertIsNone(call["arm"])
            self.assertIsNone(call["armPromptSha256"])
        # No arm's prompt ever ran: no capture answered with records.
        for name in golden["capturedFrom"]:
            with open(os.path.join(self.attempt(), name, "completion.txt")) as handle:
                self.assertEqual(handle.read(), "ready")

    def test_a_failed_recapture_is_retried_by_the_same_command_into_attempt_2(self):
        """§3.2 step 3: a recapture that fails may be repeated after the cause is
        fixed, and the repeat lands in its own attempt directory — the same
        command, unchanged, with nothing deleted by hand."""
        fixtures.write_plan(self.cli_dir,
                            [{"completion": "ready"},
                             {"completion": "ready", "exit": 3},
                             {"completion": "ready"}, {"completion": "ready"}])
        self.assertEqual(self.capture(), 1)
        self.assertEqual(sorted(os.listdir(self.captures)), ["attempt-1"])
        with open(os.path.join(self.attempt(1), "capture-002",
                               "REFUSAL.json")) as handle:
            refusal = json.load(handle)
        self.assertEqual(refusal["code"], "call-nonzero-exit")
        self.assertFalse(os.path.exists(self.golden))
        self.assertEqual(self.capture(), 0)
        self.assertEqual(sorted(os.listdir(self.captures)),
                         ["attempt-1", "attempt-2"])
        with open(self.golden) as handle:
            golden = json.load(handle)
        self.assertEqual(golden["capturedIn"], "attempt-2")
        # attempt-1's evidence is still there, unedited: the failure is
        # published, not cleaned up.
        with open(os.path.join(self.attempt(1), "capture-002",
                               "REFUSAL.json")) as handle:
            self.assertEqual(json.load(handle), refusal)

    def test_one_capture_cannot_derive_a_golden(self):
        self.assertEqual(self.capture(extra=["--runs", "1"]), 1)
        self.assertFalse(os.path.exists(self.captures))
        self.assertFalse(os.path.exists(self.golden))

    def test_the_derivation_itself_refuses_a_single_capture_slot(self):
        self.assertEqual(self.capture(), 0)
        lonely = os.path.join(self.root, "one-capture")
        os.makedirs(lonely)
        shutil.copytree(os.path.join(self.attempt(), "capture-001"),
                        os.path.join(lonely, "capture-001"))
        out = os.path.join(self.root, "ONE.json")
        # Even asked for one explicitly: MIN_CAPTURE_SLOTS is a floor.
        for extra in (["--min-slots", "1"], []):
            self.assertEqual(batch.main(["batch.py", "capture-golden",
                                         "--pins", self.pins_path,
                                         "--slots", lonely, "--out", out] + extra), 1)
        self.assertFalse(os.path.exists(out))

    def test_two_agreeing_captures_must_be_two_calls(self):
        # One call retained twice satisfies "at least two agreeing captures" and
        # agrees with itself by construction, having never been shown to
        # reproduce anything.
        self.assertEqual(self.capture(), 0)
        first, second = (batch.capture_identity(os.path.join(self.attempt(), name))
                         for name in ("capture-001", "capture-002"))
        for member, _ in batch.CAPTURE_IDENTITY:
            self.assertNotEqual(first[member], second[member], member)
        duplicated = os.path.join(self.root, "duplicated")
        os.makedirs(duplicated)
        for name in ("capture-001", "capture-002"):
            shutil.copytree(os.path.join(self.attempt(), "capture-001"),
                            os.path.join(duplicated, name))
        out = os.path.join(self.root, "DUPLICATED.json")
        self.assertEqual(batch.main(["batch.py", "capture-golden",
                                     "--pins", self.pins_path,
                                     "--slots", duplicated, "--out", out]), 1)
        self.assertFalse(os.path.exists(out))

    def test_a_capture_that_does_not_reproduce_refuses_the_derivation(self):
        self.assertEqual(self.capture(), 0)
        varying = os.path.join(self.root, "varying")
        shutil.copytree(self.attempt(), varying)
        session = os.path.join(varying, "capture-002", "session.jsonl")
        with open(session) as handle:
            lines = handle.readlines()
        entry = json.loads(lines[1])
        entry["payload"]["content"][0]["text"] += " and one more sentence"
        lines[1] = json.dumps(entry) + "\n"
        with open(session, "w") as handle:
            handle.writelines(lines)
        out = os.path.join(self.root, "VARYING.json")
        self.assertEqual(batch.main(["batch.py", "capture-golden",
                                     "--pins", self.pins_path,
                                     "--slots", varying, "--out", out]), 1)
        self.assertFalse(os.path.exists(out))

    def test_a_derivation_from_registered_prompt_captures_refuses(self):
        """§3.2 step 2: the capture is derived from PROBE calls, and a slot's
        NAME is not evidence of which prompt it answered."""
        self.recapture_then_batch(extra=["--runs", "2"])
        renamed = os.path.join(self.root, "renamed-captures")
        os.makedirs(renamed)
        for index in range(2):
            shutil.copytree(self.slot(index),
                            os.path.join(renamed, "capture-%03d" % (index + 1)))
        out = os.path.join(self.root, "RENAMED.json")
        self.assertEqual(batch.main(["batch.py", "capture-golden",
                                     "--pins", self.pins_path,
                                     "--slots", renamed, "--out", out]), 1)
        self.assertFalse(os.path.exists(out))

    # --- §6 C7 --------------------------------------------------------------

    def assenting_registry(self) -> str:
        return self.alternate_registry(
            "PINS-assent.json",
            isolationNegative=dict(self.pins["isolationNegative"],
                                   assent="granted"))

    def test_the_isolation_negative_control_fails_the_golden_match_and_keeps_three_files(self):
        # The operator's stand-in home carries a skills tree, which the stand-in
        # CLI puts in the pre-prompt context exactly as Study 010 found the real
        # one doing. The golden was captured from isolated homes, so the
        # comparison must refuse — and the control must REACH the comparison.
        leaky = fixtures.write_operator_home(os.path.join(self.root, "leaky"),
                                             skills=True)
        stale = os.path.join(leaky, ".codex", "sessions")
        os.makedirs(stale)
        with open(os.path.join(stale, "rollout-old.jsonl"), "w") as handle:
            handle.write("{}\n")            # a session that predates the control
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        out = os.path.join(self.root, "isolation-negative")
        with mock.patch.dict(os.environ, {"HOME": leaky}):
            self.assertEqual(self.negative_control(
                out, pins_path=self.assenting_registry()), 0)
        self.assertEqual(sorted(os.listdir(out)),
                         ["CALL.json", "VERDICT.json", "context.json"])
        with open(os.path.join(out, "VERDICT.json")) as handle:
            verdict = json.load(handle)
        self.assertEqual(verdict["outcome"], "refused")
        self.assertEqual(verdict["registeredExpectation"], "the golden match FAILS")
        self.assertIn("session.jsonl", verdict["deletedByCode"])
        # Round 3 finding 4: the retained verdict names the registry member that
        # authorized the call, under the registry's own name for it.
        self.assertEqual(verdict["assent"], "granted")
        with open(os.path.join(out, "CALL.json")) as handle:
            call = json.load(handle)
        for member in batch.C7_REDACTED:
            self.assertNotIn(member, call)
        self.assertEqual(call["isolation"], "operator-home")
        # Every retained byte, inspected: no path into the operator's home, no
        # skill name, no credential.
        for name in sorted(os.listdir(out)):
            with open(os.path.join(out, name), "rb") as handle:
                body = handle.read().decode("utf-8")
            for forbidden in (leaky, fixtures.SENTINEL_SKILL,
                              fixtures.SENTINEL_TOKEN, ".agents"):
                self.assertNotIn(forbidden, body, "%s leaked %r" % (name, forbidden))
        # The raw slot the call was made into is gone, transcript included.
        self.assertEqual([name for name in os.listdir(self.scratch)
                          if name.startswith("s012-c7-raw")], [])

    def test_a_control_that_reaches_neither_comparison_says_so_and_fails(self):
        # `no-context` is a registered outcome, its retention rule is exact, and
        # it exits non-zero because a control that did not run is not a step that
        # was done.
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        fixtures.write_plan(self.cli_dir, [{"completion": "ready",
                                            "no_session": True}])
        out = os.path.join(self.root, "isolation-negative-silent")
        self.assertEqual(self.negative_control(
            out, pins_path=self.assenting_registry()), 1)
        self.assertEqual(sorted(os.listdir(out)), ["CALL.json", "VERDICT.json"])
        with open(os.path.join(out, "VERDICT.json")) as handle:
            verdict = json.load(handle)
        self.assertEqual(verdict["outcome"], "no-context")
        self.assertIn("no-context", verdict["registeredOutcomes"])
        self.assertIn("undemonstrated", verdict["message"])
        self.assertEqual([name for name in os.listdir(self.scratch)
                          if name.startswith("s012-c7-raw")], [])

    def test_a_control_whose_transcript_survives_removal_refuses(self):
        # "Digested and deleted by the driver" is a claim about the disk;
        # rmtree(ignore_errors=True) made it a claim about the call that was
        # made, so the driver could report success with the operator's
        # transcript still on it.
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        out = os.path.join(self.root, "isolation-negative-stuck")
        with mock.patch.object(batch.shutil, "rmtree"):
            self.assertEqual(self.negative_control(
                out, pins_path=self.assenting_registry()), 1)
        leftover = [name for name in os.listdir(self.scratch)
                    if name.startswith("s012-c7-raw")]
        self.assertEqual(len(leftover), 1)
        shutil.rmtree(os.path.join(self.scratch, leftover[0]))

    def test_the_negative_control_runs_on_the_registered_assent_member_only(self):
        """Round 3 finding 4, both ways round: the control refuses while
        `isolationNegative.assent` is null or withheld, and — the half that
        makes it a fix rather than a rename — a registry that grants assent
        under the member the reviewed driver READ (`operatorAssent`) and not
        under the one the registry REGISTERS still refuses."""
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        out = os.path.join(self.root, "isolation-negative")
        for name, member in (("PINS-null.json", {}),
                             ("PINS-withheld.json", {"assent": "withheld"}),
                             ("PINS-old-name.json", {"operatorAssent": "granted"})):
            path = self.alternate_registry(
                name, isolationNegative=dict(self.pins["isolationNegative"],
                                             **member))
            self.assertEqual(self.negative_control(out, pins_path=path), 1, name)
            self.assertFalse(os.path.exists(out), name)
        self.assertEqual(self.negative_control(
            out, pins_path=self.assenting_registry()), 0)

    def test_no_slot_is_created_before_the_isolation_negative_control_has_run(self):
        """Round 9, finding 3: §6 C7 and README step 5 order the control BEFORE
        the batch, and until now that ordering was ceremony — the assent gated
        the control's own command and nothing on the batch path read it or the
        record, so all 150 calls could be spent on a study whose §7 publication
        list promises a control record that was never made.

        Both halves, so this cannot pass for the wrong reason: refused with the
        golden registered and no control, admitted once the control's record is
        on disk."""
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        spent = self.calls_made()
        self.assertEqual(self.run_batch(["--runs", "1"]), 1)
        self.assertFalse(os.path.exists(self.arms_root))
        self.assertEqual(self.calls_made(), spent)
        self.record_negative_control()
        self.assertEqual(self.run_batch(["--runs", "1"]), 0)
        self.assertTrue(os.path.isdir(self.slot(0)))

    def test_a_batch_refuses_while_the_registry_records_no_assent(self):
        """The record without the registry is not the registered step: §6 C7's
        assent is what authorizes the control, and a verdict on disk under a
        registry that grants nothing — or grants it under the pre-round-three
        spelling — leaves the batch refusing, before a call is spent."""
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        self.record_negative_control()
        spent = self.calls_made()
        granted = self.pins["isolationNegative"]
        for name, member in (("PINS-batch-null.json", {"assent": None}),
                             ("PINS-batch-withheld.json", {"assent": "withheld"}),
                             ("PINS-batch-old-name.json",
                              {"assent": None, "operatorAssent": "granted"})):
            path = self.alternate_registry(
                name, isolationNegative=dict(granted, **member))
            self.assertEqual(self.run_batch(["--runs", "1"], pins_path=path),
                             1, name)
            self.assertFalse(os.path.exists(self.arms_root), name)
            self.assertEqual(self.calls_made(), spent, name)
        self.assertEqual(self.run_batch(["--runs", "1"]), 0)

    def test_a_control_record_that_is_not_this_batchs_refuses(self):
        """What the gate reads, case by case: the record must be there, be
        readable as duplicate-free JSON, be an object, carry one of §6 C7's
        THREE registered outcomes, name the assent the registry now records,
        and name the golden capture THIS batch runs behind — and, since round
        10 finding 5, have the SHAPE the writer produces: the registered
        outcome list it was judged against, a name-to-digest `deletedByCode`,
        and an integer `wrapperExit`.

        The last three rows are the point of the second half: `matched` and
        `no-context` ADMIT the batch. `matched` is a registered limitation and
        `no-context` is a control that reached neither comparison and is
        reported as undemonstrated — refusing either here would make that
        registered sentence unreachable, because the command refuses to rewrite
        a record that exists."""
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        self.record_negative_control()
        record = os.path.join(batch.DEFAULT_NEGATIVE, "VERDICT.json")
        other = os.path.join(self.root, "another-golden.json")
        with open(other, "w") as handle:
            handle.write("{}\n")
        spent = self.calls_made()

        def write(body: str) -> None:
            with open(record, "w") as handle:
                handle.write(body)

        for name, damage in (
                ("absent", lambda: os.unlink(record)),
                ("unreadable", lambda: write("{\n")),
                ("duplicate keys",
                 lambda: write('{"outcome": "refused", "outcome": "matched"}')),
                ("not an object", lambda: write('["refused"]')),
                ("no outcome", lambda: write('{"assent": "granted"}')),
                ("unregistered outcome",
                 lambda: self.record_negative_control(outcome="skipped")),
                ("another assent",
                 lambda: self.record_negative_control(assent="withheld")),
                ("another golden",
                 lambda: self.record_negative_control(
                     goldenSha256=batch._digest(other))),
                # Round 10, finding 5: three members the writer always writes,
                # so a record that carries them in another shape is not one the
                # driver produced.
                ("another registration",
                 lambda: self.record_negative_control(
                     registeredOutcomes=["refused", "matched"])),
                ("deletions that are not an object",
                 lambda: self.record_negative_control(
                     deletedByCode=["session.jsonl"])),
                ("a boolean exit status",
                 lambda: self.record_negative_control(wrapperExit=True))):
            damage()
            self.assertEqual(self.run_batch(["--runs", "1"]), 1, name)
            self.assertFalse(os.path.exists(self.arms_root), name)
            self.assertEqual(self.calls_made(), spent, name)
        for outcome, shape in (
                ("matched", {}),
                # …and the no-context record deletes NOTHING, because the
                # wrapper died before it wrote a transcript to digest. That is
                # why the shape check requires `deletedByCode` present and an
                # object and never non-empty: this row is what holds the
                # registered outcome reachable (round 10, finding 5).
                ("no-context", {"deletedByCode": {}})):
            shutil.rmtree(self.arms_root, ignore_errors=True)
            # One plan entry, rewritten rather than counted on: the stand-in
            # CLI clamps to its last step, so slot 1 gets its own arm's
            # completion however many entries the cases above consumed.
            fixtures.write_plan(self.cli_dir,
                                [{"completion": arm_completion(ENTRIES[0]["arm"])}])
            self.record_negative_control(outcome=outcome, **shape)
            self.assertEqual(self.run_batch(["--runs", "1"]), 0, outcome)
            self.assertTrue(os.path.isdir(self.slot(0)), outcome)

    # --- the ledger and the resume [D-22] -----------------------------------

    def test_a_failing_run_is_refused_and_the_batch_continues(self):
        self.recapture_then_batch()
        last = self.slot(BATCH_RUNS - 1)
        with open(os.path.join(last, "REFUSAL.json")) as handle:
            refusal = json.load(handle)
        self.assertEqual(refusal["code"], "call-nonzero-exit")
        self.assertEqual(refusal["wrapperExit"], 10)
        self.assertFalse(os.path.exists(os.path.join(last, "completion.txt")))
        # …and the refused slot is sealed like any other: §2.9's manifest covers
        # every outcome, refusals included, which is why the seal is the
        # driver's and not the wrapper's.
        self.assertTrue(os.path.isfile(os.path.join(last, "SLOT-MANIFEST.json")))
        ledger = self.ledger()
        self.assertEqual([row["code"] for row in ledger["records"]],
                         [None] * (BATCH_RUNS - 1) + ["call-nonzero-exit"])
        self.assertEqual([row["globalIndex"] for row in ledger["records"]],
                         list(range(1, BATCH_RUNS + 1)))
        self.assertEqual([row["arm"] for row in ledger["records"]],
                         [entry["arm"] for entry in ENTRIES[:BATCH_RUNS]])

    def test_a_resumed_batch_merges_the_ledger_rather_than_replacing_it(self):
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        self.record_negative_control()
        self.assertEqual(self.run_batch(["--runs", "2"]), 0)
        first = self.ledger()["records"]
        self.assertEqual(self.run_batch(["--runs", "2", "--resume"]), 0)
        records = self.ledger()["records"]
        self.assertEqual(records[:2], first)
        self.assertEqual([row["globalIndex"] for row in records], [1, 2, 3, 4])
        # §2.9's chain, recomputed over the merged file exactly as the scorer
        # would: a resume that rebuilt the ledger would break it here.
        batch.verify_chain(records)

    def test_a_batch_is_continued_with_resume_and_never_restarted(self):
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        self.record_negative_control()
        # A resume with nothing to resume at: the first invocation of a batch is
        # `run` without it.
        self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 1)
        self.assertFalse(os.path.exists(self.slot(0)))
        self.assertEqual(self.run_batch(["--runs", "2"]), 0)
        before = self.ledger()
        # …and a `run` over a ledger that already records slots refuses rather
        # than restarting: no slot is ever run twice [D-22].
        self.assertEqual(self.run_batch(["--runs", "1"]), 1)
        self.assertEqual(self.ledger(), before)
        self.assertFalse(os.path.exists(self.slot(2)))

    def test_a_resume_without_runs_plans_exactly_the_remaining_order(self):
        """[D-22]: `--runs` omitted runs the registered order to its end from
        wherever the ledger leaves off. Study 011's round-4 blocker was the same
        rule against a count: with `--runs` omitted the driver read the
        registered N as a COUNT and planned a batch past it."""
        self.recapture_then_batch(extra=["--runs", "2"])
        self.assertEqual(self.dry_run_plan(["--resume"]),
                         [os.path.relpath(self.slot(offset), STUDY)
                          for offset in range(2, len(ENTRIES))])

    def test_a_plan_that_would_reach_past_the_registered_order_refuses(self):
        self.recapture_then_batch(extra=["--runs", "2"])
        before = self.ledger()
        spent = self.calls_made()
        for extra in (["--runs", str(len(ENTRIES)), "--resume"],
                      ["--runs", str(len(ENTRIES) + 1), "--resume"],
                      ["--runs", "0", "--resume"]):
            self.assertEqual(self.run_batch(extra), 1, extra)
        # …and the bound does not over-refuse: the plan that ends exactly at the
        # last registered slot is accepted (dry, so this spends no call).
        self.assertEqual(len(self.dry_run_plan(
            ["--runs", str(len(ENTRIES) - 2), "--resume"])), len(ENTRIES) - 2)
        self.assertEqual(self.ledger(), before)
        self.assertEqual(self.calls_made(), spent)

    def test_a_retained_slot_is_never_rewritten(self):
        self.recapture_then_batch(extra=["--runs", "1"])
        # The ledger and the slot are removed from the driver's view of the
        # world, and the slot on disk alone still refuses the batch.
        os.unlink(os.path.join(self.arms_root, "BATCH.json"))
        self.assertEqual(self.run_batch(["--runs", "1"]), 1)
        self.assertTrue(os.path.isdir(self.slot(0)))
        self.assertFalse(os.path.exists(self.slot(1)))

    def test_a_dangling_planned_slot_refuses_through_the_registered_path(self):
        """`os.path.exists()` calls a dangling link absent and `mkdir` calls it
        present, so a resume over one passed preflight, spent no call, and ended
        in an uncaught `FileExistsError` — no registered refusal, and BATCH.json
        left at the earlier runs."""
        self.recapture_then_batch(extra=["--runs", "2"])
        before = self.ledger()
        third = self.slot(2)
        os.makedirs(os.path.dirname(third), exist_ok=True)
        os.symlink(os.path.join(self.arms_root, "no-such-slot"), third)
        self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 1)
        self.assertTrue(os.path.islink(third))
        self.assertFalse(os.path.isdir(third))
        self.assertEqual(self.ledger(), before)
        # The wrapper says the same thing on its own, for a call made by hand.
        completed = self.wrapper(third, ENTRIES[2]["arm"])
        self.assertEqual(completed.returncode, 1)
        self.assertIn("already exists", completed.stderr)

    def test_a_ledger_diverging_from_the_registered_order_refuses_the_resume(self):
        self.recapture_then_batch(extra=["--runs", "2"])
        ledger = self.ledger()
        ledger["records"][1]["arm"] = "A" if ledger["records"][1]["arm"] != "A" else "B"
        with open(os.path.join(self.arms_root, "BATCH.json"), "w") as handle:
            json.dump(ledger, handle, indent=2)
        self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 1)
        self.assertFalse(os.path.exists(self.slot(2)))

    def test_a_physically_reordered_ledger_refuses_rather_than_being_sorted(self):
        """Round 3 finding 16. `load_ledger()` sorted the records by
        `globalIndex` before anything looked at them, so a file whose records had
        been moved passed the prefix check, was resumed into, and was rewritten
        in the order the driver preferred — while `score_rates.py` reads the same
        file in file order and refuses it. File order IS schedule order."""
        self.recapture_then_batch(extra=["--runs", "2"])
        path = os.path.join(self.arms_root, "BATCH.json")
        with open(path, "rb") as handle:
            original = handle.read()
        ledger = json.loads(original.decode("utf-8"))
        reordered = dict(ledger, records=list(reversed(ledger["records"])))
        # The content is untouched: only the order of the records in the FILE
        # moved, which is exactly what the old sort erased.
        self.assertEqual(sorted(reordered["records"],
                                key=lambda row: row["globalIndex"]),
                         ledger["records"])
        with open(path, "w") as handle:
            json.dump(reordered, handle, indent=2)
        with self.assertRaises(batch.BatchError) as caught:
            batch.load_ledger()
        self.assertIn("FILE order", str(caught.exception))
        # …through both registered commands, and neither writes anything.
        self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 1)
        self.assertEqual(self.shortfall(), 1)
        self.assertFalse(os.path.exists(self.slot(2)))
        self.assertFalse(os.path.exists(os.path.join(self.arms_root,
                                                     "SHORTFALL.json")))
        with open(path, "rb") as handle:
            self.assertEqual(json.loads(handle.read().decode("utf-8")), reordered)

    def write_ledger_file(self, body) -> str:
        """`BATCH.json` written by hand, whatever shape `body` is — the state a
        hand-edited or truncated ledger leaves, which the driver has to refuse
        through its own registered path rather than through a traceback."""
        os.makedirs(self.arms_root, exist_ok=True)
        path = os.path.join(self.arms_root, "BATCH.json")
        with open(path, "w") as handle:
            json.dump(body, handle, indent=2)
        return path

    def test_a_ledger_record_naming_another_path_is_not_the_registered_prefix(self):
        """Round 8, finding 5. The prefix check compared §2.8's schedule keys
        and nothing else, and `reconcile_ledger()` asked only that each record's
        `path` be a nonempty string naming something that exists — so a first
        record carrying the registered keys for global index 1 and the path
        `README.md` verified as the prefix, reconciled against a tree in which
        `run-001` was absent, and let `--resume` continue at index 2. The slot at
        index 1 was never made and nothing said so.

        §6 C5 clause 2 puts the ledger and the slot set in bijection "at the path
        the record names", so the path a record names must be the path §2.8
        assigns its (arm, slot index) — derived here from `slot_path()`, the
        function the driver plans and seals with, not matched against a shape.
        """
        entry = ENTRIES[0]
        record = {key: entry[key] for key in batch.SCHEDULE_KEYS}
        record.update({
            "slot": "run-%03d" % entry["slotIndex"],
            "path": "README.md",
            "wrapperExit": 0, "code": None,
            "manifestSha256": batch._digest(os.path.join(STUDY, "README.md")),
            "previousSha256": None,
        })
        self.write_ledger_file({"batchVersion": "3", "records": [record]})
        # Everything the old check looked at is in order: the schedule keys ARE
        # §2.8's for global index 1, the chain verifies over a single record
        # linking to null, and the named path exists in the study tree.
        self.assertEqual({key: record[key] for key in batch.SCHEDULE_KEYS},
                         {key: entry[key] for key in batch.SCHEDULE_KEYS})
        self.assertTrue(os.path.isfile(os.path.join(STUDY, record["path"])))
        self.assertEqual(batch.load_ledger(), [record])
        self.assertFalse(os.path.exists(self.slot(0)))
        with self.assertRaises(batch.BatchError) as caught:
            batch.verify_prefix(batch.load_ledger(), ENTRIES)
        self.assertIn("registered call order", str(caught.exception))
        self.assertIn("README.md", str(caught.exception))
        # …through the registered commands, which spend nothing and make no slot
        # at either index.
        self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 1)
        self.assertEqual(self.shortfall(), 1)
        self.assertEqual(self.calls_made(), "0")
        self.assertFalse(os.path.exists(self.slot(0)))
        self.assertFalse(os.path.exists(self.slot(1)))
        # The control: the canonical path for the same (arm, slot index) is the
        # one the driver derives, and the same ledger verifies with it — so the
        # refusal is the PATH's and not the record's.
        record["path"] = os.path.relpath(batch.slot_path(entry), batch.STUDY)
        self.write_ledger_file({"batchVersion": "3", "records": [record]})
        batch.verify_prefix(batch.load_ledger(), ENTRIES)

    def test_a_malformed_ledger_refuses_through_the_registered_path(self):
        """Round 8, finding 9. `load_ledger()` assumed the decoded top level was
        an object, so a `BATCH.json` holding `[]` reached `.get` on a list and
        raised an `AttributeError` — outside `main()`'s catch, and so a traceback
        where §2.8's resume rule promises malformed population state refuses
        through the driver's own registered path. The top level and the
        `records` member are both type-checked now, and the message names what
        the file actually holds."""
        for body, fragment in (([], "decodes to a JSON list"),
                               ({"records": {}}, "records member is a JSON dict")):
            self.write_ledger_file(body)
            with self.assertRaises(batch.BatchError) as caught:
                batch.load_ledger()
            self.assertIn(fragment, str(caught.exception), repr(body))
            # …and through both registered commands, neither of which writes.
            self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 1,
                             repr(body))
            self.assertEqual(self.shortfall(), 1, repr(body))
            self.assertEqual(self.calls_made(), "0", repr(body))
            self.assertFalse(os.path.exists(self.slot(0)), repr(body))
            self.assertFalse(os.path.exists(os.path.join(self.arms_root,
                                                         "SHORTFALL.json")),
                             repr(body))

    def test_the_withdrawn_flags_refuse_rather_than_being_ignored(self):
        """[D-22] and [D-23] removed `--start`, `--start-round` and `--slots`. A
        command line that still carries one means something else now, and must
        not quietly do something else — on `run` and on `shortfall` alike."""
        self.recapture_then_batch(extra=["--runs", "1"])
        for flag, value in (("--start", "2"), ("--start-round", "2"),
                            ("--slots", self.arms_root)):
            self.assertEqual(self.run_batch(["--runs", "1", "--resume",
                                             flag, value]), 1, flag)
            self.assertEqual(batch.main(["batch.py", "shortfall", "--reason",
                                         "withdrawn flag", "--pins",
                                         self.pins_path, flag, value]), 1, flag)
            self.assertFalse(os.path.exists(os.path.join(self.arms_root,
                                                         "SHORTFALL.json")), flag)
        self.assertFalse(os.path.exists(self.slot(1)))
        # …and the same two commands without the flag still work, so the refusal
        # is the flag's and not the command's.
        self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 0)
        self.assertEqual(self.shortfall(), 0)

    # --- the crash window between the seal and the ledger (round 6, finding 6)

    def truncate_ledger(self, keep: int) -> list:
        """The ledger cut to its first `keep` records, in place — the state a
        kill between `seal_slot()` and the ledger append leaves behind.

        Produced by running the REAL driver and then dropping the tail record,
        so every slot on disk was sealed by the driver itself and the prefix
        that remains is a chain the driver wrote. The dropped records are
        returned, because the recovery's own claim is that it rebuilds them.
        """
        path = os.path.join(self.arms_root, "BATCH.json")
        ledger = self.ledger()
        dropped = ledger["records"][keep:]
        ledger["records"] = ledger["records"][:keep]
        with open(path, "w") as handle:
            json.dump(ledger, handle, indent=2)
        return dropped

    def test_a_sealed_slot_with_no_ledger_record_is_completed_from_its_seal(self):
        """Round 6, finding 6: §2.9 seals a slot and then appends its record, so
        a kill in between leaves a sealed slot the ledger does not name. That
        batch could not be resumed — the resume planned the orphan's index again
        and refused its existing path — and could not be declared short either,
        because the two counts disagreed. It was stuck.

        The slot RAN: the wrapper returned, the refusal record and the schedule
        stamps were written, and the driver sealed the tree, all before the
        append. So the record is completed from the seal rather than re-run, and
        the test's own proof of that is byte equality with the record the driver
        wrote before it was dropped — plus the call counter, which does not move.
        """
        self.recapture_then_batch(extra=["--runs", "3"])
        dropped = self.truncate_ledger(2)
        spent = self.calls_made()
        # …and the resume continues into the next slot in the same invocation.
        self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 0)
        records = self.ledger()["records"]
        self.assertEqual(len(records), 4)
        self.assertEqual(records[2], dropped[0])
        self.assertEqual([row["globalIndex"] for row in records], [1, 2, 3, 4])
        batch.verify_chain(records)
        # One call for the fourth slot, and none for the recovered third.
        self.assertEqual(int(self.calls_made()), int(spent) + 1)

    def test_the_crash_window_recovery_is_one_slot_and_a_verifying_seal(self):
        """The three shapes the recovery refuses instead of guessing at: two
        orphans, an orphan whose tree is not the tree its manifest seals, and an
        orphan with no manifest at all. Each leaves the ledger and the slots
        exactly as it found them and spends no call — a driver that quietly
        adopted any of them would be signing a chain over bytes it never saw.
        """
        self.recapture_then_batch(extra=["--runs", "3"])
        third = self.slot(2)
        # Two orphans: the window can leave one, so this is not that window.
        self.truncate_ledger(1)
        before, spent = self.ledger(), self.calls_made()
        self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 1)
        self.assertEqual(self.ledger(), before)
        self.assertEqual(self.shortfall(), 1)
        self.assertFalse(os.path.exists(os.path.join(self.arms_root,
                                                     "SHORTFALL.json")))
        # One orphan, and its seal does not recompute: a byte of the slot moved
        # after the manifest was written, which §2.9 makes the batch's problem.
        self.truncate_ledger(2)
        with open(os.path.join(third, "stderr.raw"), "ab") as handle:
            handle.write(b"appended after the seal\n")
        before = self.ledger()
        self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 1)
        self.assertEqual(self.ledger(), before)
        # One orphan with no seal at all: the wrapper never returned, so the
        # slot did not reach a terminal outcome and no record describes it.
        os.unlink(os.path.join(third, "SLOT-MANIFEST.json"))
        self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 1)
        self.assertEqual(self.shortfall(), 1)
        self.assertEqual(self.ledger(), before)
        self.assertFalse(os.path.exists(self.slot(3)))
        self.assertEqual(self.calls_made(), spent)

    def test_a_slot_at_an_index_the_order_never_assigns_refuses_the_resume(self):
        """Round 7, finding 4: `--resume` reconciles against the slots PRESENT,
        not against the canonical paths §2.8 would name next.

        A `run-099` is not a path the registered order ever assigns, so the
        reconciliation never looked at it: the resume planned the remaining
        order and SPENT CALLS over a population C5 rule 4 would then refuse to
        score, and the operator found out afterwards. The `shortfall` command
        already refused it — the same disagreement, caught on one path and not
        the other — and that asymmetry is what this closes.
        """
        self.recapture_then_batch(extra=["--runs", "2"])
        before, spent = self.ledger(), self.calls_made()
        stray = os.path.join(self.arms_root, ENTRIES[0]["arm"], "authoring",
                             "run-099")
        os.makedirs(stray)
        self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 1)
        self.assertEqual(self.ledger(), before)
        self.assertEqual(self.calls_made(), spent, "no call is spent")
        self.assertFalse(os.path.exists(self.slot(2)))
        # …and with it gone the same command runs, so the refusal is the stray
        # slot's and not the command's.
        os.rmdir(stray)
        self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 0)
        self.assertEqual(len(self.ledger()["records"]), 3)
        self.assertEqual(int(self.calls_made()), int(spent) + 1)

    def test_an_orphan_whose_seal_is_not_readable_json_refuses(self):
        """Round 7, finding 4, second half: a `SLOT-MANIFEST.json` that is not
        readable JSON is a REFUSAL, not a decoding traceback.

        The orphan's seal is loaded through the duplicate-key-rejecting loader,
        whose `ValueError` used to escape `reconcile_ledger()` uncaught — so a
        slot interrupted mid-seal-write ended the resume and the shortfall in a
        traceback, where §2.9 makes an unverifiable seal a refusal that names
        the slot. Both spellings are checked: a truncated file and a manifest
        whose members are shadowed by a duplicate key, which is a file that
        parses in one reader and not in another.
        """
        self.recapture_then_batch(extra=["--runs", "3"])
        third = self.slot(2)
        manifest = os.path.join(third, "SLOT-MANIFEST.json")
        with open(manifest) as handle:
            sealed = handle.read()
        self.truncate_ledger(2)
        before, spent = self.ledger(), self.calls_made()
        for body in (sealed[:len(sealed) // 2],
                     '{"slot": "run-003", "slot": "run-003"}'):
            with open(manifest, "w") as handle:
                handle.write(body)
            captured = io.StringIO()
            with contextlib.redirect_stderr(captured):
                self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 1)
            self.assertIn("refused: ", captured.getvalue())
            self.assertIn("SLOT-MANIFEST.json", captured.getvalue())
            self.assertEqual(self.ledger(), before)
            self.assertEqual(self.calls_made(), spent)
        # The seal put back, the same resume completes the record it names: the
        # refusal was the unreadable file's, not the recovery's.
        with open(manifest, "w") as handle:
            handle.write(sealed)
        self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 0)
        self.assertEqual(len(self.ledger()["records"]), 4)

    def test_a_shortfall_over_a_crash_window_reconciles_before_it_declares(self):
        """The declaration is a statement about the ledger and about the slots
        on disk at once (§6 C5 rule 5), and a batch killed in the seal-then-
        record window is exactly the batch that needs one. It used to count the
        two separately and write a declaration the scorer refused; now the one
        interrupted append is completed first, by the same function the resume
        uses, and the declared prefix is the reconciled ledger's.
        """
        self.recapture_then_batch(extra=["--runs", "3"])
        dropped = self.truncate_ledger(2)
        spent = self.calls_made()
        self.assertEqual(self.shortfall(), 0)
        records = self.ledger()["records"]
        self.assertEqual(len(records), 3)
        self.assertEqual(records[2], dropped[0])
        batch.verify_chain(records)
        declared = self.declaration()
        # The two numbers that used to disagree, and the member the scorer
        # compares them on.
        self.assertEqual(declared["completedThroughGlobalIndex"],
                         records[-1]["globalIndex"])
        self.assertEqual(declared["completedSlots"], len(records))
        self.assertEqual(declared["lastSlot"], records[-1]["path"])
        self.assertEqual(self.calls_made(), spent)

    def test_a_shortfall_refuses_when_the_slots_and_the_ledger_disagree(self):
        """The reconciliation's other half: a slot on disk the ledger does not
        name and the seal-then-record window cannot explain — here an index
        §2.8's registered order never assigns to that arm.

        The count is the SCORER's own (`collect_slots()` counts an entry named
        run-NNN whatever it holds), so the declaration cannot be written over a
        population the scoring will then refuse under C5, and the driver says
        which two numbers disagree instead of publishing both.
        """
        self.recapture_then_batch(extra=["--runs", "2"])
        stray = os.path.join(self.arms_root, ENTRIES[0]["arm"], "authoring",
                             "run-099")
        os.makedirs(stray)
        declaration = os.path.join(self.arms_root, "SHORTFALL.json")
        self.assertEqual(self.shortfall(), 1)
        self.assertFalse(os.path.exists(declaration))
        self.assertEqual(len(self.ledger()["records"]), 2)
        # …and with it gone the same command declares, so the refusal is the
        # disagreement's and not the command's.
        os.rmdir(stray)
        self.assertEqual(self.shortfall(), 0)
        self.assertEqual(self.declaration()["completedSlots"], 2)

    def test_the_ledger_is_replaced_whole_and_never_written_in_place(self):
        """The other half of finding 6: `BATCH.json` is rewritten in full after
        every slot, and a kill during that write used to be able to truncate it
        — losing the only record of every slot that ran before. The write goes
        to a temporary file in the same directory and is renamed over the
        ledger, so a reader sees one whole version or the other and never a
        partial one, and no `.partial` file is left behind.
        """
        self.recapture_then_batch(extra=["--runs", "2"])
        arms_root = self.arms_root
        path = os.path.join(arms_root, "BATCH.json")
        first = os.stat(path)
        self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 0)
        second = os.stat(path)
        # A rename puts a NEW inode at the name; an in-place rewrite keeps it.
        self.assertNotEqual(first.st_ino, second.st_ino)
        self.assertEqual(second.st_mode & 0o777, 0o644)
        self.assertEqual([name for name in os.listdir(arms_root)
                          if name.startswith("BATCH.json")], ["BATCH.json"])
        self.assertEqual(len(self.ledger()["records"]), 3)

    # --- the shortfall declaration (round 3 finding 15) ---------------------

    def test_a_whole_round_is_declared_as_one_completed_round(self):
        self.recapture_then_batch()
        self.assertEqual(self.shortfall(), 0)
        declared = self.declaration()
        self.assertEqual(declared["completedRounds"], 1)
        self.assertEqual(declared["completedThroughGlobalIndex"], BATCH_RUNS)
        self.assertEqual(declared["completedSlots"], BATCH_RUNS)
        self.assertEqual(declared["registeredRounds"], batch.ROUNDS)
        last = self.slot(BATCH_RUNS - 1)
        self.assertEqual(declared["lastSlot"],
                         os.path.relpath(last, STUDY))
        self.assertEqual(declared["lastSlotEndedAt"],
                         self.call_record(BATCH_RUNS - 1)["endedAt"])
        self.assertEqual(declared["lastSlotEndedAtFrom"], declared["lastSlot"])

    def test_a_prefix_ending_inside_round_one_declares_no_completed_round(self):
        """Round 3 finding 15: the count was the LAST SLOT's round, so a batch
        that died three slots into round 1 declared one round completed — and
        §2.8's headline would have reported a round that never finished."""
        self.recapture_then_batch(extra=["--runs", "3"])
        self.assertEqual(self.shortfall(), 0)
        declared = self.declaration()
        self.assertEqual(declared["completedRounds"], 0)
        self.assertEqual(declared["completedThroughGlobalIndex"], 3)
        self.assertEqual(declared["completedSlots"], 3)
        # Three of the round's five slots ran: the prefix is inside round 1, and
        # the two remaining arms of that round were never called.
        self.assertEqual(batch.POSITIONS, 5)
        self.assertEqual(len([entry for entry in ENTRIES[:3]
                              if entry["round"] == 1]), 3)

    def test_a_tail_with_no_call_json_falls_back_to_the_last_slot_that_has_one(self):
        """Finding 15's other half, produced honestly rather than simulated: the
        wrapper writes `CALL.json` after the call returns, so a slot whose
        wrapper refused at its own preflight has a `REFUSAL.json` and no
        `CALL.json` — and no clock. The stand-in CLI's reported version is
        drifted between two `--runs 1` invocations, which is a wrapper-side
        preflight refusal and nothing the driver stands in for.
        """
        self.recapture_then_batch(extra=["--runs", "1"])
        fixtures.write_cli_version(self.cli_dir, "codex-cli 0.145.0-drifted")
        self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 0)
        refused = self.slot(1)
        self.assertFalse(os.path.exists(os.path.join(refused, "CALL.json")))
        with open(os.path.join(refused, "REFUSAL.json")) as handle:
            self.assertEqual(json.load(handle)["code"], "preflight-refused")
        self.assertEqual(self.shortfall(), 0)
        declared = self.declaration()
        self.assertEqual(declared["completedRounds"], 0)
        self.assertEqual(declared["completedThroughGlobalIndex"], 2)
        self.assertEqual(declared["lastSlot"], os.path.relpath(refused, STUDY))
        # The clock is the one slot that HAS one, and the declaration says which.
        self.assertEqual(declared["lastSlotEndedAt"],
                         self.call_record(0)["endedAt"])
        self.assertEqual(declared["lastSlotEndedAtFrom"],
                         os.path.relpath(self.slot(0), STUDY))
        self.assertNotEqual(declared["lastSlotEndedAtFrom"], declared["lastSlot"])
        self.assertIn("falls back", declared["note"])

    def test_a_prefix_with_no_clock_at_all_declares_null_and_says_why(self):
        """The floor of finding 15's fallback: when NO slot of the prefix has a
        `CALL.json`, there is no clock to publish and the declaration says so in
        its own note rather than leaving a bare null. The shortfall is still
        declared — a batch whose first slot the wrapper refused is exactly the
        batch that needs one."""
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        self.record_negative_control()
        fixtures.write_cli_version(self.cli_dir, "codex-cli 0.145.0-drifted")
        self.assertEqual(self.run_batch(["--runs", "1"]), 0)
        self.assertFalse(os.path.exists(os.path.join(self.slot(0), "CALL.json")))
        self.assertEqual(self.shortfall(), 0)
        declared = self.declaration()
        self.assertEqual(declared["completedRounds"], 0)
        self.assertEqual(declared["completedThroughGlobalIndex"], 1)
        self.assertIsNone(declared["lastSlotEndedAt"])
        self.assertIsNone(declared["lastSlotEndedAtFrom"])
        self.assertIn("both are null when no slot of the prefix carries a "
                      "timestamp", declared["note"])

    def test_a_shortfall_may_not_be_declared_over_a_batch_that_is_not_short(self):
        """§2.8: `batch.py shortfall` refuses when the slots present are not
        fewer than the registered plan. A full batch and a declaration cannot
        coexist — the scorer requires the declared prefix to equal the slots
        present, and a declaration over a full batch would be a claim that the
        study stopped early when it did not."""
        self.recapture_then_batch(extra=["--runs", "1"])
        # The remaining 149 slot paths of the registered order, present on disk.
        # `score_rates.collect_slots()` — the rule the driver counts by, rather
        # than a second definition of the population — counts an entry named
        # run-NNN whatever it holds.
        for entry in ENTRIES[1:]:
            os.makedirs(os.path.join(self.arms_root, entry["arm"], "authoring",
                                     "run-%03d" % entry["slotIndex"]))
        self.assertEqual(self.shortfall(), 1)
        self.assertFalse(os.path.exists(os.path.join(self.arms_root,
                                                     "SHORTFALL.json")))

    def test_a_shortfall_is_declared_once_and_names_a_reason(self):
        self.recapture_then_batch(extra=["--runs", "2"])
        self.assertEqual(batch.main(["batch.py", "shortfall", "--pins",
                                     self.pins_path]), 1)
        self.assertFalse(os.path.exists(os.path.join(self.arms_root,
                                                     "SHORTFALL.json")))
        self.assertEqual(self.shortfall("the operator stopped the batch"), 0)
        self.assertEqual(self.declaration()["reason"],
                         "the operator stopped the batch")
        self.assertEqual(self.shortfall(), 1)

    def test_a_batch_that_never_reached_a_slot_declares_the_empty_prefix(self):
        """§2.8 [D-21] over the ZERO prefix (round 9, finding 4): "any
        incomplete batch, at any round, for any reason, is descriptive-only",
        and a batch that died before its first slot finished is one.

        The tree that leaves is the one this case asserts: no authoring root
        anywhere, because the driver makes an arm's root with that arm's first
        slot, and no `BATCH.json`, because the driver writes the ledger inside
        the run loop. The scorer used to refuse both, so the likeliest place
        for a batch to die had no registered way to publish.

        `arms/` is made here rather than in `declare_shortfall`: in the real
        tree it is tracked and always exists, and this class's population root
        is created by `run`. The driver is left alone.
        """
        os.makedirs(self.arms_root)
        self.assertEqual(self.shortfall("the operator stopped the batch before "
                                        "its first slot returned"), 0)
        declared = self.declaration()
        self.assertEqual(declared["completedRounds"], 0)
        self.assertEqual(declared["completedThroughGlobalIndex"], 0)
        self.assertEqual(declared["completedSlots"], 0)
        self.assertIsNone(declared["lastSlot"])
        self.assertIsNone(declared["lastSlotEndedAt"])
        self.assertIsNone(declared["lastSlotEndedAtFrom"])
        self.assertFalse(os.path.exists(os.path.join(self.arms_root, "BATCH.json")))
        for arm in score_rates.ARMS:
            self.assertFalse(os.path.exists(
                score_rates.slots_root(self.arms_root, arm)), arm)
        # …and the scorer's own reader admits exactly this declaration, so the
        # driver's bytes and the relaxation are held together rather than each
        # being asserted against a hand-written copy of the other.
        self.assertTrue(score_rates._declares_no_slot_ran(declared))
        self.assertEqual(score_rates.load_ledger(self.arms_root, declared, 0), [])

    def test_a_prefix_inside_round_one_leaves_the_unreached_arms_no_root(self):
        """The other half of finding 4, driver-side: a prefix that stops inside
        round 1 leaves the arms it never called with no `authoring/` root at
        all, and the declaration it writes is the one the scorer reads over
        that tree.

        Round 1 is B, C, A, D, E, so three runs reach B, C and A and leave D
        and E untouched. `collect_slots()` reads those two as empty populations
        and C5 rule 4 validates them against this declaration's prefix.
        """
        self.recapture_then_batch(extra=["--runs", "3"])
        self.assertEqual(self.shortfall(), 0)
        declared = self.declaration()
        self.assertEqual(declared["completedRounds"], 0)
        self.assertEqual(declared["completedThroughGlobalIndex"], 3)
        self.assertEqual(declared["completedSlots"], 3)
        self.assertEqual(declared["lastSlot"],
                         os.path.relpath(self.slot(2), STUDY))
        reached = {entry["arm"] for entry in ENTRIES[:3]}
        self.assertEqual(reached, {"A", "B", "C"})
        for arm in score_rates.ARMS:
            root = score_rates.slots_root(self.arms_root, arm)
            self.assertEqual(os.path.isdir(root), arm in reached, arm)
            if arm not in reached:
                self.assertEqual(score_rates.collect_slots(root), ([], []))

    def test_the_declaration_the_driver_writes_carries_the_members_it_registers(self):
        """The parity `test_admission.py` states over the SOURCE, stated here
        over the bytes: `score_rates.check_population()` reads these members off
        a real declaration written by the real driver."""
        self.recapture_then_batch(extra=["--runs", "2"])
        self.assertEqual(self.shortfall(), 0)
        declared = self.declaration()
        for member in ("completedThroughGlobalIndex", "lastSlot", "completedSlots"):
            self.assertIn(member, declared)
        ledger = self.ledger()["records"]
        self.assertEqual(declared["completedThroughGlobalIndex"],
                         ledger[-1]["globalIndex"])
        self.assertEqual(declared["lastSlot"], ledger[-1]["path"])
        self.assertEqual(declared["completedSlots"], len(ledger))


class ImportDiscipline(unittest.TestCase):
    """The gate runs before the grid loads — probed in a fresh interpreter
    (round 7, finding 1; round 8, finding 1).

    §2.10's bytecode gate inspects the compiled cache of every ported source
    before the harness relies on it, and a module already imported is a module
    whose cache has already executed: the gate would be reading bytes that had
    had their turn. Round 7 deferred `score_rates.py`'s own `import
    policy_mirror` for that reason — and left `import census` eager one line
    above it, while `census.py` imported the mirror at its top. `import batch`
    therefore still executed the mirror before any gate ran, and the lazy
    wrapper closed nothing. Round 8, finding 4 of the same shape: a chain of
    imports is only as deferred as its eagerest link.

    Nothing in the running test process can say what an import DOES, because the
    modules are already imported here — `conftest.py` puts the harness on
    `sys.path` and this file imports `batch` at its top. Every case below
    therefore runs a FRESH interpreter and reads `sys.modules` inside it.
    """

    HARNESS = os.path.join(STUDY, "harness")

    def probe(self, body: str):
        """One fresh interpreter, running `body` with the harness importable and
        no bytecode written beside the reviewed sources (§2.10 refuses on a
        cache), returning the JSON its last line printed."""
        source = "import json, sys\nsys.path.insert(0, %r)\n%s" % (self.HARNESS,
                                                                   body)
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        environment.pop("PYTHONPATH", None)
        completed = subprocess.run([sys.executable, "-c", source],
                                   capture_output=True, text=True,
                                   env=environment, cwd=STUDY)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_importing_the_driver_does_not_import_the_mirror_or_the_census(self):
        loaded = self.probe(
            "import batch\n"
            "print(json.dumps({name: name in sys.modules for name in "
            "('integrity', 'score_rates', 'census', 'policy_mirror')}))\n")
        # The gate's own module IS loaded: the point is the ORDER, not that
        # importing the driver imports nothing.
        self.assertTrue(loaded["integrity"])
        self.assertTrue(loaded["score_rates"])
        self.assertFalse(loaded["census"], "census loaded before the gate")
        self.assertFalse(loaded["policy_mirror"],
                         "the mirror loaded before the gate")

    def test_importing_the_census_does_not_import_the_mirror(self):
        """The link round 7 left eager. `census.py` is a grid module that used
        `policy_mirror` at its top, so every importer of it — the scorer, and
        the driver through the scorer — pulled the mirror in with it."""
        loaded = self.probe(
            "import census\n"
            "print(json.dumps({name: name in sys.modules for name in "
            "('census', 'policy_mirror')}))\n")
        self.assertTrue(loaded["census"])
        self.assertFalse(loaded["policy_mirror"])

    def test_the_mirror_is_still_absent_when_the_gate_itself_runs(self):
        """The registered claim is about a MOMENT, so the probe reads
        `sys.modules` at that moment: `batch.verify_ported_bytes()` is where
        `integrity.verify()` is called, one statement into `preflight()`. The
        gate is stubbed to refuse, so the probe spends nothing and leaves no
        slot — what is asserted is what was loaded when it was entered."""
        loaded = self.probe(
            "import batch\n"
            "seen = {}\n"
            "def recording(*args, **kwargs):\n"
            "    seen['atGate'] = sorted(name for name in ('census', 'policy_mirror')\n"
            "                            if name in sys.modules)\n"
            "    raise batch.integrity.IntegrityError('probe')\n"
            "batch.integrity.verify = recording\n"
            "try:\n"
            "    batch.verify_ported_bytes()\n"
            "except batch.BatchError:\n"
            "    pass\n"
            "print(json.dumps(seen))\n")
        self.assertEqual(loaded, {"atGate": []})

    def test_the_deferral_is_a_deferral_and_not_a_removal(self):
        """Both modules still load, through the wrappers that defer them: a
        `_census()` that had stopped resolving would make every case above pass
        and the census disappear from `RESULTS.json`."""
        loaded = self.probe(
            "import score_rates\n"
            "before = sorted(name for name in ('census', 'policy_mirror')\n"
            "                if name in sys.modules)\n"
            "names = [score_rates._census().__name__,\n"
            "         score_rates._policy_mirror().__name__]\n"
            "after = sorted(name for name in ('census', 'policy_mirror')\n"
            "               if name in sys.modules)\n"
            "print(json.dumps({'before': before, 'names': names, 'after': after}))\n")
        self.assertEqual(loaded, {"before": [],
                                  "names": ["census", "policy_mirror"],
                                  "after": ["census", "policy_mirror"]})


class EntryFileOrdering(unittest.TestCase):
    """The untracked-source tripwire runs before the FIRST study-local import,
    not merely before most of them (round 8, finding 2; round 9, finding 1).
    `ImportDiscipline` above asks WHAT an import pulls in; this asks WHEN the
    scan happens relative to the first one.

    Round 10, finding 1: there is one thing no in-file ordering can reach — the
    entry file's OWN head imports, which resolve from the directory the file was
    invoked from before a byte of it runs. `-P`/`PYTHONSAFEPATH=1` is the
    closure, the three entry files refuse without it, and the last case below is
    the refusal's own test."""

    ENTRIES = ("batch.py", "score_rates.py")
    # README step 1 invokes a third entry by path, and the safe-path refusal is
    # in all three: `integrity.py` has no tripwire of its own, but it does
    # `sys.path.insert(0, HERE)` at module scope with no scan before it.
    PATH_INVOKED = ENTRIES + ("integrity.py",)

    def _sandbox(self, entry):
        """A throwaway git repo holding ONLY the reviewed entry file, so a scan
        that runs late dies on the absent `integrity` instead."""
        root = fixtures.throwaway_root()
        self.addCleanup(shutil.rmtree, root, True)
        harness = os.path.join(root, "harness")
        os.makedirs(harness)
        shutil.copy(os.path.join(STUDY, "harness", entry), harness)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "add", "harness/" + entry], cwd=root, check=True)
        return root, harness            # `git add` is enough: ls-files reads the index

    def _run(self, root, harness, entry, *argv, safe_path=True):
        """The ceremony's own invocation shape: the file by path, under the
        safe import path README step 0 exports. `safe_path=False` is the
        operator who forgot, which the entries refuse."""
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                           PYTHONSAFEPATH="1")
        environment.pop("PYTHONPATH", None)
        if not safe_path:
            environment.pop("PYTHONSAFEPATH")
        return subprocess.run([sys.executable, os.path.join(harness, entry)] + list(argv),
                              capture_output=True, text=True, cwd=root, env=environment)

    def test_an_untracked_source_is_refused_before_the_first_harness_import(self):
        for entry in self.ENTRIES:
            with self.subTest(entry=entry):
                root, harness = self._sandbox(entry)
                with open(os.path.join(harness, "planted.py"), "w") as handle:
                    handle.write("VALUE = 1\n")
                done = self._run(root, harness, entry, "run")
                self.assertEqual(done.returncode, 2, done.stderr)
                self.assertIn("untracked Python source", done.stderr)
                self.assertIn("planted.py", done.stderr)
                # The sandbox has no integrity.py: a scan that ran after the
                # import would have died here instead of refusing.
                self.assertNotIn("ModuleNotFoundError", done.stderr)

    def test_the_clean_tree_gets_past_the_scan(self):
        """The control: without the planted file the scan must NOT refuse — the
        process goes on to fail on the module the sandbox omits, which is how we
        know case one refused for the reason it names."""
        for entry in self.ENTRIES:
            with self.subTest(entry=entry):
                root, harness = self._sandbox(entry)
                done = self._run(root, harness, entry, "run")
                self.assertNotEqual(done.returncode, 2, done.stderr)
                self.assertIn("ModuleNotFoundError", done.stderr)

    def _local_import_lines(self, tree, local):
        """The module-scope lines importing one of `local`, in BOTH import
        forms (round 10, finding 1). `import integrity` and `from integrity
        import verify` put the same module on the same path at the same moment,
        and a scan that counted only the first form was a guard against one
        spelling of the thing it exists to order."""
        return [node.lineno for node in tree.body
                if (isinstance(node, ast.Import)
                    and any(alias.name in local for alias in node.names))
                or (isinstance(node, ast.ImportFrom)
                    and node.level == 0 and node.module in local)]

    def test_bytecode_writing_is_disabled_before_the_first_harness_import(self):
        """No clean runtime probe exists for the flag (the cache write it
        prevents happens inside the import machinery), so this one is over the
        source: the assignment and the guarded scan both precede every
        module-level import of a harness module, and the harness module set is
        derived from the directory so a new module is covered on sight."""
        harness_dir = os.path.join(STUDY, "harness")
        modules = {name[:-3] for name in os.listdir(harness_dir)
                   if name.endswith(".py")}
        for entry in self.ENTRIES:
            with self.subTest(entry=entry):
                with open(os.path.join(harness_dir, entry)) as handle:
                    tree = ast.parse(handle.read())
                # `min()` over an empty sequence raises, which is the right
                # behaviour: an entry file that imports no harness module at
                # module scope has changed shape and this case must say so
                # rather than pass over nothing.
                first_local = min(self._local_import_lines(
                    tree, modules - {entry[:-3]}))
                flag = [node.lineno for node in tree.body
                        if isinstance(node, ast.Assign)
                        and ast.unparse(node) == "sys.dont_write_bytecode = True"]
                guard = [node.lineno for node in tree.body
                         if isinstance(node, ast.If)
                         and "_refuse_untracked_python_sources()" in ast.unparse(node)]
                self.assertTrue(flag, "%s disables no bytecode writing" % entry)
                self.assertLess(flag[0], first_local, entry)
                self.assertTrue(guard, "%s runs no scan as a script" % entry)
                self.assertLess(guard[0], first_local, entry)

    def test_the_third_path_invoked_entry_gates_before_it_loads_anything(self):
        """README step 1 runs `integrity.py` by path. It carries no tripwire of
        its own because it needs none: its head imports nothing study-local, and
        its scan is the first statement of `verify()`.

        The emptiness assertion is the one that had to grow both import forms
        (round 10, finding 1): an emptiness assertion is satisfied by anything
        it cannot see, so `from policy_mirror import ...` at module scope here
        would have left this passing with a grid module loaded above the gate."""
        with open(os.path.join(STUDY, "harness", "integrity.py")) as handle:
            tree = ast.parse(handle.read())
        verify = next(node for node in tree.body
                      if isinstance(node, ast.FunctionDef) and node.name == "verify")
        self.assertEqual(ast.unparse(verify.body[1]), "verify_bytecode(study)")   # body[0] is the docstring
        modules = {name[:-3] for name in os.listdir(os.path.join(STUDY, "harness"))
                   if name.endswith(".py")} - {"integrity"}
        self.assertEqual([], self._local_import_lines(tree, modules))

    def test_every_path_invoked_entry_refuses_without_the_safe_import_path(self):
        """Round 10, finding 1: the residual the tripwire cannot reach.

        Invoking a script by path makes its own directory `sys.path[0]`, so the
        entry file's head imports — `subprocess`, which the scan asks git what
        is tracked with, among them — resolve from the directory the scan
        polices before any of the file runs. `-P`/`PYTHONSAFEPATH=1` is the
        closure and README step 0 exports it; each entry refuses without it,
        BEFORE its own scan, which is what the planted file proves: the flag is
        named and the untracked source is not, because the process stopped
        above it.

        This is a discipline check against operator error and not a gate
        against a hostile tree — it runs after the head imports it is about —
        and the code says so where it lives.
        """
        for entry in self.PATH_INVOKED:
            with self.subTest(entry=entry):
                root, harness = self._sandbox(entry)
                with open(os.path.join(harness, "planted.py"), "w") as handle:
                    handle.write("VALUE = 1\n")
                done = self._run(root, harness, entry, "run", safe_path=False)
                self.assertEqual(done.returncode, 2, done.stderr)
                self.assertIn("PYTHONSAFEPATH", done.stderr)
                self.assertNotIn("untracked Python source", done.stderr)
                # …and the control: with the flag the refusal does not fire, so
                # this case cannot pass on an entry that refuses everything.
                done = self._run(root, harness, entry, "run")
                self.assertNotIn("PYTHONSAFEPATH", done.stderr)


class IntervalScope(unittest.TestCase):
    """§4.3's frozen interval scope, walked over a scored population.

    "A harness test walks `RESULTS.json` and requires the set of blocks carrying
    `ci95` to be exactly that list." The list §4.3 registers is: the six primary
    ITT rates per arm and the upper end of each one's sensitivity bound; the six
    per-protocol rates per arm (S11); the raw, Q and Q-only per-class rates (S1,
    S2); the all-six rate (S3); the old-edge cross-scored rates (S10); and the
    pipeline-invalid rate (§4.4). It is NOT computed for the mislabel share,
    whose denominator is neither N nor V_X, nor for any record-level pooled
    quantity, nor for any census count in §4.5.

    The walk is structural — it asks which blocks CARRY the member, not what the
    bounds are — because a block over an empty denominator carries `ci95: null`
    and is still inside the scope. §4.3's arithmetic is pinned separately, by
    `test_verdict_parity.py`'s registered vectors.

    Round 4, finding 8: the walk is EXHAUSTIVE. It used to return at the first
    block carrying `ci95`, so an interval published beneath one — a nested rate
    block under `primary`, say — was invisible to a test whose whole job is to
    say which blocks carry intervals. The assertion below is over every `ci95`
    occurrence in the arm's block, at every depth, and the registered eleven are
    all of them.

    Round 5, finding 8, in two parts. First, a set of PATHS collapses a list to
    one member — `classes[]` is one string however many rows the list holds — so
    the shape check walked `classes[0]` and one compliant row certified all six.
    `blocks_at()` returns every element of every list on a path and the shape is
    asserted over each. Second, §4.3 registers the walk over `RESULTS.json`, not
    over its arm blocks: the scope assertion now starts at the whole published
    object, so every top-level member — `cell`, `schedule`, `seal`, `crossArm`,
    `verdicts`, `census`, `runs` — is inside the claim and an interval published
    anywhere outside the registered eleven fails it.

    Round 7, finding 8: the object walked IS the published one. It was
    `fixtures.Population.score()`, which builds the arm blocks, the verdicts and
    a census keyed by arm — and no `cell`, no `schedule` and no `crossArm` at
    all. So "starts at the whole published object" was true of a smaller object
    than `RESULTS.json`, and an interval published in a member the fixture did
    not build could not fail the walk. `Population.publish()` now calls
    `score_rates.results_document()`, the scorer's own writer, and
    `test_the_walk_covers_every_member_the_writer_publishes` holds the walked
    object's top-level members against the writer's own — read out of the
    source, not kept by hand here — so a member added to `RESULTS.json` is
    inside this claim whether or not anyone remembers this file.
    """

    # Each path is a block that must carry `ci95`, written as it is reached from
    # one arm's block in RESULTS.json. `classes[]` stands for "every one of the
    # six class rows".
    REGISTERED_SCOPE = {
        "population.pipelineInvalidRate",       # §4.4
        "classes[].primary",                    # §4.2, the six ITT rates
        "classes[].sensitivity.lower",          # the primary block itself
        "classes[].sensitivity.upper",          # §4.2's upper end
        "classes[].placement",                  # §4.6 S1's raw rate
        "classes[].rawIntersection",            # the placement block itself
        "classes[].perProtocol",                # §4.6 S11
        "classes[].oldEdge",                    # §4.6 S10
        "classes[].qIntersection",              # §4.6 S1
        "classes[].qOnlyIntersection",          # §4.6 S2
        "coverageBreadth.allSix",               # §4.6 S3
    }

    @classmethod
    def setUpClass(cls):
        with open(REGISTRY) as handle:
            pins = json.load(handle)
        cls.root = fixtures.throwaway_root("s012-scope-")
        population = fixtures.Population(cls.root, STUDY, pins)
        # One round of the registered order — one slot per arm, every one valid.
        # The scope is a property of the published SHAPE, which is the same at
        # five slots as at a hundred and fifty.
        population.build([{} for _ in range(5)])
        cls.results = population.publish()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, True)

    @staticmethod
    def published_members() -> list:
        """The top-level members `score_rates.results_document()` writes, read
        out of its own source (round 7, finding 8).

        The writer's return is one dict literal, so its keys are the published
        members and `ast` can say what they are without running a registered
        scoring — which no test can run, because §2.10's freeze pin is null
        until the freeze. A list kept by hand in this file would agree with the
        writer only until someone changed one of them.
        """
        with open(score_rates.__file__) as handle:
            tree = ast.parse(handle.read())
        for node in ast.walk(tree):
            if not (isinstance(node, ast.FunctionDef)
                    and node.name == "results_document"):
                continue
            returns = [child for child in ast.walk(node)
                       if isinstance(child, ast.Return)]
            assert len(returns) == 1, "the writer returns in one place"
            literal = returns[0].value
            assert isinstance(literal, ast.Dict), "the writer returns a literal"
            return [key.value for key in literal.keys]
        raise AssertionError("score_rates.results_document() was not found")

    def test_the_walk_covers_every_member_the_writer_publishes(self):
        """The walked object carries exactly the top-level members the scorer's
        own writer emits — the whole of `RESULTS.json` and no stand-in for it
        (round 7, finding 8).

        Asserted against the writer's source rather than against a list in this
        file, and both ways round: a member the writer emits and the walked
        object lacks would put that member outside §4.3's claim, and a member
        the walked object carries and the writer does not would mean the walk is
        over something other than what is published.
        """
        published = self.published_members()
        self.assertEqual(sorted(published), sorted(set(published)),
                         "the writer emits each member once")
        self.assertEqual(set(self.results), set(published))
        # Named as well as counted, so a writer that lost `crossArm` and a walk
        # that lost it with it would still fail here.
        self.assertLessEqual({"cell", "schedule", "seal", "arms", "crossArm",
                              "verdicts", "census", "runs"}, set(published))

    def test_the_published_schedule_carries_the_computed_utc_day(self):
        """Round 10, finding 9: §2.8 registers that all 150 slots are begun and
        completed within one UTC calendar day, and nothing computed it.

        `RESULTS.json`'s own `cell` note said "one model, one day" while the
        document carried no member a reader could check it against — and the
        same conjunct is in [D-10]'s confirmation sentence and §9's bounds. The
        date set is published under `schedule.utcDay` now, computed from the
        calendar parts of each slot's own retained stamps.

        Asserted on the WRITER's document rather than on a second scoring, so
        the wiring is what is checked: the fixture population's slots are all
        stamped on one date, and the block says so and establishes it. It
        carries no `ci95` and no rate, which is why §4.3's registered scope
        above is unchanged by it — this is a date, not a measurement.
        """
        block = self.results["schedule"]["utcDay"]
        self.assertEqual(block, score_rates.utc_day(self.results["runs"]))
        self.assertEqual(block["dates"], ["2026-08-07"])
        self.assertEqual(block["slotsWithoutReadableStamps"], 0)
        self.assertIs(block["crossedMidnight"], False)
        self.assertIs(block["oneDayEstablished"], True)
        self.assertIn("rather than a stopping rule", block["note"])
        # Nested inside `schedule`, so the top-level walk above is untouched;
        # named here so a writer that moved it to the root is caught.
        self.assertNotIn("utcDay", set(self.results))

    def blocks_carrying_ci95(self, node, path: str) -> set:
        """Every path at which `ci95` appears, to the bottom of the structure.

        A block that carries the member is recorded AND descended into (round 4,
        finding 8): stopping there would hide any interval published under it,
        which is the one thing this walk exists to see.
        """
        found = set()
        if isinstance(node, dict):
            if "ci95" in node:
                found.add(path)
            for key, value in node.items():
                found |= self.blocks_carrying_ci95(value, "%s.%s" % (path, key)
                                                   if path else key)
        elif isinstance(node, list):
            for value in node:
                found |= self.blocks_carrying_ci95(value, path + "[]")
        return found

    def test_the_walk_does_not_stop_at_the_first_interval(self):
        """The walk itself, on a known answer (round 4, finding 8).

        A block carrying `ci95` with interval-bearing blocks beneath it yields
        every one of those paths. The old walk returned the outer path and
        stopped, so the assertion below was over the outermost layer of the
        published surface rather than over the surface — and a check that has
        never been shown to fire is prose.
        """
        nested = {"outer": {"ci95": [0.0, 1.0], "count": 1,
                            "inner": {"ci95": [0.0, 1.0], "rate": 1.0},
                            "rows": [{"ci95": None}, {"rate": None}]}}
        self.assertEqual(self.blocks_carrying_ci95(nested, ""),
                         {"outer", "outer.inner", "outer.rows[]"})

    def blocks_at(self, node, path: str) -> list:
        """Every node the path names, with EVERY element of every list on the
        way (round 5, finding 8).

        A `classes[]` step used to be read as `classes[0]`, so the shape check
        below asked one of six rows and reported on all of them. The path is a
        set member and cannot distinguish the rows; this returns them all, and
        the caller asserts over each.
        """
        nodes = [node]
        for token in path.split("."):
            stepped = []
            for current in nodes:
                if token.endswith("[]"):
                    stepped.extend(current[token[:-2]])
                else:
                    stepped.append(current[token])
            nodes = stepped
        return nodes

    def test_the_blocks_carrying_an_interval_are_exactly_the_registered_ones(self):
        """Over ALL `ci95` occurrences in the WHOLE published object, at every
        depth: the registered eleven per arm are the whole set (round 5,
        finding 8).

        Walking the arm blocks and the census separately left every other
        top-level member of `RESULTS.json` outside the claim §4.3 registers over
        `RESULTS.json`. This starts at the root, so `crossArm`, `verdicts`,
        `schedule`, `seal`, `cell` and `runs` are inside it too — and the arms
        that carry the eleven are named rather than assumed, because a scoring
        that published four arm blocks would otherwise pass.
        """
        expected = {"arms.%s.%s" % (arm, path)
                    for arm in self.results["arms"]
                    for path in self.REGISTERED_SCOPE}
        self.assertEqual(set(self.results["arms"]), set("ABCDE"))
        self.assertEqual(self.blocks_carrying_ci95(self.results, ""), expected)
        # …and per arm, so a failure names the arm rather than the difference of
        # two 55-member sets.
        for arm, block in self.results["arms"].items():
            self.assertEqual(self.blocks_carrying_ci95(block, ""),
                             self.REGISTERED_SCOPE, arm)

    def test_the_quantities_section_four_three_excludes_carry_none(self):
        """The other half, named rather than left to the set difference: the
        mislabel share, the pooled label accuracy and every census count are
        published WITHOUT an interval, because records within a run share an
        author turn and are not independent trials."""
        for arm, block in self.results["arms"].items():
            for row in block["classes"]:
                self.assertIsInstance(row["mislabelShare"], float)
                self.assertNotIn("ci95", row)
            self.assertNotIn("ci95", block["labelAccuracy"], arm)
            self.assertNotIn("ci95", block["records"], arm)
        # §4.7 publishes the census as a LIST of per-arm blocks, which is what
        # the writer emits and what `census.render_markdown()` reads (round 7,
        # finding 8): the fixture's arm-keyed copy was a second shape.
        census = {block["arm"]: block for block in self.results["census"]}
        self.assertEqual(set(census), set("ABCDE"))
        for arm, block in census.items():
            self.assertEqual(self.blocks_carrying_ci95(block, ""), set(), arm)

    def interval_block_defects(self, block) -> list:
        """[(path, index, what is wrong)] over every element of every list on
        every registered path — the shape check as a value, so the walk itself
        can be held to a known answer below (round 5, finding 8)."""
        defects = []
        for path in sorted(self.REGISTERED_SCOPE):
            for index, node in enumerate(self.blocks_at(block, path)):
                if sorted(node) != ["ci95", "count", "denominator", "rate",
                                    "trials"]:
                    defects.append((path, index, "members are %s" % sorted(node)))
                elif node["denominator"] not in ("N", "V_X"):
                    defects.append((path, index,
                                    "denominator is %r" % node["denominator"]))
        return defects

    def test_every_registered_block_publishes_the_integers_its_bound_is_over(self):
        """No rate without its denominator and no bound a reader cannot
        recompute from the integers (§4.7) — over EVERY class row and not the
        first one (round 5, finding 8)."""
        for arm, block in self.results["arms"].items():
            self.assertEqual(self.interval_block_defects(block), [], arm)
        # The six rows are actually visited: a path with `classes[]` in it
        # yields six nodes, so the assertion above is over six and not over one.
        self.assertEqual(len(self.blocks_at(self.results["arms"]["A"],
                                            "classes[].primary")), 6)

    def test_the_shape_walk_sees_past_element_zero(self):
        """The walk on a known answer: element zero compliant, element three not
        (round 5, finding 8).

        The old walk read `classes[0]` and reported on `classes[]`, so one good
        row certified all six — and this is the probe that would have caught it,
        because a check that has never been shown to fire is prose.
        """
        good = {"ci95": [0.0, 1.0], "count": 1, "denominator": "N",
                "rate": 1.0, "trials": 30}
        rows = [dict(good) for _ in range(6)]
        rows[3] = {key: value for key, value in good.items()
                   if key != "denominator"}
        block = {"population": {"pipelineInvalidRate": dict(good)},
                 "coverageBreadth": {"allSix": dict(good)},
                 "classes": [{"primary": row,
                              "sensitivity": {"lower": dict(good),
                                              "upper": dict(good)},
                              "placement": dict(good),
                              "rawIntersection": dict(good),
                              "perProtocol": dict(good),
                              "oldEdge": dict(good),
                              "qIntersection": dict(good),
                              "qOnlyIntersection": dict(good)}
                             for row in rows]}
        defects = self.interval_block_defects(block)
        self.assertEqual([(path, index) for path, index, _why in defects],
                         [("classes[].primary", 3)])
        # And the same structure with the defect repaired passes, so the probe
        # fails on the row and not on the shape it was built with.
        block["classes"][3]["primary"] = dict(good)
        self.assertEqual(self.interval_block_defects(block), [])


if __name__ == "__main__":
    unittest.main()
