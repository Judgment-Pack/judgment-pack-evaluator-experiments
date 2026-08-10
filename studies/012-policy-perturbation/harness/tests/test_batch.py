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
import gatescan
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
class BatchFixture(unittest.TestCase):
    """The stand-in study, CLI, HOME and registry every wrapper-driven case
    here runs against, and nothing else. It carries no test of its own: `Batch`
    below holds the driver's behaviour and `PreCallGates` holds §7's pre-call
    gate ledger, and both need this one fixture rather than a copy of it."""

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

    def stand_in_registry(self, committed: dict = None) -> dict:
        """The committed registry with the stand-in binary's digest and version
        moved, and every one of §2.10's four post-freeze members WRITTEN.
        Everything the batch checks — N, the slot count, the registered order,
        the five arm prompts — is the committed registry's, so these tests run
        the real preflight and not a relaxed one.

        The four lifecycle members are written rather than inherited because
        they are the study's STAGE, not its registration: `register_golden()`
        and `record_negative_control()` below are this fixture's own README
        steps 4 and 5, and a value read off the committed registry would make
        every case here a function of how far the real ceremony has got — which
        §2.10 forbids a manifest-covered test expectation to be, and which rule
        3 would forbid repairing once the final round has read the file (round
        15, finding 1). `fixtures.stand_in_registry()` is where the writing
        happens, for this builder and for `test_admission.py`'s alike, and it
        is keyed off `integrity.POST_FREEZE_MEMBERS` so that a fifth member is
        nulled here with no edit; `test_no_case_here_depends_on_the_studys_stage`
        holds the constructor, and
        `test_manifest.py::test_every_stand_in_registry_writes_every_lifecycle_member`
        holds the fact that every builder goes through it.

        Round 16, finding 4: the two freeze pins are written TOGETHER. This
        builder used to fill `freeze.preregistrationSha256` and null
        `freeze.treeManifestSha256` beside it, which is the one shape §2.10
        says cannot exist and `integrity.verify_tree()` refuses by name — it
        survived only because nothing on the driver's path reads the tree pin
        off a supplied registry.
        """
        if committed is None:
            with open(REGISTRY) as handle:
                committed = json.load(handle)
        pins = fixtures.stand_in_registry(committed, {
            ("freeze", "preregistrationSha256"):
                batch._digest(os.path.join(STUDY, "PREREGISTRATION.md")),
            ("freeze", "treeManifestSha256"): fixtures.STAND_IN_TREE_MANIFEST,
        })
        pins["codex"]["binarySha256"] = batch._digest(self.cli)
        pins["codex"]["version"] = "codex-cli 0.145.0-fake"
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
        `stand_in_registry()` WRITES the assent null rather than inheriting one
        — this method and `register_golden()` are the fixture's own README
        steps 5 and 4, and every case that wants another state writes the state
        it wants (round 15, finding 1).

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

    def refusal(self, extra=(), pins_path: str = None) -> str:
        """The registered refusal line `batch.py run` prints, so a case can name
        the gate it is about instead of taking any exit 1 for the one it meant.

        Round 15, finding 1: with `require_golden()` removed from `preflight()`
        the whole suite stayed green, because §6 C7's gate below it refused for
        its own reason and every golden case asserted only the status."""
        captured = io.StringIO()
        with contextlib.redirect_stderr(captured):
            self.assertEqual(self.run_batch(list(extra), pins_path=pins_path), 1)
        return captured.getvalue()

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

    def unpinned_cli(self) -> str:
        other = fixtures.write_fake_cli(os.path.join(self.root, "cli2"), PLAN,
                                        sys.executable, HERE)
        with open(other, "a") as handle:
            handle.write("# a different binary\n")
        return other


class Batch(BatchFixture):

    # --- the fixture's own stage (round 15, finding 1) -----------------------

    def test_no_case_here_depends_on_the_studys_stage(self):
        """§2.10: no manifest-covered test expectation may be a function of the
        study's stage. Asserted rather than reviewed for the one input every
        case in this class shares — the registry `setUp` writes is IDENTICAL
        when the committed registry is advanced through each of its four
        post-freeze members, so no case running under it can read one.

        The instance it closes: the fixture used to INHERIT `golden.sha256` and
        `isolationNegative.assent`, so README steps 4 and 5 moved the refusal
        two golden cases and the C7-ordering case below actually fired on,
        while all three stayed green at every stage — silent coverage loss and
        not the livelock §2.10 describes, which is why fourteen rounds of a
        green suite did not see it (round 15, finding 1).

        Round 16, finding 4: the guard is over the shared CONSTRUCTOR as well
        as over this builder, because round 15 closed this instance, declared
        the sweep complete and was wrong — `test_admission.py`'s builder
        inherited the tree pin. One behavioural guard over
        `fixtures.stand_in_registry()` plus the source-level rule in
        `test_manifest.py` that every builder goes through it is what replaces
        a second copy of this case.

        What it does NOT cover, so the guard is not read for more than it is:
        the two other cases in this class that open `REGISTRY` themselves, the
        module-level interpreter check, and `IntervalScope` below. None of the
        four reads a post-freeze member — `check_registry()` reads the order
        and the prompts, the spelling case reads member NAMES, the interpreter
        check reads `python`, and `fixtures.Population` writes its own
        preconditions with the study's three nulled — but that is reviewed and
        not asserted here. Nor does it cover `CALL.json`'s `pinsSha256`
        (`fixtures.py`), the live digest of the registry FILE and therefore a
        function of all four members: that byte does move by stage, admission
        recomputes the same digest on the other side, and it is an expectation
        of neither side."""
        with open(REGISTRY) as handle:
            committed = json.load(handle)
        advanced = json.loads(json.dumps(committed))
        for parent, member in integrity.POST_FREEZE_MEMBERS:
            advanced.setdefault(parent, {})[member] = "sha256:" + "3" * 64
        self.assertNotEqual(advanced, committed)
        self.assertEqual(self.stand_in_registry(advanced),
                         self.stand_in_registry(committed))
        # …and the constructor itself, which `test_admission.py` reaches
        # through its own builder and not through this one.
        self.assertEqual(fixtures.stand_in_registry(advanced),
                         fixtures.stand_in_registry(committed))
        with self.assertRaises(AssertionError):
            fixtures.stand_in_registry(committed, {("freeze", "misspelled"): 1})

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
        study, and the 30-round order must not be runnable under it.

        Round 16, finding 2: NAMED, and with every other gate satisfied first.
        This case asserted a bare exit 1 while §6 C7's assent gate below
        `check_registry()` was still unmet, so the refusal it read was that
        gate's and the whole preflight call to `check_registry()` could be
        deleted with the suite still green — the round-15 golden defect, one
        gate over. `PreCallGates` below is the general form; this case is the
        instance, kept because it is where a reader looks for [D-1]."""
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        self.record_negative_control()
        spent = self.calls_made()
        pins = json.loads(json.dumps(self.pins))
        pins["batch"]["n"] = 25
        path = os.path.join(self.root, "PINS-n25.json")
        with open(path, "w") as handle:
            json.dump(pins, handle, indent=2)
        self.assertIn("batch.n = 25",
                      self.refusal(["--runs", "1"], pins_path=path))
        self.assertFalse(os.path.exists(self.arms_root))
        self.assertEqual(self.calls_made(), spent)
        # The admitting half: the same command line, the registered N, a slot.
        self.assertEqual(self.run_batch(["--runs", "1"]), 0)
        self.assertTrue(os.path.isdir(self.slot(0)))

    # --- the golden gate ----------------------------------------------------

    def test_no_slot_is_created_before_the_golden_capture_is_registered(self):
        # The failure this closes cost fifty real calls in Study 011: the batch
        # ran to completion and only the scorer noticed there was no allowlist.
        #
        # Both refusals are NAMED. An exit 1 is not evidence that this gate
        # fired: §6 C7's assent gate sits below it and refuses the same case
        # for its own reason, so with `require_golden()` gone from `preflight()`
        # this test — and the whole suite — stayed green (round 15, finding 1).
        self.assertIn("no golden context at", self.refusal(["--runs", "1"]))
        self.assertFalse(os.path.exists(self.arms_root))
        self.assertEqual(self.capture(), 0)          # the file exists…
        self.assertIn("registers no golden.sha256",
                      self.refusal(["--runs", "1"]))           # …unpinned
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
        self.assertIn("not the registered", self.refusal(["--runs", "1"]))
        self.assertFalse(os.path.exists(self.arms_root))

    def test_a_batch_never_starts_against_an_unfrozen_preregistration(self):
        """§2.10, and §7's claim about the CALLS: the freeze digest is a
        precondition of the batch and not only of the scoring.

        Round 16, finding 1: BOTH halves of the gate, both NAMED, with §6 C7's
        record already on disk so the freeze is the only unmet gate. This case
        used to assert a bare exit 1 without recording the control, so the
        refusal it actually read was C7's assent gate — `require_freeze(pins)`
        could be deleted from `preflight()` and the whole suite stayed green,
        which is the §7 bullet at the top of this docstring going unenforced
        with nothing to say so."""
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        self.record_negative_control()
        spent = self.calls_made()
        unfrozen = self.alternate_registry(
            "PINS-unfrozen.json",
            freeze=dict(self.pins["freeze"], preregistrationSha256=None))
        self.assertIn("registers no freeze.preregistrationSha256",
                      self.refusal(["--runs", "1"], pins_path=unfrozen))
        self.assertFalse(os.path.exists(self.arms_root))
        self.assertEqual(self.calls_made(), spent)
        # The gate's other half, which nothing exercised: a pin that is FILLED
        # and no longer the file's. "Frozen" is a digest that still matches,
        # not a non-null member.
        edited = self.alternate_registry(
            "PINS-edited.json",
            freeze=dict(self.pins["freeze"],
                        preregistrationSha256="sha256:" + "5" * 64))
        self.assertIn("it was edited after the freeze",
                      self.refusal(["--runs", "1"], pins_path=edited))
        self.assertFalse(os.path.exists(self.arms_root))
        self.assertEqual(self.calls_made(), spent)
        # …and the admitting half, so the gate is not merely refusing.
        self.assertEqual(self.run_batch(["--runs", "1"]), 0)
        self.assertTrue(os.path.isdir(self.slot(0)))

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
        under the one the registry REGISTERS still refuses.

        Each of the three registries WRITES the member it is about. The null
        case used to inherit its null from the committed registry, which is a
        stage and not a fixture: README step 5 records the assent, so the case
        would have stopped being the null case one step after the freeze, with
        §2.10 rule 3 forbidding the repair."""
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        out = os.path.join(self.root, "isolation-negative")
        for name, member in (
                ("PINS-null.json", {"assent": None}),
                ("PINS-withheld.json", {"assent": "withheld"}),
                ("PINS-old-name.json", {"assent": None,
                                        "operatorAssent": "granted"})):
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
        # Named, and under a registry that GRANTS the assent: the refusal this
        # case is about is the missing RECORD's, and the assent gate sits above
        # it — so an unnamed exit 1 here was the assent case one test down, and
        # the subject would have moved to the record at README step 5 (round
        # 15, finding 1).
        self.assertIn("no §6 C7 record at",
                      self.refusal(["--runs", "1"],
                                   pins_path=self.assenting_registry()))
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

    def test_a_stale_ledger_temporary_is_refused_by_name(self):
        """Round 16, finding 3: the temporary has a FIXED, registered name, and
        an uncatchable kill in the rename window leaves it behind.

        Under `mkstemp` that residue was a `BATCH.json.<random>.partial` that
        no `freeze.excluded` entry could name, that the writer scan could not
        resolve, and that only an unread docstring note asked the operator to
        remove — so a publication `git add -A` moved the manifest the final
        round attested. `O_EXCL` makes it a refusal the next run names, and the
        name is a registered exclusion, which is what makes the residue inert
        rather than merely transient."""
        self.recapture_then_batch(extra=["--runs", "1"])
        ledger = os.path.join(self.arms_root, "BATCH.json")
        stale = os.path.join(self.arms_root, batch.LEDGER_TEMP_NAME)
        with open(stale, "w") as handle:
            handle.write("half a ledger\n")
        with open(ledger, "rb") as handle:
            before = handle.read()
        spent = self.calls_made()
        self.assertIn("a previous run left the ledger's temporary behind",
                      self.refusal(["--runs", "1", "--resume"]))
        # Before a call is spent: the residue is checkable in preflight, so the
        # refusal is not the atomic writer's, which would land after the first
        # slot of the invocation had already run.
        self.assertEqual(self.calls_made(), spent)
        self.assertFalse(os.path.exists(self.slot(1)))
        # The ledger the crash left is whole and untouched, and the residue is
        # still there for the operator to record and remove.
        with open(ledger, "rb") as handle:
            self.assertEqual(handle.read(), before)
        self.assertTrue(os.path.exists(stale))
        # …and the admitting half.
        os.unlink(stale)
        self.assertEqual(self.run_batch(["--runs", "1", "--resume"]), 0)
        self.assertEqual(len(self.ledger()["records"]), 2)
        self.assertFalse(os.path.exists(stale))

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


