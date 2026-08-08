#!/usr/bin/env python3
"""The batch driver end to end, against a stand-in CLI and a stand-in operator
HOME — ported from Study 011's `harness/tests/test_batch.py` and adapted to
five arms and §2.8's registered call order (round 3 finding 12).

The real wrapper runs: the same bash, the same `env -i` scrub, the same fresh
HOME and CODEX_HOME per run, the same binary-digest and CLI-version gates (the
stand-in's digest is pinned in a test registry, so the check passes because it
was satisfied and not because it was skipped), the same arm-keyed slot rule,
the same slot retention, and the real §3.2 recapture with the probe prompt.
Only the binary and the operator's home are stand-ins, and neither reaches a
network or a model. `$HOME` is redirected to a throwaway directory for every
case, so the operator's real credential is never copied anywhere by the suite.

What this proves that a unit test cannot: that a failing run terminates its own
slot with a refusal record and the batch CONTINUES (§2.5's ported difference
from Study 010); that the slots the wrapper writes carry the arm, the arm
prompt digest and the three schedule stamps §2.9 registers, in the arm's own
tree; that resumption by global schedule index merges the ledger rather than
replacing it [D-22]; that no slot is created before the golden capture is
registered; that no retained byte carries the credential; and that §6 C7
retains its three files and deletes the transcript itself.

Two adaptations to §2.10 [D-23], which are also the two things this file
deliberately does NOT do:

  * **the population root is derived**, so there is no `--slots` to point at a
    throwaway tree — `batch.ARMS_ROOT` and `batch.RESULTS` are patched to this
    test's own root instead, exactly as Study 011's file already patched
    `RESULTS`, and every refusal line under test is the registered one;
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
        self.arms_root = os.path.join(self.root, "arms")
        self.patch_constant("ARMS_ROOT", self.arms_root)
        # The no-new-slots marker is the STUDY's own RESULTS.json (§2.8),
        # pointed at this test's root for the same reason.
        self.patch_constant("RESULTS", os.path.join(self.root, "RESULTS.json"))
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
                cli: str = None, environment: dict = None):
        """One call of the real wrapper, by hand, as an operator would — with
        §2.7's two new arguments, the arm id and the arm's own prompt path."""
        env = dict(os.environ)
        env["PYTHON_BIN"] = sys.executable
        # The driver subprocess must not write bytecode beside the
        # reviewed sources: the §2.10 gate refuses on a cache, and this
        # child does not inherit pytest's environment (round 5, finding 3).
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env.update(environment or {})
        return subprocess.run(
            ["bash", WRAPPER, self.scratch, slot, pins_path or self.pins_path,
             arm, os.path.join(STUDY, "arms", arm, "PROMPT.txt"),
             cli or self.cli],
            capture_output=True, text=True, env=env)

    def recapture_then_batch(self, extra=("--runs", str(BATCH_RUNS))):
        """The registered order: capture, agree, register the digest, then the
        batch."""
        self.assertEqual(self.capture(), 0)
        self.register_golden()
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
        refusal test below.
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
        another arm's tree silently, and every per-slot check would pass."""
        stray = os.path.join(self.arms_root, "B", "authoring", "run-001")
        completed = self.wrapper(stray, "C")
        self.assertEqual(completed.returncode, 1)
        self.assertIn("not under arms/C/authoring/", completed.stderr)
        self.assertFalse(os.path.exists(stray))

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
            ["bash", WRAPPER, self.scratch, slot, self.pins_path,
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
        cls.results = population.score()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, True)

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
            self.assertEqual(self.blocks_carrying_ci95(
                self.results["census"][arm], ""), set(), arm)

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