# --- §7's pre-call gates, derived (round 16, findings 1 and 2) ---------------
#
# The class three rounds have now repaired one instance at a time: a gate that
# `preflight()` runs before the first call, a test that drives the registered
# command line and asserts a bare exit 1, and a LATER gate that supplies that
# exit 1 for its own reason. Delete the call and the suite stays green. Round
# 15 closed it on the golden gate; round 16's sweep found ten of preflight's
# fourteen gates in the same state, and `require_freeze()` — a §7 enforcement
# claim about the CALLS — removable at all five of its call sites at once.
#
# What follows is the class rather than the eleventh instance. The gate set is
# READ OUT OF `batch.py` by `ast`; `PRE_CALL_GATES` is required to be exactly
# it, so a gate added to the driver, or a command that starts calling one, is a
# missing ledger row and fails by name. Three tests stand on that one
# derivation: A that the ledger is complete, B that each row's needle is really
# a refusal that gate raises and that no OTHER gate raises it unrecorded, and C
# that with every other gate satisfied and this one alone unmet the registered
# command line refuses BY THAT NAME, spends no call, writes no artifact and
# leaves the ledger where it was — and admits once the gate is satisfied.
#
# What it cannot do is in `PreCallGates`'s own docstring, in full. The short
# version: it is author-VISIBLE, not author-proof. Deleting a gate and its
# ledger row together is green; what the mechanism converts is a silent
# deletion into an edit of the file whose only job is to record the gate set.


# The derivation's generic half lives in `gatescan.py` (round 17, finding 3),
# because `score_rates.verify_preconditions()` needs the same AST walk and a
# second copy of it is the "two hand-kept builders" pattern this sequence has
# already repeated three times. What stays here is what is genuinely
# batch-shaped: `main()`'s command dispatch, `preflight()`'s `prompt_kind`
# branch, the `invoke()` spend boundary, and the per-command cell keying.
_module_functions = gatescan.module_functions
_raised_literal = gatescan.raised_literal
gate_identity = gatescan.gate_identity
Gate = gatescan.Gate


def _batch_tree() -> ast.Module:
    """`batch.py`'s own source. Read from `batch.__file__`, so this is the file
    the tests import and `integrity.verify()` pins, not a second copy."""
    return gatescan.parse(batch.__file__)


def _is_batch_error(node: ast.Raise) -> bool:
    return gatescan.is_raise_of(node, "BatchError")


def _raises_batch_error(name: str, functions: dict) -> bool:
    """Whether calling `name` can raise `BatchError`, directly or through
    another module-level function of `batch.py`."""
    return gatescan.can_raise(name, functions, "BatchError")


def _first_invoke(function: ast.FunctionDef):
    """The line of a function's first `invoke()`, or None — the point where a
    call is spent and the pre-call region ends.

    Derived with an EMPTY gate set on purpose: `invoke` is matched by its own
    name, so the bound does not depend on the gate set the bound is used to
    compute."""
    return min([row[2] for row in _sites_in(function, ()) if row[0] == "invoke"],
               default=None)


def hosts() -> tuple:
    """Every function whose pre-call region this ledger derives: `main()`'s own
    pre-dispatch region, the shared `preflight()`, and each command entry."""
    return ("main", "preflight") + tuple(sorted(set(command_entries().values())))


def gate_functions(host: str = "preflight", limit=None) -> tuple:
    """The gate FUNCTIONS one HOST runs: that host's own direct module-level
    callees that can refuse, above `limit` when a limit is given.

    Derived, never listed. For `preflight()` it is `verify_ported_bytes`,
    `require_freeze`, `check_registry`, `require_golden` and
    `require_isolation_negative`; a sixth arrives here by being called, not by
    being written down.

    Round 17, finding 2: the host used to be `preflight()` and nothing else,
    while PREREGISTRATION.md §2.10 registers the rule over "every gate the
    driver runs before it spends a call … per registered command" and this
    file's own docstring claimed that a gate added to a COMMAND ENTRY becomes a
    named failure. It did not. An entry's `require_x(…)` was in no host's
    callee set, produced no cell, and could be deleted with the suite green —
    measured: a refusing `require_absolute_scratch()` added to `run_batch()`
    above its first `invoke()` left the whole suite at 309 passed. Only an
    entry's INLINE `raise` was caught, which is why the mechanism looked as
    though it worked: round 16's own new gate happened to be inline.

    The rule is DEPTH ONE, and that is the honest formulation rather than the
    "transitive closure over module-level callees" the finding asked for. It is
    also the rule that has always been in force for `preflight()`, so it is the
    SYMMETRIC one. Refusal-CAPABILITY is transitive — `_raises_batch_error()`
    walks callees — but gate IDENTITY is not: a literal closure from the five
    entries reaches fourteen functions, and six of them (`williams`,
    `schedule`, `_write_json_atomic`, `slot_outcome`, `verify_seal_of`,
    `verify_chain`) are reached only THROUGH another function that is already
    ledgered as a gate, so each would be counted a second time under its own
    name. What that leaves outside is the depth of literal attribution, and it
    is stated in this class's own limits rather than glossed."""
    functions = _module_functions(_batch_tree())
    # The dispatch is not a gate: an entry function is a HOST of its own and
    # its gates are derived there, once. `preflight` and `invoke` are sites of
    # their own kinds, not gate functions.
    skip = set(command_entries().values()) | {"preflight", "invoke"}
    return gatescan.callee_gates(functions[host], functions, "BatchError",
                                 skip=skip, limit=limit)


def all_gate_functions() -> tuple:
    """Every gate function any host runs before a call — `main()`'s, the shared
    `preflight()`'s, and each command entry's above that entry's first
    `invoke()`.

    This is the universe `gate_refusal_literals()` reads. It has to be the
    UNION and not preflight's five, or test B would compare each needle against
    a third of the messages the driver can actually print, and a needle two
    gates share would read as unique."""
    functions = _module_functions(_batch_tree())
    names = set()
    for host in hosts():
        names |= set(gate_functions(host, _first_invoke(functions[host])))
    return tuple(sorted(names))


def _command_selector(test, commands):
    """The commands an `if` arm of `main()`'s dispatch is reached by, or
    `commands` unchanged when the test is not a dispatch arm.

    `main()` selects on a bare name — `command == "run"` and `command in
    ("run", "shortfall")` — which is the same shape `prompt_kind` has inside
    `preflight()`, one level up. Both spellings are read, because [D-22]'s
    removed-flag refusal is written with the second one."""
    if not isinstance(test, ast.Compare) or len(test.ops) != 1 \
            or not isinstance(test.left, ast.Name) or test.left.id != "command":
        return commands
    right = test.comparators[0]
    if isinstance(test.ops[0], ast.Eq) and isinstance(right, ast.Constant):
        chosen = (right.value,)
    elif isinstance(test.ops[0], ast.In) \
            and isinstance(right, (ast.Tuple, ast.List)) \
            and all(isinstance(item, ast.Constant) for item in right.elts):
        chosen = tuple(item.value for item in right.elts)
    else:
        return commands
    if commands is None:
        return chosen
    return tuple(name for name in chosen if name in commands)


def _sites_in(function: ast.FunctionDef, gates: tuple) -> list:
    """[(kind, label, line, prompt_kind, literal, commands)] for one function
    body.

    `kind` is "gate" for a call to one of the gate functions, "inline" for a
    `raise BatchError` the function makes itself, "preflight" for the call that
    delegates to the shared preflight, and "invoke" for the first spent call.

    An inline gate's LABEL is the source of the `if` that guards it, unparsed.
    A line number would move under every edit above it and a message would make
    test B circular; the condition is what a reader identifies the gate by, and
    rewording it is an edit to this ledger — which is the point. An `except`
    handler is a guard like any other and is labelled by the handler it is in,
    not by the `if` that happens to enclose the `try` (round 17, finding 3):
    two handlers under one guard used to collapse into one cell and a gate
    disappeared silently.

    `prompt_kind` carries the ONE branch inside `preflight()` that decides
    which command reaches a site; `commands` carries the same thing for
    `main()`'s dispatch, and is None where the site is unguarded by it. Every
    other `if` is part of a gate's own condition, not of the path.

    COMPOUND-STATEMENT HEADERS ARE SCANNED (round 17, finding 2). The walk used
    to recurse into `If`/`For`/`While`/`With` BODIES and never inspect
    `If.test`, `For.iter`, `While.test` or `With.items`, so a call in a header
    was invisible. That is live, not hypothetical: `capture_slots(slots_dir)`
    — the gate `batch.py`'s own docstring names as the one that "refuses
    batch-shaped names" — is the iterator of a `for` loop, so widening the gate
    set without this would have put it in the gate set and produced no cell for
    it: a gate function with no site.

    The WALK is `gatescan.sites_in()` (round 17, finding 3), shared with the
    scorer's ledger. What this function supplies is the two batch-shaped
    halves: which calls are sites, and which `if` selects a PATH rather than
    guarding a gate."""

    def classify(call):
        if not isinstance(call.func, ast.Name):
            return None
        if call.func.id in gates:
            return ("gate", call.func.id)
        if call.func.id == "preflight":
            argument = (call.args[5] if len(call.args) > 5 else None)
            if not isinstance(argument, ast.Constant):
                raise AssertionError(
                    "batch.py:%d calls preflight() with a prompt_kind this "
                    "derivation cannot read: the branch that decides which "
                    "command reaches which gate has to be a literal at the "
                    "call site" % call.lineno)
            return ("preflight", argument.value)
        if call.func.id == "invoke":
            return ("invoke", None)
        return None

    def narrow(test, context):
        prompt_kind, commands = context
        if isinstance(test, ast.Compare) and isinstance(test.left, ast.Name) \
                and test.left.id == "prompt_kind" and len(test.ops) == 1 \
                and isinstance(test.ops[0], ast.Eq) \
                and isinstance(test.comparators[0], ast.Constant):
            kind = test.comparators[0].value
            return ((kind, commands), ("!" + kind, commands))
        chosen = _command_selector(test, commands)
        if chosen is not commands:
            return ((prompt_kind, chosen), (prompt_kind, commands))
        return None

    return [(kind, label, line, context[0], literal, context[1])
            for kind, label, line, context, literal
            in gatescan.sites_in(function, "BatchError", classify, narrow,
                                 context=(None, None))]


def command_entries() -> dict:
    """{command: entry function}, read out of `main()`'s own dispatch.

    Every member of `batch.COMMANDS` must land somewhere: the dispatch's `if
    command == "…"` arms name four of them and the fall-through return names
    the fifth, and a command that reaches neither fails here rather than
    quietly leaving its gates underived."""
    functions = _module_functions(_batch_tree())
    main = functions["main"]
    entries = {}
    for node in ast.walk(main):
        if not isinstance(node, ast.If) or not isinstance(node.test, ast.Compare):
            continue
        test = node.test
        if not (isinstance(test.left, ast.Name) and test.left.id == "command"
                and len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq)
                and isinstance(test.comparators[0], ast.Constant)):
            continue
        for inner in node.body:
            if isinstance(inner, ast.Return) \
                    and isinstance(inner.value, ast.Call) \
                    and isinstance(inner.value.func, ast.Name) \
                    and inner.value.func.id in functions:
                entries[test.comparators[0].value] = inner.value.func.id
    remaining = [name for name in batch.COMMANDS if name not in entries]
    # The fall-through: the last statement of `main()`'s dispatch block, which
    # is the command no `if` arm names.
    body = [node for node in main.body if isinstance(node, ast.Try)]
    tail = body[-1].body[-1] if body else None
    if len(remaining) != 1 or not isinstance(tail, ast.Return) \
            or not isinstance(tail.value, ast.Call) \
            or not isinstance(tail.value.func, ast.Name) \
            or tail.value.func.id not in functions:
        raise AssertionError(
            "main() dispatches %r and batch.COMMANDS is %r: this derivation "
            "reads one fall-through command at the end of the dispatch and %d "
            "are unaccounted for" % (sorted(entries), list(batch.COMMANDS),
                                     len(remaining)))
    entries[remaining[0]] = tail.value.func.id
    return entries


def _add_cell(cells: dict, key: tuple, line: int) -> None:
    """One derived cell, and a refusal to lose one to a key collision.

    `cells` used to be an ordinary dict assignment, so two sites that produced
    one key silently became one cell (round 17, finding 3). A GATE function is
    one gate however many times a host calls it — that is `gate_identity()`'s
    rule and the reason `require_freeze` is one `SATISFY` row and five cells —
    so repeated call sites of one gate collapse to the FIRST of them by
    design. Two distinct INLINE raises under one guard do not: that is two
    gates wearing one name, and it fails here rather than becoming a cell whose
    deletion nothing notices. `capture_isolation_negative()` carries the live
    example — two `raise BatchError`s both guarded by `os.path.exists(raw)`,
    which only stay apart because the second sits below the first `invoke()`."""
    if key not in cells or cells[key] == line:
        cells[key] = min(cells.get(key, line), line)
        return
    if key[2] == "gate":
        cells[key] = min(cells[key], line)
        return
    raise AssertionError(
        "batch.py:%d and batch.py:%d both derive the cell %r: two refusals "
        "under one guard are one ledger row, so deleting either is invisible. "
        "Give one of them its own guard." % (cells[key], line, key))


def derived_pre_call_gates() -> dict:
    """{(command, host, kind, label): line} — every gate the driver runs
    BEFORE it spends a call, per command.

    A site counts when it is in `main()`'s own pre-dispatch region, in
    `preflight()`, or in a command's own entry function above that entry's
    first `invoke()`. `preflight()`'s sites are attributed to each command that
    reaches them: the registered-batch arm to the commands that call it with
    `"registered"`, the probe arm to the ones that call it with `"probe"`, and
    the unguarded ones to both. `main()`'s are attributed by its dispatch —
    each `if command == …` arm to its own command, and the sites above the
    dispatch to all five.

    KEYED ON (command, gate) and not on the gate alone, because that is the
    distinction the round-16 sweep turned on: `require_freeze()` is called at
    five sites across four commands, and a (gate, needle) table would have
    declared the whole of it covered by the single `run` case that touches
    one.

    Round 17, finding 2: THE GATE SET IS NOW HOST-RELATIVE. It used to be
    `preflight()`'s five for every host, so a command entry's own gate calls
    matched nothing and produced no cell — the registered rule at
    PREREGISTRATION.md §2.10 said "per registered command" and the derivation
    said "per preflight". Each entry now contributes its own direct
    refusal-capable callees above its first `invoke()`, and `main()` is a host
    rather than a file this derivation reads only to learn five names."""
    tree = _batch_tree()
    functions = _module_functions(tree)
    shared = _sites_in(functions["preflight"], gate_functions("preflight"))
    cells = {}
    # `main()` has no `invoke()` of its own: its whole body is pre-call, and
    # every command reaches it before it reaches anything else.
    for kind, label, line, _prompt, _literal, commands in _sites_in(
            functions["main"], gate_functions("main")):
        if kind in ("invoke", "preflight"):
            continue
        for command in (commands if commands is not None else batch.COMMANDS):
            _add_cell(cells, (command, "main", kind, label), line)
    for command, entry in sorted(command_entries().items()):
        first_call = _first_invoke(functions[entry])
        rows = _sites_in(functions[entry], gate_functions(entry, first_call))
        for kind, label, line, _prompt, _literal, _commands in rows:
            if kind == "invoke" or (first_call is not None and line >= first_call):
                continue
            if kind == "preflight":
                for inner in shared:
                    inner_kind, inner_label, inner_line, prompt = inner[:4]
                    if prompt is None or prompt == label \
                            or (prompt.startswith("!") and prompt[1:] != label):
                        _add_cell(cells, (command, "preflight", inner_kind,
                                          inner_label), inner_line)
                continue
            _add_cell(cells, (command, entry, kind, label), line)
    return cells


def gate_refusal_literals() -> dict:
    """{gate identity: (refusal string, …)} — the messages each gate raises,
    read out of `batch.py`. A gate FUNCTION owns every `raise BatchError` in
    its body; an inline gate owns the raises its own `if` guards.

    Over `all_gate_functions()` and every host, not `preflight()`'s five: the
    needle test is a claim that no OTHER gate can supply a case's needle, and a
    universe that is a third of the driver's refusals cannot support it. Round
    17, finding 2 found a live vacuity the moment the universe widened — see
    `_SHARED_SCRATCH` below."""
    tree = _batch_tree()
    functions = _module_functions(tree)
    gates = all_gate_functions()
    literals = {}
    # Inline gates live in `main()`, in `preflight()` and in the command
    # entries; a raise inside a gate FUNCTION belongs to that gate and is
    # collected below, not twice.
    for host in sorted(hosts()):
        for row in _sites_in(functions[host], gates):
            kind, label, literal = row[0], row[1], row[4]
            if kind != "inline" or literal is None:
                continue
            literals.setdefault(("inline", host, label), []).append(literal)
    for gate in gates:
        literals[("gate", gate)] = [
            text for text in
            (_raised_literal(node) for node in ast.walk(functions[gate])
             if isinstance(node, ast.Raise) and _is_batch_error(node))
            if text]
    return {key: tuple(value) for key, value in literals.items()}


# The ceremony act that leaves each gate SATISFIED, keyed on the gate itself
# rather than on the command, and asserted total against the derivation by
# `test_every_derived_gate_has_a_way_to_satisfy_it` — so a gate added to the
# driver arrives with a way to meet it, not only with a way to break it.
# `satisfied_by_the_fixture` is the honest name for a gate the stand-in study
# already meets (its wrapper is on disk, its scratch parent is a directory, its
# CLI is the pinned one); those are broken by a `recipe` instead.
SATISFY = {
    # -- `main()`'s own pre-dispatch region (round 17, finding 2) ------------
    # A well-formed command line meets all four: the fixture always names its
    # scratch parent and its slots directory, gives every flag a value, and
    # carries no flag a registered decision removed. Each is broken by a
    # `recipe` that changes the SHAPE of the line rather than a value in it.
    ("main", "gate", "_argument"): "satisfied_by_the_fixture",
    ("main", "inline", "flag in argv"): "satisfied_by_the_fixture",
    ("main", "inline", "scratch_parent is None"): "satisfied_by_the_fixture",
    ("main", "inline", "slots_dir is None"): "satisfied_by_the_fixture",

    ("preflight", "gate", "verify_ported_bytes"): "satisfied_by_the_fixture",
    ("preflight", "inline", "not slots"): "satisfied_by_the_fixture",
    ("preflight", "inline", "not os.path.isfile(SCRIPT)"):
        "satisfied_by_the_fixture",
    ("preflight", "inline", "not os.path.isdir(scratch_parent)"):
        "satisfied_by_the_fixture",
    ("preflight", "gate", "require_freeze"): "freeze_the_preregistration",
    ("preflight", "inline", "not entries"): "satisfied_by_the_fixture",
    ("preflight", "inline",
     "entries[-1]['globalIndex'] > REGISTERED_SLOTS"):
        "satisfied_by_the_fixture",
    ("preflight", "gate", "check_registry"): "satisfied_by_the_fixture",
    ("preflight", "inline", "not pinned"): "satisfied_by_the_fixture",
    ("preflight", "inline", "not _matches(actual, pinned)"):
        "satisfied_by_the_fixture",
    ("preflight", "inline", "not os.path.isfile(cli_override)"):
        "satisfied_by_the_fixture",
    ("preflight", "inline",
     "not _matches(override_digest, pins['codex']['binarySha256'])"):
        "satisfied_by_the_fixture",
    ("preflight", "inline", "os.path.exists(RESULTS)"):
        "satisfied_by_the_fixture",
    ("preflight", "inline", "os.path.lexists(temporary)"):
        "satisfied_by_the_fixture",
    ("preflight", "gate", "require_golden"): "register_the_golden",
    ("preflight", "gate", "require_isolation_negative"):
        "record_negative_control",
    ("preflight", "inline", "existing"): "satisfied_by_the_fixture",

    ("run_batch", "inline", "records and (not resume)"):
        "satisfied_by_the_fixture",
    ("run_batch", "inline", "os.path.exists(RESULTS)"):
        "satisfied_by_the_fixture",
    ("run_batch", "gate", "verify_ported_bytes"): "satisfied_by_the_fixture",
    ("run_batch", "gate", "require_freeze"): "freeze_the_preregistration",
    ("run_batch", "inline", "resume and (not records)"):
        "satisfied_by_the_fixture",
    ("run_batch", "inline", "not remaining"): "satisfied_by_the_fixture",
    ("run_batch", "inline", "runs < 1"): "satisfied_by_the_fixture",
    ("run_batch", "inline", "runs > len(remaining)"):
        "satisfied_by_the_fixture",
    # `run_batch`'s own gate FUNCTIONS, all six of them outside this ledger
    # until round 17 finding 2 made the gate set host-relative.
    ("run_batch", "gate", "schedule_entries"): "satisfied_by_the_fixture",
    ("run_batch", "gate", "load_ledger"): "satisfied_by_the_fixture",
    ("run_batch", "gate", "verify_prefix"): "satisfied_by_the_fixture",
    ("run_batch", "gate", "reconcile_ledger"): "satisfied_by_the_fixture",
    ("run_batch", "gate", "write_ledger"): "satisfied_by_the_fixture",
    ("run_batch", "gate", "arm_prompt"): "satisfied_by_the_fixture",

    ("run_capture", "inline", "os.path.exists(out_path)"):
        "satisfied_by_the_fixture",
    ("run_capture", "inline", "runs < MIN_CAPTURE_SLOTS"):
        "satisfied_by_the_fixture",

    ("capture_golden", "inline", "not out_path"): "satisfied_by_the_fixture",
    ("capture_golden", "inline", "os.path.exists(out_path)"):
        "satisfied_by_the_fixture",
    ("capture_golden", "inline", "min_slots < MIN_CAPTURE_SLOTS"):
        "satisfied_by_the_fixture",
    ("capture_golden", "gate", "verify_ported_bytes"):
        "satisfied_by_the_fixture",
    ("capture_golden", "gate", "require_freeze"): "freeze_the_preregistration",
    ("capture_golden", "inline", "not probe_pin"): "satisfied_by_the_fixture",
    ("capture_golden", "inline",
     "call.get('promptKind') != 'probe' or call.get('promptSha256') "
     "!= probe_pin"): "satisfied_by_the_fixture",
    ("capture_golden", "inline", "len(usable) < required"):
        "capture_two_agreeing_probes",
    ("capture_golden", "inline", "context != first"):
        "satisfied_by_the_fixture",
    # The two §3.2 gates `capture_golden()`'s own docstring names as the ones
    # that hold it. `capture_slots` sits in a `for … in` header, so it was
    # invisible twice over — to the gate set and to the site walk.
    ("capture_golden", "gate", "capture_slots"): "satisfied_by_the_fixture",
    ("capture_golden", "gate", "require_distinct_sessions"):
        "satisfied_by_the_fixture",

    ("capture_isolation_negative", "gate", "verify_ported_bytes"):
        "satisfied_by_the_fixture",
    ("capture_isolation_negative", "gate", "require_freeze"):
        "freeze_the_preregistration",
    ("capture_isolation_negative", "inline", "assent != 'granted'"):
        "grant_the_assent",
    ("capture_isolation_negative", "inline",
     "not os.path.isdir(scratch_parent)"): "satisfied_by_the_fixture",
    ("capture_isolation_negative", "gate", "require_golden"):
        "register_the_golden",
    ("capture_isolation_negative", "inline", "os.path.exists(out_dir)"):
        "satisfied_by_the_fixture",
    ("capture_isolation_negative", "inline", "os.path.exists(raw)"):
        "satisfied_by_the_fixture",

    ("declare_shortfall", "gate", "verify_ported_bytes"):
        "satisfied_by_the_fixture",
    ("declare_shortfall", "inline", "os.path.exists(RESULTS)"):
        "satisfied_by_the_fixture",
    ("declare_shortfall", "inline", "os.path.exists(out_path)"):
        "satisfied_by_the_fixture",
    ("declare_shortfall", "inline", "not reason"): "satisfied_by_the_fixture",
    ("declare_shortfall", "gate", "require_freeze"):
        "freeze_the_preregistration",
    ("declare_shortfall", "inline", "present >= REGISTERED_SLOTS"):
        "satisfied_by_the_fixture",
    ("declare_shortfall", "inline", "present != len(records)"):
        "satisfied_by_the_fixture",
    ("declare_shortfall", "gate", "schedule_entries"):
        "satisfied_by_the_fixture",
    ("declare_shortfall", "gate", "load_ledger"): "satisfied_by_the_fixture",
    ("declare_shortfall", "gate", "verify_prefix"): "satisfied_by_the_fixture",
    ("declare_shortfall", "gate", "reconcile_ledger"):
        "satisfied_by_the_fixture",
    ("declare_shortfall", "gate", "write_ledger"): "satisfied_by_the_fixture",
}

# Two refusals the driver spells the same way in two gates. Recorded here, and
# asserted to be EXACTLY these two, because a needle a second gate can supply
# is how a named case goes quietly vacuous — the defect one layer up from the
# one this ledger is for (round 16, finding 2).
_SHARED_RUNS = (("inline", "run_batch", "runs < 1"),)
_SHARED_SCRATCH = (("inline", "capture_isolation_negative",
                    "not os.path.isdir(scratch_parent)"),)

# Every derived (command, gate) cell, and how it is held. The keys are checked
# against the derivation in both directions, so this table cannot silently
# omit a gate and cannot silently name one the driver does not run.
PRE_CALL_GATES = {
    # -- `main()`'s own pre-dispatch region (round 17, finding 2) ------------
    #
    # The first gates any command line meets, and until round 17 they were in
    # no ledger at all: `command_entries()` read `main()` only to learn the
    # five entry names, so its own eleven refusals — [D-22]/[D-23]'s removed
    # flags, three `--scratch-parent is required`, `--slots is required`, and
    # `_argument()`'s "needs a value" once per command — were derived by
    # nothing and named by nothing. Every one of them is driven here.
    ("run", "main", "gate", "_argument"): Gate(
        "command", "needs a value", recipe="a_flag_given_without_its_value"),
    ("capture", "main", "gate", "_argument"): Gate(
        "command", "needs a value", recipe="a_flag_given_without_its_value"),
    ("capture-golden", "main", "gate", "_argument"): Gate(
        "command", "needs a value", recipe="a_flag_given_without_its_value"),
    ("capture-isolation-negative", "main", "gate", "_argument"): Gate(
        "command", "needs a value", recipe="a_flag_given_without_its_value"),
    ("shortfall", "main", "gate", "_argument"): Gate(
        "command", "needs a value", recipe="a_flag_given_without_its_value"),
    ("run", "main", "inline", "flag in argv"): Gate(
        "command", "is removed from `batch.py",
        recipe="a_flag_a_registered_decision_removed"),
    ("shortfall", "main", "inline", "flag in argv"): Gate(
        "command", "is removed from `batch.py",
        recipe="a_flag_a_registered_decision_removed"),
    ("run", "main", "inline", "scratch_parent is None"): Gate(
        "command", "--scratch-parent is required",
        recipe="a_command_line_with_no_scratch_parent"),
    ("capture", "main", "inline", "scratch_parent is None"): Gate(
        "command", "--scratch-parent is required",
        recipe="a_command_line_with_no_scratch_parent"),
    ("capture-isolation-negative", "main", "inline",
     "scratch_parent is None"): Gate(
        "command", "--scratch-parent is required",
        recipe="a_command_line_with_no_scratch_parent"),
    ("capture-golden", "main", "inline", "slots_dir is None"): Gate(
        "command", "--slots is required",
        recipe="a_command_line_with_no_slots_directory"),

    # -- `run`, through the shared preflight ---------------------------------
    ("run", "preflight", "gate", "verify_ported_bytes"): Gate(
        "command", "the ported bytes are not the registered ones",
        recipe="break_the_ported_bytes"),
    ("run", "preflight", "inline", "not slots"): Gate(
        "preflight", "a batch needs at least one run",
        recipe="empty_slot_list", shared=_SHARED_RUNS,
        why="`run` cannot reach preflight with an empty slot list: run_batch's "
            "own `runs < 1` refuses first, with the same words. The gate is "
            "therefore driven at `preflight()` itself, where its own refusal "
            "is the one under test, and the collision is declared above."),
    ("run", "preflight", "inline", "not os.path.isfile(SCRIPT)"): Gate(
        "command", "no authoring wrapper at", recipe="hide_the_wrapper"),
    ("run", "preflight", "inline", "not os.path.isdir(scratch_parent)"): Gate(
        # Round 17, finding 2: the needle was "is not a directory", and the
        # moment the literal universe stopped being preflight's five gates it
        # turned out `capture_slots()` and `reconcile_ledger()` spell their own
        # refusals the same way. This row was already vacuous at 62054fd —
        # widening the derivation is what made it visible. Narrowed to the two
        # words that identify preflight's own message; `_SHARED_SCRATCH` is
        # unchanged, because the genuine collision was always with
        # `capture_isolation_negative`'s identical sentence.
        "command", "scratch parent", recipe="scratch_parent_that_is_not",
        shared=_SHARED_SCRATCH),
    ("run", "preflight", "gate", "require_freeze"): Gate(
        "command", "registers no freeze.preregistrationSha256"),
    ("run", "preflight", "inline", "not entries"): Gate(
        "preflight", "no schedule entries were given for",
        recipe="slots_without_entries",
        why="`run` derives its entries and its slots from one expansion, so no "
            "command line reaches preflight with slots and no entries — "
            "batch.py's own comment above the §2.8 bound calls this and the "
            "index bound below it belt-and-braces. Driven at `preflight()`, "
            "which is where the claim is made."),
    ("run", "preflight", "inline",
     "entries[-1]['globalIndex'] > REGISTERED_SLOTS"): Gate(
        "preflight", "no invocation may plan a slot past the registered order",
        recipe="entries_past_the_registered_order",
        why="the same: `run_batch` slices the expansion and refuses `--runs` "
            "past what remains (`runs > len(remaining)`), so the command line "
            "cannot present preflight with an out-of-range entry. §2.8's bound "
            "is checked anyway, and is driven here at the function."),
    ("run", "preflight", "gate", "check_registry"): Gate(
        "command", "registers batch.n = ", recipe="registry_that_shrinks_n"),
    ("run", "preflight", "inline", "not os.path.isfile(cli_override)"): Gate(
        "command", "no CLI at", recipe="cli_override_that_is_not_there"),
    ("run", "preflight", "inline",
     "not _matches(override_digest, pins['codex']['binarySha256'])"): Gate(
        "command", "the CLI at ", recipe="cli_override_that_is_not_pinned"),
    ("run", "preflight", "inline", "os.path.exists(RESULTS)"): Gate(
        "command", "no slot may be created in any arm after a",
        recipe="publish_a_rate"),
    ("run", "preflight", "inline", "os.path.lexists(temporary)"): Gate(
        "command", "a previous run left the ledger's temporary behind",
        recipe="a_stale_ledger_temporary"),
    ("run", "preflight", "gate", "require_golden"): Gate(
        "command", "registers no golden.sha256"),
    ("run", "preflight", "gate", "require_isolation_negative"): Gate(
        "command",
        "§6 C7 runs before the batch and the registry records the assent"),
    ("run", "preflight", "inline", "existing"): Gate(
        "command", "already exist and are never rewritten",
        recipe="a_slot_that_already_exists"),

    # -- `run`, in `run_batch` itself: its own gate FUNCTIONS ----------------
    #
    # Round 17, finding 2. `gate_functions()` derived from `preflight()` alone,
    # so these six were in no gate set, matched nothing in `_sites_in()` and
    # produced no cell — the registered sentence said "per registered command"
    # and the derivation said "per preflight". `verify_prefix()` is the gate
    # that enforces §2.8's registered call order, which is the study's central
    # integrity claim, and it was outside the pre-call ledger entirely.
    ("run", "run_batch", "gate", "schedule_entries"): Gate(
        "residual",
        why="`schedule_entries()` carries no `raise BatchError` of its own — "
            "it is refusal-CAPABLE only through `schedule()`/`williams()`, "
            "which check the registered order's own construction — so test B "
            "has no literal of its own to pin and this cell cannot be named. "
            "It is a structural invariant over this file's own constants, not "
            "a ceremony gate: `ENTRIES = batch.schedule_entries()` at the top "
            "of this module means a refusal it could make arrives as a "
            "collection error over the whole file, not as a case."),
    ("run", "run_batch", "gate", "load_ledger"): Gate(
        "command", "a ledger is an object carrying a records list",
        recipe="a_ledger_that_is_not_an_object"),
    ("run", "run_batch", "gate", "verify_prefix"): Gate(
        "residual",
        why="§2.8's registered call order, checked against the ledger. "
            "Reaching it with every other gate met needs a ledger that loads "
            "and then diverges, which is a whole recorded batch and not a "
            "ceremony step this fixture takes. MEASURED, on a full-tree copy "
            "at 62054fd: deleting the call at all four of its sites leaves "
            "`test_a_ledger_diverging_from_the_registered_order_refuses_the_"
            "resume` red and the rest of the suite green — so it is held, "
            "unnamed, by exactly one case."),
    ("run", "run_batch", "gate", "reconcile_ledger"): Gate(
        "residual",
        why="the §2.9 crash-window reconciliation, reached only under "
            "`--resume`. Not driven by name here and not named anywhere else "
            "either: none of its refusal literals appears under harness/"
            "tests/. What holds it is `open_a_crash_window()`'s ADMITTING "
            "half — the recovery rows above run the real reconciliation and "
            "require it to complete the interrupted record — so a deletion "
            "loses the recovery, not only the refusal."),
    ("run", "run_batch", "gate", "write_ledger"): Gate(
        "residual",
        why="no `raise BatchError` of its own; it refuses only through "
            "`_write_json_atomic()` and `arm_prompt()`, so test B has no "
            "literal to pin and this cell cannot carry a name. The crash-"
            "window rows above drive the call itself, which is what makes "
            "the recovered record appear in the ledger at all."),
    ("run", "run_batch", "gate", "arm_prompt"): Gate(
        "residual",
        why="the dry-run branch prints each arm's pinned prompt. It cannot "
            "refuse with every other gate met: `check_registry()` inside "
            "preflight calls `arm_prompt()` for all five arms first, so a "
            "registry that would trip it here is refused above — the same "
            "redundant-gate shape §2.8's index bound has, and recorded for "
            "the same reason rather than left as a permanent silent green."),

    # -- `run`, in `run_batch` itself: the crash-window recovery -------------
    ("run", "run_batch", "gate", "verify_ported_bytes"): Gate(
        "command", "the ported bytes are not the registered ones",
        recipe="break_the_ported_bytes_over_a_crash_window",
        why="preflight's own copy of this gate carries the same words, so the "
            "needle alone cannot say which fired. What separates them is the "
            "LEDGER: this site stands above the recovery's `write_ledger()`, "
            "so with it deleted the interrupted record is appended before "
            "preflight refuses. Every case here asserts the ledger is byte "
            "unchanged after a refusal, and that is the assertion this row "
            "turns on."),
    ("run", "run_batch", "gate", "require_freeze"): Gate(
        "command", "registers no freeze.preregistrationSha256",
        recipe="open_a_crash_window",
        why="the same, for the freeze: one of the five call sites §7's "
            "enforcement claim rests on, and the only one whose deletion "
            "preflight's copy would otherwise mask (round 16, finding 1)."),
    ("run", "run_batch", "inline", "records and (not resume)"): Gate(
        "residual",
        why="a plain `run` over a ledger that already records slots. Held "
            "today by `test_a_batch_is_continued_with_resume_and_never_"
            "restarted`, which asserts exit 1 and that no slot was added, but "
            "not the name; converting it is the next command's work and is "
            "recorded here rather than left invisible."),
    ("run", "run_batch", "inline", "os.path.exists(RESULTS)"): Gate(
        "residual",
        why="§2.8's no-new-slots marker, on the recovery path. The same "
            "constant is driven on the slot path and the shortfall path by "
            "`test_the_published_marker_refuses_new_slots_and_a_shortfall`; "
            "reaching THIS one needs a crash window and a published rate at "
            "once, and it is not driven."),
    ("run", "run_batch", "inline", "resume and (not records)"): Gate(
        "residual",
        why="`--resume` with an empty ledger. Driven by the first half of "
            "`test_a_batch_is_continued_with_resume_and_never_restarted`, "
            "which asserts exit 1 and that the first slot was not created — "
            "unnamed, and recorded."),
    ("run", "run_batch", "inline", "not remaining"): Gate(
        "residual",
        why="the completed order: it needs 150 recorded slots, which no case "
            "in this file builds. §2.8's other end — an invocation planning "
            "past the order — is driven by `test_a_plan_that_would_reach_past_"
            "the_registered_order_refuses`."),
    ("run", "run_batch", "inline", "runs < 1"): Gate(
        "residual",
        why="`--runs 0`. Not driven, and its message is the one preflight's "
            "`not slots` gate also raises — the collision is declared on that "
            "row rather than left for a later round to find."),
    ("run", "run_batch", "inline", "runs > len(remaining)"): Gate(
        "residual",
        why="held by `test_a_plan_that_would_reach_past_the_registered_order_"
            "refuses`, which drives the registered command line and asserts "
            "exit 1 and that no slot was created — unnamed, and recorded."),

    # -- `capture`: the probe arm of the same preflight ----------------------
    ("capture", "preflight", "gate", "verify_ported_bytes"): Gate(
        "command", "the ported bytes are not the registered ones",
        recipe="break_the_ported_bytes"),
    ("capture", "preflight", "gate", "require_freeze"): Gate(
        "command", "registers no freeze.preregistrationSha256"),
    ("capture", "preflight", "inline", "not pinned"): Gate(
        "command", "registers no probePrompt.sha256",
        recipe="registry_with_no_probe_pin"),
    ("capture", "preflight", "inline", "not _matches(actual, pinned)"): Gate(
        "command", ", not the pinned ", recipe="registry_with_a_wrong_probe_pin",
        shared=(("inline", "preflight",
                 "not _matches(override_digest, "
                 "pins['codex']['binarySha256'])"),
                ("gate", "check_registry")),
        why="§3.2's probe-prompt pin, and the one gate on the `capture` path "
            "that had no negative case at all (round 16, finding 2). Its "
            "message shares `, not the pinned ` with the CLI gate above it and "
            "with `check_registry()`'s arm-prompt refusal; both are satisfied "
            "in this state, and the collision is declared rather than assumed "
            "away."),
    ("capture", "preflight", "inline", "not slots"): Gate(
        "residual",
        why="the same preflight site as `run`'s, which is driven above. "
            "`capture` reaches it through the one `preflight()` call the "
            "derivation reads, so a per-command bypass would fail test A "
            "rather than pass silently here."),
    ("capture", "preflight", "inline", "not os.path.isfile(SCRIPT)"): Gate(
        "residual", why="the same preflight site as `run`'s, driven above."),
    ("capture", "preflight", "inline",
     "not os.path.isdir(scratch_parent)"): Gate(
        "residual", why="the same preflight site as `run`'s, driven above."),
    ("capture", "preflight", "inline",
     "not os.path.isfile(cli_override)"): Gate(
        "residual", why="the same preflight site as `run`'s, driven above."),
    ("capture", "preflight", "inline",
     "not _matches(override_digest, pins['codex']['binarySha256'])"): Gate(
        "residual", why="the same preflight site as `run`'s, driven above."),
    ("capture", "preflight", "inline", "existing"): Gate(
        "residual",
        why="the same preflight site as `run`'s, driven above; a capture "
            "attempt directory is numbered, so the state is reached by hand "
            "rather than by a repeat."),
    ("capture", "run_capture", "inline", "os.path.exists(out_path)"): Gate(
        "residual",
        why="held by `test_a_registered_capture_is_never_rewritten`, which "
            "drives `capture-golden` at an existing `--out` and asserts exit "
            "1 — the same refusal string, from `capture_golden()`'s own row "
            "below, and not this one."),
    ("capture", "run_capture", "inline", "runs < MIN_CAPTURE_SLOTS"): Gate(
        "residual",
        why="held by `test_one_capture_cannot_derive_a_golden`, which drives "
            "`capture --runs 1` and asserts exit 1 before a call is spent — "
            "unnamed, and recorded."),

    # -- `capture-golden` ----------------------------------------------------
    ("capture-golden", "capture_golden", "gate", "verify_ported_bytes"): Gate(
        "command", "the ported bytes are not the registered ones",
        recipe="break_the_ported_bytes"),
    ("capture-golden", "capture_golden", "gate", "require_freeze"): Gate(
        "command", "registers no freeze.preregistrationSha256"),
    ("capture-golden", "capture_golden", "inline", "not out_path"): Gate(
        "residual",
        why="`--out` omitted. `test_capture_golden_writes_only_where_it_is_"
            "told` drives it and asserts the study's own capture is byte "
            "unchanged — the property that matters — without naming the "
            "refusal."),
    ("capture-golden", "capture_golden", "inline",
     "os.path.exists(out_path)"): Gate(
        "residual",
        why="held by `test_a_registered_capture_is_never_rewritten`; exit 1, "
            "unnamed. Its message is also `run_capture`'s, which is why that "
            "row points here."),
    ("capture-golden", "capture_golden", "inline",
     "min_slots < MIN_CAPTURE_SLOTS"): Gate(
        "residual",
        why="held by `test_the_derivation_itself_refuses_a_single_capture_"
            "slot`; exit 1, unnamed."),
    ("capture-golden", "capture_golden", "inline", "not probe_pin"): Gate(
        "residual",
        why="the same registry member the `capture` row above drives through "
            "preflight, checked a second time here because this command takes "
            "no preflight at all. Not driven."),
    ("capture-golden", "capture_golden", "inline",
     "call.get('promptKind') != 'probe' or call.get('promptSha256') "
     "!= probe_pin"): Gate(
        "residual",
        why="held by `test_a_derivation_from_registered_prompt_captures_"
            "refuses`, which builds a capture from an arm's prompt and asserts "
            "exit 1 — unnamed."),
    ("capture-golden", "capture_golden", "inline",
     "len(usable) < required"): Gate(
        "residual",
        why="held by `test_the_derivation_itself_refuses_a_single_capture_"
            "slot` and `test_two_agreeing_captures_must_be_two_calls`; exit 1, "
            "unnamed."),
    # The two §3.2 gates `capture_golden()`'s own docstring names as the ones
    # that hold it (round 17, finding 2). `capture_slots()` is the iterator of
    # a `for` loop, so it needed BOTH halves of the repair to become visible:
    # the host-relative gate set to enter the gate set at all, and the header
    # scan to produce a site once it had.
    ("capture-golden", "capture_golden", "gate", "capture_slots"): Gate(
        "command", "holds the batch slot",
        recipe="a_batch_shaped_name_among_the_captures"),
    ("capture-golden", "capture_golden", "gate",
     "require_distinct_sessions"): Gate(
        "command", "two slots holding one call's evidence",
        recipe="two_capture_slots_holding_one_call"),
    ("capture-golden", "capture_golden", "inline", "context != first"): Gate(
        "residual",
        why="held by `test_a_capture_that_does_not_reproduce_refuses_the_"
            "derivation`; exit 1, unnamed."),

    # -- `capture-isolation-negative` ----------------------------------------
    ("capture-isolation-negative", "capture_isolation_negative", "gate",
     "verify_ported_bytes"): Gate(
        "command", "the ported bytes are not the registered ones",
        recipe="break_the_ported_bytes"),
    ("capture-isolation-negative", "capture_isolation_negative", "gate",
     "require_freeze"): Gate(
        "command", "registers no freeze.preregistrationSha256"),
    ("capture-isolation-negative", "capture_isolation_negative", "gate",
     "require_golden"): Gate("command", "registers no golden.sha256"),
    ("capture-isolation-negative", "capture_isolation_negative", "inline",
     "assent != 'granted'"): Gate(
        "residual",
        why="held by `test_the_negative_control_runs_on_the_registered_assent_"
            "member_only`, which drives the command with the assent recorded "
            "at the round-3 member name and asserts exit 1 — unnamed, and its "
            "message shares its first clause with `require_isolation_"
            "negative()`'s, which is driven by name on the `run` row above."),
    ("capture-isolation-negative", "capture_isolation_negative", "inline",
     "not os.path.isdir(scratch_parent)"): Gate(
        "residual",
        why="the same words as preflight's scratch gate, which is driven on "
            "the `run` row; this command does not go through preflight, so "
            "the check is its own and is not driven."),
    ("capture-isolation-negative", "capture_isolation_negative", "inline",
     "os.path.exists(out_dir)"): Gate(
        "residual",
        why="§6 C7 runs ONCE; the record is never rewritten. Not driven — the "
            "canonical path is [D-23]'s and every case here moves the "
            "constant."),
    ("capture-isolation-negative", "capture_isolation_negative", "inline",
     "os.path.exists(raw)"): Gate(
        "residual",
        why="a scratch slot left by a previous control at the same pid. Not "
            "reachable from a command line inside one process."),

    # -- `shortfall` ---------------------------------------------------------
    ("shortfall", "declare_shortfall", "gate", "verify_ported_bytes"): Gate(
        "command", "the ported bytes are not the registered ones",
        recipe="break_the_ported_bytes"),
    ("shortfall", "declare_shortfall", "gate", "require_freeze"): Gate(
        "command", "registers no freeze.preregistrationSha256"),
    ("shortfall", "declare_shortfall", "inline",
     "os.path.exists(RESULTS)"): Gate(
        "residual",
        why="held by `test_the_published_marker_refuses_new_slots_and_a_"
            "shortfall`, which drives it AND its counterfactual — exit 1 with "
            "no declaration written, then exit 0 once the marker is gone. "
            "Unnamed, and the only residual here with an admitting half."),
    ("shortfall", "declare_shortfall", "inline",
     "os.path.exists(out_path)"): Gate(
        "residual",
        why="held by `test_a_shortfall_is_declared_once_and_names_a_reason`; "
            "exit 1, unnamed. Its message is `%s already exists`, which "
            "`capture_isolation_negative()`'s raw-slot gate also raises."),
    ("shortfall", "declare_shortfall", "inline", "not reason"): Gate(
        "residual",
        why="`--reason` omitted. Driven by `test_a_shortfall_is_declared_once_"
            "and_names_a_reason`, which gives the command line without "
            "`--reason` and asserts exit 1 with no declaration written, then "
            "the admitting half — unnamed, and recorded. Measured: deleting "
            "this gate turns that case red on its own, which is why the "
            "residual rows are not the same thing as uncovered gates."),
    ("shortfall", "declare_shortfall", "inline",
     "present >= REGISTERED_SLOTS"): Gate(
        "residual",
        why="held by `test_a_shortfall_may_not_be_declared_over_a_batch_that_"
            "is_not_short`, which puts the whole registered order on disk and "
            "asserts exit 1 with no declaration written — unnamed."),
    ("shortfall", "declare_shortfall", "inline",
     "present != len(records)"): Gate(
        "residual",
        why="held by `test_a_shortfall_refuses_when_the_slots_and_the_ledger_"
            "disagree`; exit 1, unnamed."),
    # `declare_shortfall()`'s own gate FUNCTIONS — the same five `run_batch`
    # runs, over the same ledger, and outside this ledger for the same reason
    # until round 17, finding 2.
    ("shortfall", "declare_shortfall", "gate", "schedule_entries"): Gate(
        "residual",
        why="the same structural invariant as `run`'s row above: no `raise "
            "BatchError` of its own, so no needle to pin, and it is exercised "
            "at this module's own import rather than by a case."),
    ("shortfall", "declare_shortfall", "gate", "load_ledger"): Gate(
        "command", "a ledger is an object carrying a records list",
        recipe="a_ledger_that_is_not_an_object"),
    ("shortfall", "declare_shortfall", "gate", "verify_prefix"): Gate(
        "residual",
        why="the same gate as `run`'s row above, at the shortfall's own call "
            "site, and held the same way: MEASURED at 62054fd, deleting it at "
            "all four sites leaves one case red and it is a `run` case, so "
            "this site is held by nothing of its own."),
    ("shortfall", "declare_shortfall", "gate", "reconcile_ledger"): Gate(
        "residual",
        why="the shortfall reconciles the ledger with the slots before it "
            "declares anything (round 6, finding 6). Not named: none of its "
            "refusal literals appears under harness/tests/. What holds the "
            "call is `test_a_shortfall_refuses_when_the_slots_and_the_ledger_"
            "disagree` and the crash-window declaration case, which need the "
            "reconciliation to have run to reach their own assertions."),
    ("shortfall", "declare_shortfall", "gate", "write_ledger"): Gate(
        "residual",
        why="no `raise BatchError` of its own, so no needle; and it is "
            "reached only when the reconciliation recovered a record, which "
            "is the crash-window state the declaration cases build."),
}

# The census the record quotes. `PRE_CALL_GATES` is checked against the
# derivation in both directions; this is checked against `PRE_CALL_GATES` and
# against the derivation, so a disposition sentence citing these numbers cites
# a value the suite maintains rather than one someone counted by hand.
#
# Round 17, finding 8 is why it exists. Round 16's record said "thirty-one of
# fifty-seven derived cells are residual" for a ledger that the same commit had
# already made fifty-eight — a hand count taken mid-work and never retaken, in
# the one direction nobody checks because it understates the author's own
# coverage. The recurring defect across rounds 15, 16 and 17 is not a
# direction; it is a sentence about a DERIVED artifact, written by hand.
LEDGER_CENSUS = {"cells": 82, "command": 40, "preflight": 3, "residual": 39}


@unittest.skipUnless(
    RUNNING_REGISTERED,
    "the wrapper refuses an interpreter harness/PINS.json does not register "
    "(§2.10), so no wrapper-driven case can run here")
class PreCallGates(BatchFixture):
    """§7's claim that no call is spent before every registered precondition
    holds — as a property of the SUITE and not of one gate at a time.

    WHAT THIS CAN SHOW.
      * Deleting any ledgered gate call turns the suite red. With that gate
        alone unmet the command either runs to a slot or refuses with another
        gate's words, and the named assertion catches both.
      * A gate added to `main()`, to `preflight()` or to a command entry, or a
        command that starts calling one, is a key the derivation produces and
        the ledger does not: test A fails and names it. This bullet used to say
        the same thing and was HALF FALSE, which is round 17 finding 2's
        subject. An INLINE `if …: raise BatchError(…)` added to a command entry
        was caught by name — verified — but a gate written the ordinary way, as
        `require_x(…)`, was not: the gate set was derived from `preflight()`'s
        callees alone, so an entry's own gate call matched nothing and produced
        no cell. Measured at 62054fd: a refusing `require_absolute_scratch()`
        added to `run_batch()` above its first `invoke()` left the derived set
        unchanged at 58 and the whole suite at 309 passed. Round 16's own new
        gate happened to be inline, which is why the mechanism looked as though
        it worked. The gate set is host-relative now, `main()` is a host, and
        compound-statement headers are scanned — 58 cells to 82.
      * Rewording a refusal fails test B. That is deliberate. The message is
        the only thing that says WHICH gate refused, and every claim here rests
        on it.
      * Moving a gate below the first `invoke()` takes its cell out of the
        derived set, which fails test A, and spends a call, which fails the
        `calls_made()` invariant every case carries.

    WHAT THIS CANNOT SHOW, so that it is not read as a proof.
      * It says nothing about a gate being CORRECT. An inverted predicate still
        fires on a fixture built to trip it, which is why every driven row also
        carries an admitting half.
      * It sees statically resolved calls to module-level names in `batch.py`
        only. `integrity.verify()` is in scope because `verify_ported_bytes()`
        wraps it; `transcription/authoring_call.sh`'s own gates are outside it
        entirely, the same Python-only residual round 15 recorded for the
        writer scan. An ATTRIBUTE-spelled callee is outside it too, and that is
        load-bearing now rather than theoretical: round 17 finding 1's
        `score_rates.require_lawful_destination()` calls in `capture_golden()`
        and `capture_isolation_negative()` are gates by every other definition
        used here and produce no cell, because they are `score_rates.x(…)` and
        not `x(…)`. They are held by
        `test_manifest.py`'s `PARAMETER_ROOTS` behavioural pairs instead, which
        is named here so the next round does not read this ledger as covering
        them.
      * GATE DEPTH IS ONE, and literal attribution is one level shallower
        still. A gate function owns its cell as a black box, so a refusal
        raised inside a gate's own callee — `verify_chain()` inside
        `load_ledger()`, `slot_outcome()`/`verify_seal_of()` inside
        `reconcile_ledger()`, `_write_json_atomic()`/`arm_prompt()` inside
        `write_ledger()`, `schedule()`/`williams()` inside
        `schedule_entries()` — is inside a ledgered cell and invisible to test
        B. That is why `schedule_entries` and `write_ledger` are residual rows:
        they carry no `raise BatchError` of their own, so there is no needle
        that could name them.
      * THE PRE-CALL BOUND IS TEXTUAL, NOT EXECUTIONAL. `line >= first_call`
        is a source-order bound. `run_batch()`'s dry-run branch returns before
        the loop, so its `arm_prompt()` call is pre-call in execution and
        pre-call by line — but a gate placed textually below the first
        `invoke()` on a branch that returns first would be missed, and one
        placed textually above it on a path that never runs would be counted.
      * It cannot tell a redundant gate from a load-bearing one. §2.8's index
        bound is checked after `run_batch` has already bounded the slice, and
        `batch.py` says so itself; such rows carry a `why` naming the gate
        above them, or they would be permanent silent green.
      * It is author-VISIBLE, not author-proof. Deleting a gate AND its ledger
        row is green. What it converts is a silent deletion into an edit of the
        file whose only job is to record the gate set — a diff a reviewer sees.
      * It says nothing about ORDER beyond "above the first call". §6 C7's "the
        control ran BEFORE the batch" is a separate property, held by the
        control's own record and not by this.
      * It is a claim about `batch.py`'s pre-call region. §7's other
        enforcement bullets are untouched by it. The bullet that used to stand
        here said the same of `score_rates.verify_preconditions()` — "the
        scorer's own ordered table in `test_admission.py` is hand-kept and has
        the same silent-omission property" — which was honest and which round
        17 finding 3 measured: TWELVE of that function's twenty-three refusal
        sites could be removed together with the suite green, against a record
        that said three. It is mirrored now. `test_admission.py`'s
        `PRE_READ_GATES` is the scorer's twenty-five cells, derived through the
        same `gatescan.py` this file uses, so the derivation exists once and a
        third site — `collect_slots`, `terminality`, `load_ledger` and
        `check_population` run twenty more refusal sites before `score()` reads
        a slot — costs a table rather than a rewrite. That third site is NOT
        covered; it is named there and here rather than left for round 18.
    """

    def setUp(self):
        super().setUp()
        self.undo = []
        # Overrides the ADMITTING drive keeps — a recipe that reaches its state
        # through a flag (`--resume` over a crash window) says so here, because
        # dropping that flag would make the admitting half a different command.
        self.keep = {}
        # The study at README step 2: ported bytes verified, wrapper on disk,
        # CLI pinned — and none of steps 3, 4 and 5 taken. Each ceremony act in
        # `SATISFY` is one of those steps, so "this gate alone unmet" is
        # "this step alone not taken".
        pins = json.loads(json.dumps(self.pins))
        pins["freeze"]["preregistrationSha256"] = None
        self.write_pins(pins)
        # `shortfall` writes into the population root the batch creates, so the
        # root exists here as it would after any batch. It is not a gate — no
        # `raise BatchError` guards it — and the derivation therefore never
        # sees it.
        os.makedirs(self.arms_root, exist_ok=True)
        # The capture is a file from the start and its PIN is the ceremony act:
        # §6 C7's record is written with the capture's digest, so a state where
        # the capture does not exist at all cannot also carry a C7 record, and
        # the gate under test would not be the only unmet one.
        with open(self.golden, "w") as handle:
            json.dump({"contextVersion": "1", "entries": [],
                       "capturedFrom": ["a stand-in for the §3.2 capture"]},
                      handle)

    def fresh(self):
        """One cell's fixture, from scratch. `doCleanups()` unwinds the last
        cell's throwaway root, patched constants and stand-in HOME, and
        `setUp()` builds the next — so no cell can be satisfied by a state
        another cell left behind."""
        for undo in reversed(self.undo):
            undo()
        self.undo = []
        self.doCleanups()
        self.setUp()

    # --- the ceremony acts, one per gate that has one -----------------------

    def satisfied_by_the_fixture(self):
        """The stand-in study already meets this gate: the committed wrapper is
        on disk, the scratch parent is a directory, the CLI is the one the
        stand-in registry pins, no rate is published and no slot exists. Such a
        gate is broken by its row's `recipe`, never by omission."""

    def freeze_the_preregistration(self):
        """README step 3."""
        pins = json.loads(json.dumps(self.pins))
        pins["freeze"]["preregistrationSha256"] = batch._digest(
            os.path.join(STUDY, "PREREGISTRATION.md"))
        self.write_pins(pins)

    def register_the_golden(self):
        """README step 4's second half: the capture's digest replaces the null.
        The capture itself is on disk from `setUp`."""
        self.register_golden()

    def grant_the_assent(self):
        """README step 5's authorization, without the record — which is what
        `capture-isolation-negative` needs before it may run at all."""
        pins = json.loads(json.dumps(self.pins))
        pins["isolationNegative"]["assent"] = "granted"
        self.write_pins(pins)

    def capture_two_agreeing_probes(self):
        """The §3.2 recapture, run for real, so `capture-golden` has an attempt
        directory to derive from. Two calls of the stand-in CLI.

        The recapture is itself gated on the freeze, so this act freezes for
        the length of its own two calls and puts the pin back where it found
        it. That is the ceremony's real order — step 3 precedes step 4 — and
        without it the freeze gate could not be the ONE unmet gate of a
        `capture-golden` that has slots to derive from."""
        before = self.pins["freeze"]["preregistrationSha256"]
        self.freeze_the_preregistration()
        self.assertEqual(self.capture(out=os.path.join(self.root, "FIRST.json")),
                         0)
        pins = json.loads(json.dumps(self.pins))
        pins["freeze"]["preregistrationSha256"] = before
        self.write_pins(pins)

    # --- the break recipes --------------------------------------------------

    def break_the_ported_bytes(self) -> dict:
        def refuse(*arguments, **keywords):
            raise integrity.IntegrityError("harness/policy_mirror.py is sha256:dead…")

        patched = mock.patch.object(integrity, "verify", refuse)
        patched.start()
        self.undo.append(patched.stop)
        return {}

    def open_a_crash_window(self) -> dict:
        """A slot sealed and not yet in the ledger — §2.9's kill window, which
        is the only state that reaches `run_batch`'s own copies of the ported
        bytes and freeze gates. Built by running the REAL driver and dropping
        the tail record, so the slot on disk was sealed by the driver."""
        self.freeze_the_preregistration()
        self.register_the_golden()
        self.record_negative_control()
        self.assertEqual(self.run_batch(["--runs", "2"]), 0)
        path = os.path.join(self.arms_root, "BATCH.json")
        with open(path) as handle:
            ledger = json.load(handle)
        ledger["records"] = ledger["records"][:1]
        with open(path, "w") as handle:
            json.dump(ledger, handle, indent=2)
        # …and back to step 2, so the gate under test is the unmet one again.
        pins = json.loads(json.dumps(self.pins))
        pins["freeze"]["preregistrationSha256"] = None
        self.write_pins(pins)
        self.undo.append(self.freeze_the_preregistration)
        # The admitting drive keeps `--resume`: without it the same command
        # line means "restart a recorded batch", which is a different refusal.
        self.keep = {"extra": ["--resume"]}
        return {"extra": ["--resume"]}

    def break_the_ported_bytes_over_a_crash_window(self) -> dict:
        overrides = self.open_a_crash_window()
        self.freeze_the_preregistration()
        self.break_the_ported_bytes()
        return overrides

    def empty_slot_list(self) -> dict:
        return {"entries": ENTRIES[:1], "slots": []}

    def slots_without_entries(self) -> dict:
        return {"entries": [], "slots": [batch.slot_path(ENTRIES[0])]}

    def entries_past_the_registered_order(self) -> dict:
        past = dict(ENTRIES[0], globalIndex=batch.REGISTERED_SLOTS + 1)
        return {"entries": [past], "slots": [batch.slot_path(past)]}

    def hide_the_wrapper(self) -> dict:
        patched = mock.patch.object(batch, "SCRIPT",
                                    os.path.join(self.root, "no-wrapper.sh"))
        patched.start()
        self.undo.append(patched.stop)
        return {}

    def scratch_parent_that_is_not(self) -> dict:
        return {"scratch": os.path.join(self.root, "no-such-scratch")}

    def registry_that_shrinks_n(self) -> dict:
        return {"pins": self.alternate_registry(
            "PINS-n25.json", batch=dict(self.pins["batch"], n=25))}

    def registry_with_no_probe_pin(self) -> dict:
        return {"pins": self.alternate_registry("PINS-no-probe.json",
                                                probePrompt={"sha256": None})}

    def registry_with_a_wrong_probe_pin(self) -> dict:
        return {"pins": self.alternate_registry(
            "PINS-probe.json", probePrompt={"sha256": "sha256:" + "7" * 64})}

    def cli_override_that_is_not_there(self) -> dict:
        return {"cli": os.path.join(self.root, "no-such-cli")}

    def cli_override_that_is_not_pinned(self) -> dict:
        return {"cli": self.unpinned_cli()}

    def publish_a_rate(self) -> dict:
        with open(batch.RESULTS, "w") as handle:
            handle.write("{}\n")
        self.undo.append(lambda: os.unlink(batch.RESULTS))
        return {}

    def a_stale_ledger_temporary(self) -> dict:
        path = os.path.join(self.arms_root, batch.LEDGER_TEMP_NAME)
        with open(path, "w") as handle:
            handle.write("half a ledger a kill left behind\n")
        self.undo.append(lambda: os.unlink(path))
        return {}

    def a_slot_that_already_exists(self) -> dict:
        slot = self.slot(0)
        os.makedirs(os.path.dirname(slot))
        os.symlink(os.path.join(self.root, "nowhere"), slot)
        self.undo.append(lambda: shutil.rmtree(self.arms_root, True))
        return {}

    # --- the recipes for `main()`'s own pre-dispatch region ------------------
    #
    # Round 17, finding 2, step 8. `main()` was never a host of this
    # derivation: `command_entries()` read it only to learn the five entry
    # names, so eleven gates the operator meets FIRST — before any entry
    # function is reached — were outside the ledger, and none of their refusal
    # strings appears anywhere else under harness/tests/. They are gates by the
    # same definition as every other row here: a `raise BatchError` above the
    # first spent call.

    def a_flag_given_without_its_value(self) -> dict:
        """`--pins` last on the line and nothing after it. Every command reads
        `--pins` through `_argument()` before it does anything else, so this is
        one recipe for all five and it lands on the unguarded call site the
        cell's line names."""
        return {"bare": "--pins"}

    def a_command_line_with_no_scratch_parent(self) -> dict:
        """The flag is REMOVED, not emptied: `--scratch-parent` with no value
        is `_argument()`'s refusal one gate earlier, and this row is about the
        one below it."""
        return {"drop": ("--scratch-parent",)}

    def a_command_line_with_no_slots_directory(self) -> dict:
        """`capture-golden`'s own required flag, the same way."""
        return {"drop": ("--slots",)}

    def a_flag_a_registered_decision_removed(self) -> dict:
        """[D-23] removed `--slots` from the population-naming surface, and
        [D-22] removed `--start`. A command line that still carries one means
        something the driver no longer does, so it refuses by name instead of
        being ignored — for `run` and `shortfall`, which are the two commands
        that check."""
        return {"extra": ["--slots", "an argument [D-23] removed"]}

    # --- the recipes for the command entries' own gates ----------------------

    def a_ledger_that_is_not_an_object(self) -> dict:
        """`BATCH.json` holding `[]`. It decodes, and `load_ledger()` refuses
        it by type before any record is read — round 8 finding 9's traceback,
        now the driver's own registered refusal. Both `run` and `shortfall`
        load the ledger before they use it, and the file is left exactly as
        planted, so the "the refused command moved the ledger" assertion is
        live rather than vacuous on a missing file."""
        path = os.path.join(self.arms_root, "BATCH.json")
        with open(path, "w") as handle:
            handle.write("[]\n")
        self.undo.append(lambda: os.unlink(path))
        return {}

    def a_batch_shaped_name_among_the_captures(self) -> dict:
        """A `run-NNN` directory in the capture attempt. `capture_slots()` is
        the gate `batch.py`'s own docstring names as the one that keeps a
        golden capture from being derived from the batch's own runs (§3.2 step
        2), and it was invisible to this ledger until compound-statement
        headers were scanned — it is the iterator of a `for` loop."""
        path = os.path.join(self.attempt(), "run-001")
        os.makedirs(path)
        self.undo.append(lambda: shutil.rmtree(path, True))
        return {}

    def two_capture_slots_holding_one_call(self) -> dict:
        """A third capture slot that is a COPY of one of the two the recapture
        made. Its context agrees perfectly — by construction rather than by
        reproduction, which is the whole distinction §3.2 rests on — so it is
        `require_distinct_sessions()` and nothing else that refuses."""
        slots = sorted(name for name in os.listdir(self.attempt())
                       if os.path.isdir(os.path.join(self.attempt(), name)))
        path = os.path.join(self.attempt(), "copy-of-%s" % slots[0])
        shutil.copytree(os.path.join(self.attempt(), slots[0]), path)
        self.undo.append(lambda: shutil.rmtree(path, True))
        return {}

    # --- driving one registered command line --------------------------------

    def command_line(self, command: str, **overrides) -> list:
        scratch = overrides.get("scratch", self.scratch)
        pins = overrides.get("pins", self.pins_path)
        cli = overrides.get("cli", self.cli)
        extra = list(overrides.get("extra", ()))
        if command == "run":
            line = ["batch.py", "run", "--scratch-parent", scratch,
                    "--pins", pins, "--golden", self.golden,
                    "--cli-override", cli, "--runs", "1"] + extra
        elif command == "capture":
            line = ["batch.py", "capture", "--scratch-parent", scratch,
                    "--captures", self.captures, "--out", self.artifact(command),
                    "--pins", pins, "--cli-override", cli] + extra
        elif command == "capture-golden":
            line = ["batch.py", "capture-golden", "--pins", pins,
                    "--slots", self.attempt(), "--out",
                    self.artifact(command)] + extra
        elif command == "capture-isolation-negative":
            line = ["batch.py", "capture-isolation-negative",
                    "--scratch-parent", scratch, "--out", self.artifact(command),
                    "--pins", pins, "--golden", self.golden,
                    "--cli-override", cli] + extra
        else:
            line = ["batch.py", "shortfall", "--reason",
                    "the stand-in CLI batch was cut short on purpose",
                    "--pins", pins] + extra
        # `main()`'s own pre-dispatch gates are about the SHAPE of the command
        # line rather than about a value in it, so their recipes take a flag
        # away (round 17, finding 2, step 8). `drop` removes a flag and its
        # value — which is what "--scratch-parent is required" refuses — and
        # `bare` leaves the flag at the end of the line with nothing after it,
        # which is what `_argument()` refuses. Neither is expressible as a
        # substitution, which is why the other recipes could not reach main().
        for flag in overrides.get("drop", ()):
            index = line.index(flag)
            del line[index:index + 2]
        bare = overrides.get("bare")
        if bare is not None:
            index = line.index(bare)
            del line[index:index + 2]
            line.append(bare)
        return line

    def artifact(self, command: str) -> str:
        """The one path the command would have written. Every refusing case
        asserts it is absent, which is the "and nothing was made" half of
        "before a call is spent"."""
        if command == "run":
            return self.slot(0)
        if command == "capture":
            return os.path.join(self.root, "CAPTURED.json")
        if command == "capture-golden":
            return os.path.join(self.root, "DERIVED.json")
        if command == "capture-isolation-negative":
            return os.path.join(self.root, "c7-record")
        return os.path.join(self.arms_root, "SHORTFALL.json")

    def ledger_bytes(self):
        path = os.path.join(self.arms_root, "BATCH.json")
        if not os.path.exists(path):
            return None
        with open(path, "rb") as handle:
            return handle.read()

    def drive(self, command: str, **overrides) -> tuple:
        """(exit status, stderr) for one registered command line. `batch.main()`
        prints every `BatchError` as `refused: …` and returns 1, so this is the
        operator's own view of the refusal and not an exception a test caught
        inside the module."""
        captured = io.StringIO()
        with contextlib.redirect_stderr(captured), \
                contextlib.redirect_stdout(io.StringIO()):
            status = batch.main(self.command_line(command, **overrides))
        return status, captured.getvalue()

    def ladder(self, command: str) -> list:
        """The gates this command runs, in the order `batch.py` runs them."""
        derived = derived_pre_call_gates()
        return [key[1:] for key, _line in
                sorted(((key, line) for key, line in derived.items()
                        if key[0] == command),
                       key=lambda row: (row[0][1] != "preflight", row[1]))]

    # --- A: the ledger is the derivation ------------------------------------

    def test_the_ledger_names_exactly_the_gates_the_driver_runs(self):
        """The omission test, in both directions.

        A gate added to `preflight()` or to a command entry above its first
        call, or an existing gate reached by a command that did not reach it
        before, is a key here that `PRE_CALL_GATES` does not carry — and a row
        naming a gate the driver no longer runs is a key the derivation does
        not produce. Either is a failure that names the cell. This is the test
        that makes the other two total rather than a list someone kept."""
        derived = set(derived_pre_call_gates())
        self.assertEqual(
            derived - set(PRE_CALL_GATES), set(),
            "batch.py runs these gates before a call and PRE_CALL_GATES does "
            "not record them")
        self.assertEqual(
            set(PRE_CALL_GATES) - derived, set(),
            "PRE_CALL_GATES records gates batch.py does not run before a call")
        # …and the derivation is live, not an empty set agreeing with an empty
        # table: every registered command carries gates, and BOTH halves of
        # the gate set are pinned. `preflight()`'s five were the whole of it
        # until round 17, finding 2; the union across every host is fourteen,
        # and pinning only the five is how the widening could be reverted with
        # the suite green.
        self.assertEqual(sorted({key[0] for key in derived}),
                         sorted(batch.COMMANDS))
        self.assertEqual(gate_functions("preflight"),
                         ("check_registry", "require_freeze", "require_golden",
                          "require_isolation_negative", "verify_ported_bytes"))
        self.assertEqual(
            all_gate_functions(),
            ("_argument", "arm_prompt", "capture_slots", "check_registry",
             "load_ledger", "reconcile_ledger", "require_distinct_sessions",
             "require_freeze", "require_golden", "require_isolation_negative",
             "schedule_entries", "verify_ported_bytes", "verify_prefix",
             "write_ledger"))
        # …and every host is a host: `main()` was read for its dispatch and
        # never walked, which is how eleven of its own refusals stayed out of
        # the ledger, so the host set is asserted too.
        self.assertEqual(sorted(hosts()),
                         ["capture_golden", "capture_isolation_negative",
                          "declare_shortfall", "main", "preflight",
                          "run_batch", "run_capture"])

    def test_every_derived_gate_has_a_way_to_satisfy_it(self):
        """The ladder that makes the behavioural test constructible is derived
        too: every gate the driver runs before a call carries a ceremony act
        that meets it, so a new gate arrives with a way to SATISFY it and not
        only with a way to break it. Without this, "every other gate satisfied"
        would quietly become "every other gate this file happens to know"."""
        sites = {key[1:] for key in derived_pre_call_gates()}
        self.assertEqual(sites - set(SATISFY), set(),
                         "these gates have no act in SATISFY")
        self.assertEqual(set(SATISFY) - sites, set(),
                         "SATISFY carries acts for gates the driver does not "
                         "run before a call")
        for site, act in sorted(SATISFY.items()):
            self.assertTrue(callable(getattr(self, act, None)),
                            "%r names no act on this fixture" % (site,))

    def test_every_ledger_row_is_driven_or_says_why_not(self):
        """A residual is a DECLARED gap. A row that drives nothing has to say
        what holds the gate today, so the residue is named in the file the
        reviewer reads rather than being the absence of a case."""
        for key, row in sorted(PRE_CALL_GATES.items()):
            with self.subTest(gate=key):
                self.assertIn(row.how, ("command", "preflight", "residual"))
                if row.how == "residual":
                    self.assertIsNone(row.named)
                    self.assertTrue(row.why and len(row.why) > 40, key)
                else:
                    self.assertTrue(row.named, key)
                    if row.how == "preflight":
                        self.assertTrue(row.why, key)

    def test_the_census_the_record_quotes_is_derived_not_counted(self):
        """The numbers a disposition sentence is allowed to state.

        A hand count of a derived set is the one thing this class exists to
        make impossible, and round 16's own record took one (round 17, finding
        8). Both directions: the census matches the ledger, and the ledger
        matches the derivation, so the four numbers cannot drift from the code
        without a named failure here."""
        counted = {"cells": len(PRE_CALL_GATES)}
        for how in ("command", "preflight", "residual"):
            counted[how] = sum(1 for row in PRE_CALL_GATES.values()
                               if row.how == how)
        self.assertEqual(counted, LEDGER_CENSUS)
        self.assertEqual(len(derived_pre_call_gates()), LEDGER_CENSUS["cells"])
        self.assertEqual(sum(LEDGER_CENSUS[how] for how in
                             ("command", "preflight", "residual")),
                         LEDGER_CENSUS["cells"])

    # --- B: the needle is that gate's own refusal ---------------------------

    def test_every_named_refusal_is_one_the_gate_actually_raises(self):
        """The spelling test. A needle that no `raise BatchError` in that gate
        carries would make its case pass for the wrong reason, and a needle a
        SECOND gate also raises is how a case goes vacuous — which is the
        defect this whole ledger is a repair of, one layer up. Both are read
        out of `batch.py`'s own source.

        The `shared` field is the honest form of the second half: where two
        gates genuinely spell one refusal the same way, the ledger records
        exactly which, and a NEW collision fails here."""
        literals = gate_refusal_literals()
        for key, row in sorted(PRE_CALL_GATES.items()):
            if row.how == "residual":
                continue
            site = gate_identity(key[1:])
            with self.subTest(gate=key):
                own = literals.get(site, ())
                self.assertTrue(own, "%r raises no BatchError this scan can "
                                     "read" % (site,))
                self.assertTrue(
                    any(row.named in text for text in own),
                    "%r is not a fragment of any refusal %r raises: %r"
                    % (row.named, site, own))
                carriers = {other for other, texts in literals.items()
                            if any(row.named in text for text in texts)
                            and other != site}
                self.assertEqual(
                    carriers, set(row.shared),
                    "%r is also raised by %r; a needle a second gate can "
                    "supply cannot say which gate refused"
                    % (row.named, sorted(carriers - set(row.shared))))

    # --- C: the gate refuses, by name, before anything happens --------------

    def test_each_gate_refuses_by_name_with_every_other_gate_satisfied(self):
        """The behavioural half, one subtest per driven cell.

        For each, the ceremony is taken up to the point where this gate — and
        only this gate — is unmet, the registered command line is given, and
        the run has to refuse BY THIS GATE'S NAME, spend no call, write no
        artifact and leave the ledger byte unchanged. Then the gate is
        satisfied and the same command line has to ADMIT, because a gate that
        refuses everything proves nothing.

        This is what a deleted gate call fails: with every other precondition
        met the command does not refuse for someone else's reason, it runs.
        """
        for key, row in sorted(PRE_CALL_GATES.items()):
            if row.how == "residual":
                continue
            command, site = key[0], key[1:]
            with self.subTest(gate=key):
                self.fresh()
                for other in self.ladder(command):
                    # The omitted ceremony act IS the break — and it is omitted
                    # wherever it appears, because one registered step can meet
                    # more than one gate (§2.10's freeze is checked in
                    # `preflight()` and again in `run_batch()`'s recovery) and
                    # a step half-taken is not a state the ceremony has.
                    if row.recipe is None and SATISFY[other] == SATISFY[site]:
                        continue
                    getattr(self, SATISFY[other])()
                overrides = (getattr(self, row.recipe)() if row.recipe else {})
                if row.how == "preflight":
                    self.refuses_at_preflight(row, overrides)
                    continue
                artifact = self.artifact(command)
                before = (self.calls_made(), self.ledger_bytes(),
                          os.path.lexists(artifact), os.path.isdir(artifact))
                status, stderr = self.drive(command, **overrides)
                self.assertEqual(status, 1, stderr)
                self.assertIn(row.named, stderr)
                self.assertEqual(self.calls_made(), before[0], "a call was spent")
                self.assertEqual(self.ledger_bytes(), before[1],
                                 "the refused command moved the ledger")
                # Nothing the command would have written appeared, and nothing
                # that was already there changed shape. "Absent" is the usual
                # case; the two rows that build a crash window, and the one
                # that plants a dangling link at a planned slot, start from a
                # state the command must also leave alone.
                self.assertEqual((os.path.lexists(artifact),
                                  os.path.isdir(artifact)), before[2:],
                                 "the refused command wrote its artifact")
                # …and the admitting half.
                for undo in reversed(self.undo):
                    undo()
                self.undo = []
                if row.recipe is None:
                    getattr(self, SATISFY[site])()
                status, stderr = self.drive(command, **self.keep)
                self.assertEqual(status, 0, stderr)
                self.assertTrue(os.path.lexists(artifact))

    def refuses_at_preflight(self, row, overrides: dict) -> None:
        """The three gates no registered command line can reach, because a
        gate in `run_batch` refuses the same command first. Driven at
        `preflight()` itself, where the claim is made — the row's `why` names
        the gate above it, so a redundant gate is recorded as redundant rather
        than sitting green forever."""
        spent = self.calls_made()
        with self.assertRaises(batch.BatchError) as caught:
            batch.preflight(overrides["entries"], overrides["slots"],
                            self.scratch, self.pins_path, self.cli,
                            "registered", self.golden)
        self.assertIn(row.named, str(caught.exception))
        self.assertEqual(self.calls_made(), spent)
        self.assertFalse(os.path.exists(self.slot(0)))
        # The admitting half, at the same function: the registered slice.
        self.assertTrue(batch.preflight(
            ENTRIES[:1], [batch.slot_path(ENTRIES[0])], self.scratch,
            self.pins_path, self.cli, "registered", self.golden))


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
        scoring, which no test runs: the registered interface publishes into
        the study itself and its preconditions bind committed artifacts no
        fixture owns (§2.10). A list kept by hand in this file would agree with
        the writer only until someone changed one of them.
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
        stamped on one date, and the block says so — and establishes NOTHING,
        because five slots are not the registered 150. Round 11, finding 6: the
        property is over the whole batch, so a prefix publishes its date set and
        reports the one-day rule as not established, exactly as the realised
        transition census beside it is published and not claimed. It carries no
        `ci95` and no rate, which is why §4.3's registered scope above is
        unchanged by it — this is a date, not a measurement.
        """
        block = self.results["schedule"]["utcDay"]
        complete = self.results["schedule"]["complete"]
        self.assertEqual(block, score_rates.utc_day(self.results["runs"],
                                                    complete))
        self.assertEqual(block["dates"], ["2026-08-07"])
        self.assertEqual(block["slotsWithoutReadableStamps"], 0)
        self.assertIs(block["crossedMidnight"], False)
        # The reason the flag is False, NAMED rather than left to the reader:
        # this is a five-slot prefix of a 150-slot schedule.
        self.assertIs(complete, False)
        self.assertIs(block["oneDayEstablished"], False)
        # …and not stuck False. The same rows over a complete batch establish
        # it, so only the completeness conjunct moved.
        self.assertIs(score_rates.utc_day(self.results["runs"],
                                          True)["oneDayEstablished"], True)
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
