#!/usr/bin/env python3
"""The batch driver end to end, against a stand-in CLI and a stand-in operator
HOME.

The real wrapper runs: the same bash, the same `env -i` scrub, the same fresh
HOME and CODEX_HOME per run, the same binary-digest check (the stand-in's
digest is pinned in a test registry, so the check passes because it was
satisfied, not because it was skipped), the same slot retention, and the real
§3.2 recapture with the probe prompt. Only the binary and the operator's home
are stand-ins, and neither reaches a network or a model.

What this proves that a unit test cannot: that a failing run terminates its own
slot with a refusal record and the batch CONTINUES — the registered difference
from Study 010 — that an admissible run whose completion holds no array is
counted as a valid authoring-empty run rather than dropped, that the slots the
wrapper writes are the slots the scorer reads all the way to the rate table,
that C6's per-run isolation evidence carries information in BOTH branches
(credential and no credential), that no retained byte carries the credential,
that the batch cannot create a slot before the golden capture is registered,
and that §6 C7 retains three files and deletes the transcript itself.

`$HOME` is redirected to a throwaway directory for every wrapper-driven case,
so the operator's real credential is never copied anywhere by the suite.
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
import unittest
from unittest import mock

import batch
import fixtures
import score_rates

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(os.path.dirname(HERE))

# Plan: two probe captures for the golden recapture, then the batch — two
# identical completions, one that also reaches the boundary class, one that
# holds no array at all, and one failure.
PLAN = [
    {"completion": "ready"},
    {"completion": "ready"},
    {"completion": fixtures.COMPLETION_A},
    {"completion": fixtures.COMPLETION_B},
    {"completion": fixtures.COMPLETION_A},
    {"completion": fixtures.COMPLETION_EMPTY},
    {"completion": fixtures.COMPLETION_A, "exit": 3},
]
BATCH_RUNS = 5


class Batch(unittest.TestCase):

    def setUp(self):
        import shutil
        import tempfile
        self.root = tempfile.mkdtemp(prefix="s011-batch-")
        self.addCleanup(shutil.rmtree, self.root, True)
        self.scratch = os.path.join(self.root, "scratch")
        os.makedirs(self.scratch)
        # The operator's HOME, stood in for: a credential with a sentinel
        # value and no skills tree. Every wrapper call in this file copies
        # THIS credential, never the real one.
        self.home = fixtures.write_operator_home(os.path.join(self.root, "home"))
        self.environment = mock.patch.dict(os.environ, {"HOME": self.home})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.cli = fixtures.write_fake_cli(os.path.join(self.root, "cli"), PLAN,
                                           sys.executable, HERE)
        with open(os.path.join(STUDY, "harness", "PINS.json")) as handle:
            pins = json.load(handle)
        pins["codex"]["binarySha256"] = batch._digest(self.cli)
        pins["codex"]["version"] = "codex-cli 0.145.0-fake"
        pins["batch"]["runs"] = BATCH_RUNS
        # §2.6: no call is made under a registry whose freeze digest is null,
        # so the stand-in registry carries the digest this file actually has.
        pins["preregistration"]["sha256"] = batch._digest(
            os.path.join(STUDY, "PREREGISTRATION.md"))
        self.pins_path = os.path.join(self.root, "PINS.json")
        self.write_pins(pins)
        self.captures = os.path.join(self.root, "recapture")
        self.slots = os.path.join(self.root, "authoring")
        self.golden = os.path.join(self.root, "GOLDEN-CONTEXT.json")

    def write_pins(self, pins: dict) -> None:
        self.pins = pins
        with open(self.pins_path, "w") as handle:
            json.dump(pins, handle, indent=2)

    def register_golden(self) -> str:
        """§3.2 step 3, done as registered: the capture's digest replaces the
        null in the registry before the first slot runs."""
        pins = dict(self.pins)
        pins["golden"] = dict(pins["golden"], sha256=batch._digest(self.golden))
        self.write_pins(pins)
        return pins["golden"]["sha256"]

    def run_batch(self, slots: str, extra=()):
        # The registry these slots will be stamped with, remembered as the
        # batch runs: a registry edited afterwards is a different registry, and
        # the scorer is entitled to say so.
        self.registry = batch._digest(self.pins_path)
        return batch.main(["batch.py", "run", "--scratch-parent", self.scratch,
                           "--slots", slots, "--pins", self.pins_path,
                           "--golden", self.golden,
                           "--cli-override", self.cli] + list(extra))

    def capture(self, out: str = None, extra=()):
        return batch.main(["batch.py", "capture", "--scratch-parent", self.scratch,
                           "--captures", self.captures, "--out", out or self.golden,
                           "--pins", self.pins_path, "--cli-override", self.cli]
                          + list(extra))

    def score(self, slots: str = None):
        """§2.6: the scorer's registry of record is the COMMITTED PINS.json and
        it computes that digest itself; `main()` has no flag for it. These
        slots were made under the stand-in registry — a stand-in binary needs
        a registry that names its digest — so the test says which registry its
        own slots are supposed to name, and the batch's slots are still held to
        naming exactly one."""
        return score_rates.score(slots or self.slots, self.pins_path,
                                 os.path.join(STUDY, "FAMILY.json"),
                                 os.path.join(STUDY, "transcription", "PROMPT.txt"),
                                 self.golden,
                                 registry_sha256=getattr(self, "registry", None)
                                 or batch._digest(self.pins_path))

    def admit(self, slot: str):
        """admit() against the stand-in registry these slots were made under."""
        return score_rates.admit(
            slot, os.path.join(STUDY, "transcription", "PROMPT.txt"), self.golden,
            self.pins, registry_sha256=batch._digest(self.pins_path))

    def recapture_then_batch(self):
        """The registered order: capture, agree, register the digest, then the
        batch."""
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        self.assertEqual(self.run_batch(self.slots), 0)

    def attempt(self, index: int = 1) -> str:
        return os.path.join(self.captures, "attempt-%d" % index)

    # --- the golden gate ------------------------------------------------------

    def test_no_slot_is_created_before_the_golden_capture_is_registered(self):
        # The failure this closes cost fifty real calls: the batch used to run
        # to completion and only the scorer noticed there was no allowlist.
        self.assertEqual(self.run_batch(self.slots, ["--runs", "1"]), 1)
        self.assertFalse(os.path.exists(self.slots))
        self.assertEqual(self.capture(), 0)          # the file exists...
        self.assertEqual(self.run_batch(self.slots, ["--runs", "1"]), 1)  # ...unpinned
        self.assertFalse(os.path.exists(self.slots))
        self.register_golden()
        self.assertEqual(self.run_batch(self.slots, ["--runs", "1"]), 0)
        self.assertTrue(os.path.isdir(os.path.join(self.slots, "run-001")))

    def test_a_golden_that_is_not_the_registered_one_refuses(self):
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        with open(self.golden, "a") as handle:
            handle.write("\n")
        self.assertEqual(self.run_batch(self.slots, ["--runs", "1"]), 1)
        self.assertFalse(os.path.exists(self.slots))

    def test_a_golden_capture_is_never_derived_from_batch_slots(self):
        self.recapture_then_batch()
        post_hoc = os.path.join(self.root, "POST-HOC.json")
        self.assertEqual(batch.main(["batch.py", "capture-golden",
                                     "--pins", self.pins_path, "--slots",
                                     self.slots, "--out", post_hoc]), 1)
        self.assertFalse(os.path.exists(post_hoc))

    def test_capture_golden_writes_only_where_it_is_told(self):
        self.assertEqual(self.capture(), 0)
        # No --out: the derivation refuses rather than landing in the study.
        self.assertEqual(batch.main(["batch.py", "capture-golden",
                                     "--pins", self.pins_path, "--slots",
                                     self.attempt()]), 1)
        self.assertFalse(os.path.exists(os.path.join(
            STUDY, "transcription", "GOLDEN-CONTEXT.json")))

    # --- the ported bytes -----------------------------------------------------

    def test_drifted_ported_bytes_stop_the_batch_and_the_scorer(self):
        import integrity

        def refuse(*args, **kwargs):
            raise integrity.IntegrityError("harness/policy_mirror.py is sha256:dead…")

        self.assertEqual(self.capture(), 0)
        self.register_golden()
        with mock.patch.object(integrity, "verify", refuse):
            self.assertEqual(self.run_batch(self.slots, ["--runs", "1"]), 1)
            self.assertFalse(os.path.exists(self.slots))
            with self.assertRaises(score_rates.ScoreError):
                score_rates.verify_preconditions(self.pins_path,
                                                 os.path.join(STUDY, "transcription",
                                                              "PROMPT.txt"),
                                                 self.golden)

    # --- the run -------------------------------------------------------------

    def test_a_dry_run_creates_nothing(self):
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        self.assertEqual(self.run_batch(self.slots, ["--runs", "3", "--dry-run"]), 0)
        self.assertFalse(os.path.exists(self.slots))

    def unpinned_cli(self) -> str:
        other = fixtures.write_fake_cli(os.path.join(self.root, "cli2"), PLAN,
                                        sys.executable, HERE)
        with open(other, "a") as handle:
            handle.write("# a different binary\n")
        return other

    def test_a_cli_that_is_not_the_pinned_one_never_reaches_a_call(self):
        code = batch.main(["batch.py", "run", "--scratch-parent", self.scratch,
                           "--slots", self.slots, "--pins", self.pins_path,
                           "--golden", self.golden,
                           "--cli-override", self.unpinned_cli(), "--runs", "1"])
        self.assertEqual(code, 1)
        self.assertFalse(os.path.exists(self.slots))

    def test_the_wrapper_checks_the_digest_itself_not_only_the_driver(self):
        # The operator can run one call by hand; the pin has to hold there too.
        environment = dict(os.environ)
        environment["PYTHON_BIN"] = sys.executable
        completed = subprocess.run(
            ["bash", os.path.join(STUDY, "transcription", "authoring_call.sh"),
             self.scratch, os.path.join(self.slots, "run-001"), self.pins_path,
             self.unpinned_cli()],
            capture_output=True, text=True, env=environment)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("not the pinned", completed.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.slots, "run-001")))

    def wrapper(self, slot: str, pins_path: str = None, cli: str = None,
                environment: dict = None):
        """One call of the real wrapper, by hand, as an operator would."""
        env = dict(os.environ)
        env["PYTHON_BIN"] = sys.executable
        env.update(environment or {})
        return subprocess.run(
            ["bash", os.path.join(STUDY, "transcription", "authoring_call.sh"),
             self.scratch, slot, pins_path or self.pins_path, cli or self.cli],
            capture_output=True, text=True, env=env)

    def test_the_cli_version_is_a_pre_call_gate_not_a_later_verdict(self):
        # The reviewed draft read --version only AFTER the authoring call, so a
        # drifted CLI was scored invalid once the call had been spent. §2.1
        # says the study does not run with a substitute; a gate that fires
        # afterwards is not that.
        pins = json.loads(json.dumps(self.pins))
        pins["codex"]["version"] = "codex-cli 0.145.0"   # the stand-in says -fake
        path = os.path.join(self.root, "PINS-version.json")
        with open(path, "w") as handle:
            json.dump(pins, handle, indent=2)
        slot = os.path.join(self.slots, "run-001")
        completed = self.wrapper(slot, pins_path=path)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("not the pinned", completed.stderr)
        self.assertFalse(os.path.exists(slot))
        # And no call was made: the stand-in counts every non-version call, and
        # it never got one.
        self.assertFalse(os.path.exists(os.path.join(os.path.dirname(self.cli),
                                                     "counter")))

    def test_an_unregistered_interpreter_never_reaches_a_call(self):
        # §2.6 registers the interpreter and the reviewed draft's harness read
        # that member nowhere, while every README command ran a bare `python3`.
        stub = os.path.join(self.root, "python-stub")
        with open(stub, "w") as handle:
            handle.write('#!/bin/bash\n'
                         'if [[ "$*" == *python_implementation* ]]; then\n'
                         '  echo "PyPy 3.12"\n'
                         '  exit 0\n'
                         'fi\n'
                         'exec %s "$@"\n' % sys.executable)
        os.chmod(stub, 0o755)
        slot = os.path.join(self.slots, "run-001")
        completed = self.wrapper(slot, environment={"PYTHON_BIN": stub})
        self.assertEqual(completed.returncode, 1)
        self.assertIn("not the registered", completed.stderr)
        self.assertFalse(os.path.exists(slot))
        self.assertFalse(os.path.exists(os.path.join(os.path.dirname(self.cli),
                                                     "counter")))

    def test_a_signal_during_the_call_still_removes_the_credential(self):
        # The residual the review found by SIGKILL: an EXIT trap alone does not
        # cover a signal. INT, TERM and HUP now clean up too — SIGKILL cannot
        # be covered by any process, and §2.5 says so rather than claiming
        # "however it dies".
        import signal
        import time

        cli = fixtures.write_fake_cli(
            os.path.join(self.root, "cli-slow"),
            [{"completion": fixtures.COMPLETION_A, "sleep": 30}],
            sys.executable, HERE)
        pins = json.loads(json.dumps(self.pins))
        pins["codex"]["binarySha256"] = batch._digest(cli)
        path = os.path.join(self.root, "PINS-slow.json")
        with open(path, "w") as handle:
            json.dump(pins, handle, indent=2)
        slot = os.path.join(self.root, "authoring-signalled", "run-001")
        env = dict(os.environ)
        env["PYTHON_BIN"] = sys.executable
        process = subprocess.Popen(
            ["bash", os.path.join(STUDY, "transcription", "authoring_call.sh"),
             self.scratch, slot, path, cli],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
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

    def test_the_recapture_uses_the_probe_prompt_and_agrees_with_itself(self):
        self.assertEqual(self.capture(), 0)
        golden = json.load(open(self.golden))
        self.assertEqual(golden["capturedFrom"], ["capture-001", "capture-002"])
        self.assertEqual(golden["capturedIn"], "attempt-1")
        self.assertTrue(golden["entries"])
        for name in golden["capturedFrom"]:
            call = json.load(open(os.path.join(self.attempt(), name, "CALL.json")))
            self.assertEqual(call["promptKind"], "probe")
            self.assertEqual(call["promptSha256"], self.pins["probePrompt"]["sha256"])
        # The registered prompt never ran: no capture answered with records.
        for name in golden["capturedFrom"]:
            with open(os.path.join(self.attempt(), name, "completion.txt")) as handle:
                self.assertEqual(handle.read(), "ready")

    def test_a_repeated_recapture_gets_its_own_attempt_directory(self):
        # §3.2 step 3: a disagreeing recapture may be repeated after the cause
        # is fixed. Slots are never rewritten, so the repeat needs somewhere to
        # go and every attempt stays published.
        self.assertEqual(self.capture(), 0)
        second = os.path.join(self.root, "GOLDEN-2.json")
        self.assertEqual(self.capture(out=second), 0)
        self.assertEqual(sorted(os.listdir(self.captures)), ["attempt-1", "attempt-2"])
        self.assertEqual(json.load(open(second))["capturedIn"], "attempt-2")

    def test_one_capture_cannot_derive_a_golden(self):
        # The freeze-blocking hole: `capture --runs 1` passed 1 as the
        # derivation's minimum, so a single unreproduced context became an
        # allowlist and the batch accepted it. Two clauses now refuse it —
        # one before any call is spent, one where the derivation happens.
        self.assertEqual(self.capture(extra=["--runs", "1"]), 1)
        self.assertFalse(os.path.exists(self.captures))
        self.assertFalse(os.path.exists(self.golden))

    def test_the_derivation_itself_refuses_a_single_capture_slot(self):
        self.assertEqual(self.capture(), 0)
        lonely = os.path.join(self.root, "one-capture")
        os.makedirs(lonely)
        import shutil
        shutil.copytree(os.path.join(self.attempt(), "capture-001"),
                        os.path.join(lonely, "capture-001"))
        out = os.path.join(self.root, "ONE.json")
        # Even asked for one explicitly: MIN_CAPTURE_SLOTS is a floor.
        self.assertEqual(batch.main(["batch.py", "capture-golden",
                                     "--pins", self.pins_path, "--slots", lonely,
                                     "--out", out, "--min-slots", "1"]), 1)
        self.assertEqual(batch.main(["batch.py", "capture-golden",
                                     "--pins", self.pins_path, "--slots", lonely,
                                     "--out", out]), 1)
        self.assertFalse(os.path.exists(out))

    def duplicate_captures(self, name: str) -> str:
        """Two capture slots holding ONE call's evidence: `capture-001`, copied
        under both names, exactly as a `cp -r` of a retained slot leaves it."""
        import shutil
        directory = os.path.join(self.root, name)
        os.makedirs(directory)
        for slot in ("capture-001", "capture-002"):
            shutil.copytree(os.path.join(self.attempt(), "capture-001"),
                            os.path.join(directory, slot))
        return directory

    def test_two_agreeing_captures_must_be_two_calls(self):
        # The round-2 gap: the derivation counted slots and compared normalized
        # contexts, so one call retained twice satisfied "at least two agreeing
        # captures" — and agreed with itself by construction, having never been
        # shown to reproduce anything.
        self.assertEqual(self.capture(), 0)
        # The honest half first: two real probe calls, distinct in every raw
        # identity, agreeing after normalization — the outcome the recapture
        # exists to demonstrate, and it still derives.
        first, second = (batch.capture_identity(os.path.join(self.attempt(), name))
                         for name in ("capture-001", "capture-002"))
        for member, _ in batch.CAPTURE_IDENTITY:
            self.assertNotEqual(first[member], second[member], member)
        golden = json.load(open(self.golden))
        self.assertEqual(golden["capturedFrom"], ["capture-001", "capture-002"])
        # …and the duplicate refuses, however it was made.
        out = os.path.join(self.root, "DUPLICATED.json")
        self.assertEqual(batch.main(["batch.py", "capture-golden",
                                     "--pins", self.pins_path, "--slots",
                                     self.duplicate_captures("duplicated"),
                                     "--out", out]), 1)
        self.assertFalse(os.path.exists(out))

    def test_two_captures_naming_one_session_refuse_even_when_nothing_else_matches(self):
        # The narrow shape: two slots whose bytes, clocks and directories all
        # differ, and whose transcripts name the same session. Their normalized
        # contexts agree — session_meta carries no conversation content — so
        # nothing but the raw session id says they are one call.
        self.assertEqual(self.capture(), 0)
        import shutil
        directory = os.path.join(self.root, "one-session")
        shutil.copytree(self.attempt(), directory)
        first = os.path.join(directory, "capture-001", "session.jsonl")
        second = os.path.join(directory, "capture-002", "session.jsonl")
        identity = batch.session_identity(first)
        self.assertTrue(identity)
        with open(second) as handle:
            lines = handle.readlines()
        meta = json.loads(lines[0])
        self.assertEqual(meta["type"], "session_meta")
        meta["payload"]["id"] = identity
        lines[0] = json.dumps(meta) + "\n"
        with open(second, "w") as handle:
            handle.writelines(lines)
        out = os.path.join(self.root, "ONE-SESSION.json")
        self.assertEqual(batch.main(["batch.py", "capture-golden",
                                     "--pins", self.pins_path, "--slots",
                                     directory, "--out", out]), 1)
        self.assertFalse(os.path.exists(out))

    def test_a_capture_that_does_not_reproduce_refuses_the_derivation(self):
        self.assertEqual(self.capture(), 0)
        varying = os.path.join(self.root, "varying")
        os.makedirs(varying)
        import shutil
        for index, name in enumerate(("capture-001", "capture-002"), 1):
            shutil.copytree(os.path.join(self.attempt(), name),
                            os.path.join(varying, name))
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
                                     "--pins", self.pins_path, "--slots", varying,
                                     "--out", out]), 1)
        self.assertFalse(os.path.exists(out))

    def test_a_golden_derived_after_the_batch_cannot_re_admit_its_runs(self):
        # The freeze-blocking hole: BATCH.json recorded the pre-batch golden
        # and the scorer never read it, so a capture derived afterwards and
        # re-pinned turned invalid runs valid. Every slot now names the
        # capture it was made against.
        self.recapture_then_batch()
        before = self.score()
        self.assertEqual(before["population"]["valid"], 4)
        # The attack, as the review ran it: copy retained capture slots into a
        # directory of another name and derive a golden from them after the
        # fact. It derives cleanly — the captures do agree — and it is a
        # different file, which is the whole point.
        import shutil
        post_hoc = os.path.join(self.root, "post-hoc-captures")
        shutil.copytree(self.attempt(), post_hoc)
        second = os.path.join(self.root, "GOLDEN-2.json")
        self.assertEqual(batch.main(["batch.py", "capture-golden",
                                     "--pins", self.pins_path, "--slots", post_hoc,
                                     "--out", second]), 0)
        self.assertNotEqual(batch._digest(second), batch._digest(self.golden))
        pins = json.loads(json.dumps(self.pins))
        pins["golden"]["sha256"] = batch._digest(second)
        self.write_pins(pins)
        self.golden = second
        after = self.score()
        self.assertEqual(after["population"]["valid"], 0)
        self.assertEqual(after["population"]["invalidCodes"], {"golden-mismatch": 5})

    def test_a_registry_edited_after_the_batch_invalidates_every_slot(self):
        # The other half of the same guarantee: --pins cannot redefine the
        # cell, because the cell is the registry the runs were MADE under.
        self.recapture_then_batch()
        self.assertEqual(self.score()["population"]["valid"], 4)
        for name, member, value, code in (
                # A registry that renames the cell contradicts what every run
                # recorded, and each run says so with its own code…
                ("PINS-alien.json", "model", "alien-model", "model-mismatch"),
                ("PINS-binary.json", "binarySha256", "sha256:" + "1" * 64,
                 "binary-mismatch")):
            alien = json.loads(json.dumps(self.pins))
            alien["codex"][member] = value
            path = os.path.join(self.root, name)
            with open(path, "w") as handle:
                json.dump(alien, handle, indent=2)
            results = self.score_with(path)
            self.assertEqual(results["population"]["valid"], 0, name)
            self.assertEqual(results["population"]["invalidCodes"], {code: 5}, name)
        # …and a registry whose cell values agree but whose BYTES are not the
        # registry of record is refused on that alone, so "same model, quietly
        # different registry" is not a way in either.
        other = json.loads(json.dumps(self.pins))
        other["note"] = "a registry that differs from the one the runs were made under"
        path = os.path.join(self.root, "PINS-other.json")
        with open(path, "w") as handle:
            json.dump(other, handle, indent=2)
        results = score_rates.score(
            self.slots, path, os.path.join(STUDY, "FAMILY.json"),
            os.path.join(STUDY, "transcription", "PROMPT.txt"), self.golden,
            registry_sha256=batch._digest(path))
        self.assertEqual(results["population"]["valid"], 0)
        self.assertEqual(results["population"]["invalidCodes"], {"registry-mismatch": 5})
        for entry in results["classes"]:
            self.assertIsNone(entry["coverage"]["rate"])
            self.assertIsNone(entry["reviewTier"]["tier"])

    def test_a_registry_that_shrinks_n_never_reaches_a_slot(self):
        # A registry naming registeredRuns 1 does not get to publish a rate
        # over one hand-picked slot: terminality refuses the whole scoring
        # before any slot is read (§2.4).
        self.recapture_then_batch()
        alien = json.loads(json.dumps(self.pins))
        alien["batch"]["runs"] = 1
        path = os.path.join(self.root, "PINS-one-run.json")
        with open(path, "w") as handle:
            json.dump(alien, handle, indent=2)
        with self.assertRaises(score_rates.ScoreError) as caught:
            self.score_with(path)
        self.assertIn("not terminal", str(caught.exception))

    def score_with(self, pins_path: str) -> dict:
        return score_rates.score(
            self.slots, pins_path, os.path.join(STUDY, "FAMILY.json"),
            os.path.join(STUDY, "transcription", "PROMPT.txt"), self.golden,
            registry_sha256=self.registry)

    def test_a_registered_capture_is_never_rewritten(self):
        self.assertEqual(self.capture(), 0)
        self.assertEqual(batch.main(["batch.py", "capture-golden",
                                     "--pins", self.pins_path, "--slots",
                                     self.attempt(), "--out", self.golden]), 1)

    def test_the_slots_are_the_shape_the_scorer_reads(self):
        self.recapture_then_batch()
        for name in ("run-001", "run-002", "run-003", "run-004"):
            slot = os.path.join(self.slots, name)
            for retained in ("CALL.json", "stdout.raw", "stderr.raw", "session.jsonl",
                             "context.json", "completion.txt"):
                self.assertTrue(os.path.isfile(os.path.join(slot, retained)),
                                "%s/%s" % (name, retained))
        call = json.load(open(os.path.join(self.slots, "run-001", "CALL.json")))
        self.assertEqual(call["model"], self.pins["codex"]["model"])
        self.assertEqual(call["binarySha256"], self.pins["codex"]["binarySha256"])
        self.assertEqual(call["promptKind"], "registered")
        self.assertEqual(call["slotIndex"], 1)
        self.assertTrue(call["homeIsolated"] and call["environmentScrubbed"])
        # C6, credential branch: the isolated home held the .codex directory
        # and the copied credential — recursively, so pollution shows.
        self.assertTrue(call["credentialCopied"])
        self.assertEqual(call["isolatedHomeInventory"], [".codex", ".codex/auth.json"])
        self.assertTrue(call["credentialRemoved"])
        # The scrubbed PATH is fixed system directories plus one per-run
        # directory, and it is published rather than described.
        values = call["environmentValues"]
        self.assertNotIn(self.home, values["PATH"])
        self.assertNotIn(os.environ.get("PATH", "@none@"), values["PATH"])
        self.assertTrue(values["PATH"].startswith("/usr/local/sbin:"))
        # TMPDIR is this run's own, under this run's own scratch — not /tmp,
        # which the pinned CLI's sandbox would make writable for every run.
        self.assertNotEqual(values["TMPDIR"], "/tmp")
        self.assertTrue(values["TMPDIR"].startswith(call["cwd"] + os.sep), values["TMPDIR"])
        self.assertIn("s011-authoring-run-001", values["TMPDIR"])

    def test_a_machine_with_no_operator_credential_still_admits_its_runs(self):
        # C6's other branch. The draft expected an inventory of 0 entries here,
        # a state the wrapper cannot produce, so every slot on a credential-less
        # machine scored isolation-unproven after fifty real calls.
        bare = fixtures.write_operator_home(os.path.join(self.root, "bare-home"),
                                            credential=False)
        with mock.patch.dict(os.environ, {"HOME": bare}):
            self.assertEqual(self.capture(), 0)
            self.register_golden()
            self.assertEqual(self.run_batch(self.slots, ["--runs", "1"]), 0)
        call = json.load(open(os.path.join(self.slots, "run-001", "CALL.json")))
        self.assertFalse(call["credentialCopied"])
        self.assertFalse(call["credentialRemoved"])
        self.assertEqual(call["isolatedHomeInventory"], [".codex"])
        code, detail, _ = self.admit(os.path.join(self.slots, "run-001"))
        self.assertIsNone(code, detail)

    def test_a_polluted_isolated_home_refuses_in_either_branch(self):
        self.recapture_then_batch()
        slot = os.path.join(self.slots, "run-001")
        path = os.path.join(slot, "CALL.json")
        for inventory, copied in (
                ([".codex", ".codex/auth.json", ".codex/config.toml"], True),
                ([".codex", ".codex/auth.json", "AGENTS.md"], True),
                ([".agents", ".agents/skills", ".codex"], False),
                ([".codex"], True),
                ([".codex", ".codex/auth.json"], False)):
            call = json.load(open(path))
            call["isolatedHomeInventory"] = inventory
            call["credentialCopied"] = copied
            call["credentialRemoved"] = copied
            with open(path, "w") as handle:
                json.dump(call, handle, indent=2)
            code, detail, _ = self.admit(slot)
            self.assertEqual(code, "isolation-unproven", "%r/%s" % (inventory, copied))
            self.assertIn("isolated home held", detail)

    def test_no_retained_byte_and_no_leftover_carries_the_credential(self):
        self.recapture_then_batch()
        self.assertEqual(batch.main([
            "batch.py", "capture-isolation-negative", "--scratch-parent", self.scratch,
            "--out", os.path.join(self.root, "isolation-negative"),
            "--pins", self.pins_path, "--golden", self.golden,
            "--cli-override", self.cli]), 0)
        hits = []
        for root in (self.slots, self.captures, self.scratch,
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
        # And no copy of it is left lying under the scratch parent either.
        leftovers = [os.path.join(base, name)
                     for base, _, names in os.walk(self.scratch) for name in names
                     if name == "auth.json"]
        self.assertEqual(leftovers, [])

    def test_a_wrapper_death_after_the_copy_still_removes_the_credential(self):
        # The residual the blocker re-check found: without a trap, a wrapper
        # killed between the credential copy and the slot seal left the copy
        # under the scratch parent. Reproduce the death — the stand-in exits 0
        # with a transcript carrying no assistant message, so the wrapper's
        # completion extraction raises under set -e — and require the EXIT
        # trap to have removed the copy anyway, however the run ended.
        cli = fixtures.write_fake_cli(
            os.path.join(self.root, "cli-dying"),
            [{"completion": "ready"}, {"completion": "ready"},
             {"completion": fixtures.COMPLETION_A, "no_assistant": True}],
            sys.executable, HERE)
        pins = dict(self.pins)
        pins["codex"] = dict(pins["codex"], binarySha256=batch._digest(cli))
        self.write_pins(pins)
        self.cli = cli
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        slots = os.path.join(self.root, "authoring-dying")
        self.run_batch(slots, ["--runs", "1"])  # the run fails; the outcome
        # under test is the credential, not the exit path.
        leftovers = [os.path.join(base, name)
                     for base, _, names in os.walk(self.scratch) for name in names
                     if name == "auth.json"]
        self.assertEqual(leftovers, [], "a wrapper death left the credential copy")
        for root in (slots, self.scratch):
            for base, _, names in os.walk(root):
                for name in names:
                    path = os.path.join(base, name)
                    if os.path.islink(path):
                        continue
                    with open(path, "rb") as handle:
                        if fixtures.SENTINEL_TOKEN.encode("utf-8") in handle.read():
                            self.fail("credential bytes retained at %r" % path)

    # --- §6 C7 ---------------------------------------------------------------

    def negative_control(self, out: str, pins_path: str = None):
        return batch.main(["batch.py", "capture-isolation-negative",
                           "--scratch-parent", self.scratch, "--out", out,
                           "--pins", pins_path or self.pins_path,
                           "--golden", self.golden, "--cli-override", self.cli])

    def test_the_isolation_negative_control_fails_the_golden_match_and_keeps_three_files(self):
        # The operator's stand-in home carries a skills tree, which the
        # stand-in CLI puts in the pre-prompt context exactly as Study 010
        # found the real one doing. The golden was captured from isolated
        # homes, so the comparison must refuse — and the control must reach
        # the comparison rather than stopping at a session count.
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
            self.assertEqual(self.negative_control(out), 0)
        self.assertEqual(sorted(os.listdir(out)),
                         ["CALL.json", "VERDICT.json", "context.json"])
        verdict = json.load(open(os.path.join(out, "VERDICT.json")))
        self.assertEqual(verdict["outcome"], "refused")
        self.assertEqual(verdict["registeredExpectation"], "the golden match FAILS")
        self.assertIn("session.jsonl", verdict["deletedByCode"])
        self.assertEqual(verdict["operatorAssent"], "granted")
        call = json.load(open(os.path.join(out, "CALL.json")))
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
                          if name.startswith("s011-c7-raw")], [])

    def test_a_control_that_reaches_neither_comparison_says_so_and_fails(self):
        # The reviewed draft returned 0 with outcome `no-context` — neither
        # registered comparison — and retained two files while §6 C7 promised
        # three. `no-context` is now a registered outcome, its retention rule
        # is exact, and it exits non-zero because a control that did not run
        # is not a step that was done.
        cli = fixtures.write_fake_cli(
            os.path.join(self.root, "cli-silent"),
            [{"completion": "ready"}, {"completion": "ready"},
             {"completion": "ready", "no_session": True}],
            sys.executable, HERE)
        pins = dict(self.pins)
        pins["codex"] = dict(pins["codex"], binarySha256=batch._digest(cli))
        self.write_pins(pins)
        self.cli = cli
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        out = os.path.join(self.root, "isolation-negative-silent")
        self.assertEqual(self.negative_control(out), 1)
        self.assertEqual(sorted(os.listdir(out)), ["CALL.json", "VERDICT.json"])
        verdict = json.load(open(os.path.join(out, "VERDICT.json")))
        self.assertEqual(verdict["outcome"], "no-context")
        self.assertIn("no-context", verdict["registeredOutcomes"])
        self.assertIn("undemonstrated", verdict["message"])
        self.assertEqual([name for name in os.listdir(self.scratch)
                          if name.startswith("s011-c7-raw")], [])

    def test_a_control_whose_transcript_survives_removal_refuses(self):
        # "Digested and deleted by the driver" is a claim about the disk.
        # rmtree(ignore_errors=True) made it a claim about the call that was
        # made, so the driver could report success with the operator's
        # transcript still on it.
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        out = os.path.join(self.root, "isolation-negative-stuck")
        with mock.patch.object(batch.shutil, "rmtree"):
            self.assertEqual(self.negative_control(out), 1)
        leftover = [name for name in os.listdir(self.scratch)
                    if name.startswith("s011-c7-raw")]
        self.assertEqual(len(leftover), 1)
        import shutil
        shutil.rmtree(os.path.join(self.scratch, leftover[0]))

    def test_the_negative_control_refuses_without_recorded_assent(self):
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        pins = json.loads(json.dumps(self.pins))
        pins["isolationNegative"]["operatorAssent"] = "withheld"
        path = os.path.join(self.root, "PINS-no-assent.json")
        with open(path, "w") as handle:
            json.dump(pins, handle, indent=2)
        out = os.path.join(self.root, "isolation-negative")
        self.assertEqual(self.negative_control(out, pins_path=path), 1)
        self.assertFalse(os.path.exists(out))

    # --- the ledger ----------------------------------------------------------

    def test_a_failing_run_is_refused_and_the_batch_continues(self):
        self.recapture_then_batch()
        self.assertEqual(sorted(os.listdir(self.slots)),
                         ["BATCH.json"] + ["run-00%d" % index
                                           for index in range(1, BATCH_RUNS + 1)])
        refusal = json.load(open(os.path.join(self.slots, "run-005", "REFUSAL.json")))
        self.assertEqual(refusal["code"], "call-nonzero-exit")
        self.assertEqual(refusal["wrapperExit"], 10)
        self.assertFalse(os.path.exists(os.path.join(self.slots, "run-005", "completion.txt")))
        ledger = json.load(open(os.path.join(self.slots, "BATCH.json")))
        self.assertEqual([row["code"] for row in ledger["records"]],
                         [None, None, None, None, "call-nonzero-exit"])

    def test_a_resumed_batch_merges_the_ledger_rather_than_replacing_it(self):
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        self.assertEqual(self.run_batch(self.slots, ["--runs", "2"]), 0)
        self.assertEqual(self.run_batch(self.slots, ["--runs", "3", "--start", "3"]), 0)
        ledger = json.load(open(os.path.join(self.slots, "BATCH.json")))
        self.assertEqual([row["slot"] for row in ledger["records"]],
                         ["run-00%d" % index for index in range(1, BATCH_RUNS + 1)])
        self.assertEqual([row["startIndex"] for row in ledger["records"]],
                         [1, 1, 3, 3, 3])
        results = self.score()
        self.assertEqual(results["population"]["slots"], BATCH_RUNS)

    def test_a_resume_that_would_overlap_the_ledger_refuses(self):
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        self.assertEqual(self.run_batch(self.slots, ["--runs", "2"]), 0)
        import shutil
        shutil.rmtree(os.path.join(self.slots, "run-002"))
        self.assertEqual(self.run_batch(self.slots, ["--runs", "1", "--start", "2"]), 1)

    def test_a_retained_slot_is_never_rewritten(self):
        self.recapture_then_batch()
        self.assertEqual(self.run_batch(self.slots), 1)

    def test_a_dangling_planned_slot_refuses_the_resume_through_the_registered_path(self):
        """Round 3: `os.path.exists()` calls a dangling link absent and `mkdir`
        calls it present, so a resume over one passed preflight, spent no call,
        and ended in an uncaught `FileExistsError` from `refuse_slot()` — no
        registered refusal, and `BATCH.json` left at the earlier runs. A link
        at a planned slot path is a slot that already exists."""
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        self.assertEqual(self.run_batch(self.slots, ["--runs", "2"]), 0)
        before = json.load(open(os.path.join(self.slots, "BATCH.json")))
        os.symlink(os.path.join(self.slots, "no-such-slot"),
                   os.path.join(self.slots, "run-003"))
        # A registered refusal (exit 1), not a traceback…
        self.assertEqual(self.run_batch(self.slots, ["--runs", "3", "--start", "3"]), 1)
        # …no slot created over the link, and the ledger untouched.
        self.assertTrue(os.path.islink(os.path.join(self.slots, "run-003")))
        self.assertFalse(os.path.isdir(os.path.join(self.slots, "run-003")))
        self.assertEqual(json.load(open(os.path.join(self.slots, "BATCH.json"))), before)
        self.assertFalse(os.path.exists(os.path.join(self.slots, "run-004")))
        # The wrapper says the same thing on its own, for a call made by hand.
        environment = dict(os.environ)
        environment["PYTHON_BIN"] = sys.executable
        completed = subprocess.run(
            ["bash", os.path.join(STUDY, "transcription", "authoring_call.sh"),
             self.scratch, os.path.join(self.slots, "run-003"), self.pins_path,
             self.cli],
            capture_output=True, text=True, env=environment)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("already exists", completed.stderr)

    def test_a_derivation_from_registered_prompt_captures_refuses(self):
        """§3.2 step 2: the capture is derived from PROBE calls. `capture_slots`
        refused batch-shaped NAMES, and a name is not evidence of which prompt
        was answered — two registered-prompt slots renamed `capture-001/002`
        derived a golden cleanly."""
        self.recapture_then_batch()
        import shutil
        renamed = os.path.join(self.root, "renamed-captures")
        os.makedirs(renamed)
        for index, name in enumerate(("run-001", "run-002"), 1):
            shutil.copytree(os.path.join(self.slots, name),
                            os.path.join(renamed, "capture-%03d" % index))
        out = os.path.join(self.root, "RENAMED.json")
        self.assertEqual(batch.main(["batch.py", "capture-golden",
                                     "--pins", self.pins_path,
                                     "--slots", renamed, "--out", out]), 1)
        self.assertFalse(os.path.exists(out))

    def test_the_derivation_and_the_shortfall_run_the_same_preflight_as_the_calls(self):
        """Round 3: `capture-golden` and `shortfall` skipped the ported-bytes,
        interpreter and freeze checks, so a golden capture could be derived —
        and a shortfall declared — under an unregistered interpreter against an
        unfrozen study. Both feed the published arithmetic."""
        import integrity

        self.assertEqual(self.capture(), 0)
        self.register_golden()
        self.assertEqual(self.run_batch(self.slots, ["--runs", "2"]), 0)

        def refuse(*arguments, **keywords):
            raise integrity.IntegrityError("harness/policy_mirror.py is sha256:dead…")

        out = os.path.join(self.root, "DRIFTED.json")
        with mock.patch.object(integrity, "verify", refuse):
            self.assertEqual(batch.main(["batch.py", "capture-golden",
                                         "--pins", self.pins_path,
                                         "--slots", self.attempt(), "--out", out]), 1)
            self.assertEqual(batch.main(["batch.py", "shortfall", "--slots", self.slots,
                                         "--pins", self.pins_path,
                                         "--reason", "drifted bytes"]), 1)
        self.assertFalse(os.path.exists(out))
        self.assertFalse(os.path.exists(os.path.join(self.slots, "SHORTFALL.json")))

        # …and the freeze digest, which the registry must carry before either.
        unfrozen = json.loads(json.dumps(self.pins))
        unfrozen["preregistration"]["sha256"] = None
        path = os.path.join(self.root, "PINS-unfrozen.json")
        with open(path, "w") as handle:
            json.dump(unfrozen, handle, indent=2)
        self.assertEqual(batch.main(["batch.py", "capture-golden", "--pins", path,
                                     "--slots", self.attempt(), "--out", out]), 1)
        self.assertEqual(batch.main(["batch.py", "shortfall", "--slots", self.slots,
                                     "--pins", path, "--reason", "unfrozen"]), 1)
        self.assertFalse(os.path.exists(out))
        self.assertFalse(os.path.exists(os.path.join(self.slots, "SHORTFALL.json")))

    # --- terminality ---------------------------------------------------------

    def test_an_incomplete_batch_is_not_scorable_until_the_shortfall_is_declared(self):
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        self.assertEqual(self.run_batch(self.slots, ["--runs", "2"]), 0)
        with self.assertRaises(score_rates.ScoreError):
            self.score()
        self.assertEqual(batch.main(["batch.py", "shortfall", "--slots", self.slots,
                                     "--pins", self.pins_path, "--reason",
                                     "the stand-in CLI batch was cut short on purpose"]), 0)
        results = self.score()
        self.assertEqual(results["population"]["slots"], 2)
        self.assertEqual(results["population"]["shortfall"], BATCH_RUNS - 2)
        self.assertIn("cut short", results["population"]["shortfallDeclaration"]["reason"])

    def test_a_shortfall_may_not_be_declared_over_a_batch_that_is_not_short(self):
        self.recapture_then_batch()
        self.assertEqual(batch.main(["batch.py", "shortfall", "--slots", self.slots,
                                     "--pins", self.pins_path, "--reason",
                                     "not actually short"]), 1)
        self.assertFalse(os.path.exists(os.path.join(self.slots, "SHORTFALL.json")))

    def test_a_declaration_that_is_not_this_batchs_refuses_the_scoring(self):
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        self.assertEqual(self.run_batch(self.slots, ["--runs", "2"]), 0)
        with open(os.path.join(self.slots, "SHORTFALL.json"), "w") as handle:
            json.dump({"registeredRuns": BATCH_RUNS, "completedSlots": 4,
                       "reason": "counts that are not this batch's"}, handle)
        with self.assertRaises(score_rates.ScoreError):
            self.score()

    def test_the_scorer_has_no_flag_that_writes_a_rate_table_elsewhere(self):
        self.recapture_then_batch()
        self.assertEqual(score_rates.main(
            ["score_rates.py", "score", "--slots", self.slots,
             "--out", os.path.join(self.root, "peek")]), 1)
        self.assertFalse(os.path.exists(os.path.join(self.root, "peek")))
        self.assertFalse(os.path.exists(os.path.join(STUDY, "RESULTS.json")))

    # --- the registered scoring interface (§7) --------------------------------

    def published(self, out: str) -> dict:
        with open(os.path.join(out, "RESULTS.json")) as handle:
            return json.load(handle)

    def test_every_withdrawn_and_unknown_argument_refuses_rather_than_being_ignored(self):
        """Round 3: `_argument()` ignored what it did not recognize, so a stale
        or mistaken command line ran a DIFFERENT scoring than it reads as
        having run. Every input-path flag is gone from the registered command,
        and an argument the command does not know refuses."""
        self.recapture_then_batch()
        for argument in (["--pins", self.pins_path], ["--family", "/dev/null"],
                         ["--prompt", "/dev/null"], ["--golden", self.golden],
                         ["--registry-sha256", self.registry],
                         ["--out", os.path.join(self.root, "peek")],
                         ["--registry", self.registry], ["--slots"], ["nonsense"],
                         ["--slots", self.slots, "--slots", self.slots]):
            self.assertEqual(score_rates.main(
                ["score_rates.py", "score", "--slots", self.slots] + argument), 1,
                "%r was accepted" % (argument,))
        self.assertFalse(os.path.exists(os.path.join(self.root, "peek")))
        self.assertFalse(os.path.exists(os.path.join(STUDY, "RESULTS.json")))
        self.assertFalse(os.path.exists(os.path.join(STUDY, "RATES.md")))

    def test_no_surface_publishes_a_scoring_of_alternate_registry_slots(self):
        """Rounds 2 and 3, together. Round 2: `--pins` could not redefine the
        cell but `score()`'s library override could, and the public
        `write_outputs()` took the resulting dict. Round 3: the registered
        command still ACCEPTED `--pins`, so a registry identical to the
        committed one except for `batch.runs` redefined N and published a
        one-slot population as this study's; and `write_outputs()` trusted a
        mutable member, so editing `cell.registryOverride` to None published
        an override scoring anywhere.

        The alternate registry used here is exactly the round-3 one: every
        digest and cell value equal to the stand-in registry these slots were
        made under, `batch.runs` changed to 1. Every surface is tried.

        These slots ARE alternate-registry slots: the whole file drives the
        real wrapper under a stand-in registry naming a stand-in binary.
        """
        # One slot, so the shrunk registry's N = 1 is TERMINAL against it and
        # the attack gets as far as a computed dict — the reviewer's exact
        # setup, which is what makes the refusals below load-bearing.
        self.assertEqual(self.capture(), 0)
        self.register_golden()
        self.assertEqual(self.run_batch(self.slots, ["--runs", "1"]), 0)
        committed = batch._digest(os.path.join(STUDY, "harness", "PINS.json"))
        self.assertNotEqual(self.registry, committed)
        shrunk = json.loads(json.dumps(self.pins))
        shrunk["batch"]["runs"] = 1
        shrunk_path = os.path.join(self.root, "PINS-one-run.json")
        with open(shrunk_path, "w") as handle:
            json.dump(shrunk, handle, indent=2)

        # 1. The registered command cannot be handed that registry at all: the
        #    flag is gone, and an unknown flag refuses instead of being dropped.
        self.assertEqual(score_rates.main(
            ["score_rates.py", "score", "--slots", self.slots,
             "--pins", shrunk_path]), 1)

        # 2. Nor can it be reached by scoring the committed registry: the
        #    registered command derives every path from its own location, and
        #    this study's committed registry has no golden pin yet, so it
        #    refuses before a slot is read rather than publishing anything.
        self.assertEqual(score_rates.main(
            ["score_rates.py", "score", "--slots", self.slots]), 1)

        # 3. The library path computes a dict and there is NO public writer to
        #    hand it to. `write_outputs` is gone; `emit_records` is gone.
        for name in ("write_outputs", "emit_records"):
            self.assertFalse(hasattr(score_rates, name),
                             "score_rates.%s is public again" % name)

        # 4. The private writer, called directly with the round-3 attack: score
        #    the alternate-registry slots under the shrunk registry with the
        #    matching override, then edit the ordinary returned dict's
        #    `registryOverride` member to None, exactly as the reviewer did.
        #    It is refused on what the study tree says, not on that member.
        counted = score_rates.score(
            self.slots, shrunk_path, os.path.join(STUDY, "FAMILY.json"),
            os.path.join(STUDY, "transcription", "PROMPT.txt"), self.golden,
            registry_sha256=self.registry)
        self.assertEqual(counted["population"]["registeredRuns"], 1)
        self.assertEqual(counted["population"]["valid"], 1)
        self.assertEqual(counted["cell"][score_rates.REGISTRY_OVERRIDE], self.registry)
        with self.assertRaises(score_rates.ScoreError) as caught:
            score_rates._write_outputs(counted)
        self.assertIn("override", str(caught.exception))
        counted["cell"][score_rates.REGISTRY_OVERRIDE] = None
        with self.assertRaises(score_rates.ScoreError) as caught:
            score_rates._write_outputs(counted)
        self.assertIn("committed harness/PINS.json", str(caught.exception))
        # …and with EVERY cell digest forged to the committed study's, so the
        # dict no longer says anywhere that it counted under another registry,
        # N is still the committed registry's to state and this scoring
        # counted one slot against a registry that asked for one.
        with open(os.path.join(STUDY, "harness", "PINS.json")) as handle:
            real = json.load(handle)
        counted["cell"].update({
            "registryOfRecordSha256": committed,
            "promptSha256": real["prompt"]["sha256"],
            "familySha256": real["family"]["sha256"],
            "goldenSha256": real["golden"]["sha256"],
            "preregistrationSha256": real["preregistration"]["sha256"],
            "model": real["codex"]["model"],
            "cli": real["codex"]["version"],
            "binarySha256": real["codex"]["binarySha256"],
        })
        with self.assertRaises(score_rates.ScoreError) as caught:
            score_rates._write_outputs(counted)
        self.assertIn("registered batch size", str(caught.exception))

        # 5. A results dict that never came through score() cannot be published
        #    either: it cannot say which registry it counted under.
        forged = json.loads(json.dumps(counted))
        forged["cell"].pop(score_rates.REGISTRY_OVERRIDE)
        for candidate in (forged, {"runs": []}, [], None):
            with self.assertRaises(score_rates.ScoreError):
                score_rates._write_outputs(candidate)

        # Nothing reached a published file by any of those routes.
        self.assertFalse(os.path.exists(os.path.join(STUDY, "RESULTS.json")))
        self.assertFalse(os.path.exists(os.path.join(STUDY, "RATES.md")))

    def test_emitting_records_into_the_slot_tree_refuses_before_anything_is_written(self):
        """Round 3: `--emit-records <slots>/run-002` wrote a phantom slot into
        the population it had just published, so the retained tree could not
        reproduce the published rates and the next scoring refused. The two
        directories must be disjoint, and the refusal must precede the writing
        rather than follow it."""
        self.recapture_then_batch()
        before = sorted(os.listdir(self.slots))
        for target in (self.slots, os.path.join(self.slots, "run-006"),
                       os.path.join(self.slots, "run-001", "records"),
                       os.path.dirname(self.slots)):
            with self.assertRaises(score_rates.ScoreError) as caught:
                score_rates._check_records_target(self.slots, target)
            self.assertIn("emit-records", str(caught.exception))
            self.assertEqual(score_rates.main(
                ["score_rates.py", "score", "--slots", self.slots,
                 "--emit-records", target]), 1)
        # No phantom slot, and no rate table: the refusal came first.
        self.assertEqual(sorted(os.listdir(self.slots)), before)
        self.assertFalse(os.path.exists(os.path.join(STUDY, "RESULTS.json")))
        # A directory outside the slot tree is what the command accepts.
        score_rates._check_records_target(self.slots,
                                          os.path.join(self.root, "records"))

    def stand_in_study(self, out: str):
        """The registered command pointed at a stand-in study, as a context.

        This REBINDS `score_rates`'s module constants, which is precisely the
        escape PREREGISTRATION.md §7 says no check inside a file can refuse. It
        is used here for the only thing it is good for: standing up a whole
        stand-in study — its own registry, its own golden capture, its own
        study root — so the registered command's success path can be exercised
        without writing into the committed tree, whose golden pin is still
        null. Nothing in it is evidence that the command can be redirected by
        an argument, a flag, a default or the environment; the other cases in
        this section are that evidence.
        """
        return mock.patch.multiple(
            score_rates, STUDY=out, REGISTRY_OF_RECORD=self.pins_path,
            REGISTERED_FAMILY=os.path.join(STUDY, "FAMILY.json"),
            REGISTERED_PROMPT=os.path.join(STUDY, "transcription", "PROMPT.txt"),
            REGISTERED_GOLDEN=self.golden)

    def test_the_registered_command_publishes_the_tables_and_the_records_it_promises(self):
        self.recapture_then_batch()
        out = os.path.join(self.root, "published")
        records = os.path.join(self.root, "records")
        with self.stand_in_study(out):
            self.assertEqual(score_rates.main(
                ["score_rates.py", "score", "--slots", self.slots,
                 "--emit-records", records]), 0)
        # §2.4: the tables land in the study root, which is not a parameter.
        self.assertEqual(sorted(os.listdir(out)), ["RATES.md", "RESULTS.json"])
        results = self.published(out)
        self.assertIsNone(results["cell"][score_rates.REGISTRY_OVERRIDE])
        self.assertEqual(results["cell"]["registryOfRecordSha256"], self.registry)
        self.assertEqual(results["population"]["valid"], 4)
        # §8: the emitted record trees are outside the slot tree, and they are
        # the valid runs that produced a parseable array — run-004 held none
        # and has no compiled tree, which §8 states rather than implies.
        self.assertEqual(sorted(os.listdir(records)),
                         ["run-001", "run-002", "run-003"])
        self.assertTrue(os.path.isfile(os.path.join(records, "run-001", "RECORDS.md")))
        self.assertEqual(sorted(os.listdir(self.slots)),
                         ["BATCH.json"] + ["run-00%d" % index
                                           for index in range(1, BATCH_RUNS + 1)])

    def test_the_writer_is_private_and_score_registered_is_its_only_caller(self):
        """§7 claims the publication boundary is one function called from one
        place. Read that off the source rather than off a comment: a second
        caller would be a second way for a dict computed elsewhere to become
        RESULTS.json, which is exactly what the round-3 finding was."""
        import ast

        with open(score_rates.__file__.replace(".pyc", ".py"), "rb") as handle:
            tree = ast.parse(handle.read().decode("utf-8"))
        callers = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name) \
                        and inner.func.id == "_write_outputs":
                    callers.append(node.name)
        self.assertEqual(callers, ["score_registered"])
        # …and its whole signature is the results it is handed: no output
        # directory, so there is no "publish this dict over there" at all.
        import inspect
        self.assertEqual(
            sorted(inspect.signature(score_rates._write_outputs).parameters),
            ["results"])

    def test_the_registered_interface_takes_no_input_path_and_reads_no_environment(self):
        import inspect

        parameters = inspect.signature(score_rates.score_registered).parameters
        # The slot tree, and an output directory for the derived record trees.
        # No registry, no family, no prompt, no golden, no output root: all
        # five are derived from the module's own location, so no caller and no
        # command line can supply one.
        self.assertEqual(sorted(parameters), ["records_dir", "slots_dir"])
        self.assertEqual(sorted(score_rates.SCORE_FLAGS),
                         ["--emit-records", "--slots"])
        # And no environment variable is a way in: the module reads none.
        with open(score_rates.__file__.replace(".pyc", ".py"), "rb") as handle:
            source = handle.read().decode("utf-8")
        for reader in ("os.environ", "getenv", "os.putenv"):
            self.assertNotIn(reader, source,
                             "score_rates.py reads the environment through %r" % reader)

    # --- the rates -----------------------------------------------------------

    def test_the_scored_rates_are_the_profile_the_fixtures_fix(self):
        self.recapture_then_batch()
        results = self.score()
        population = results["population"]
        self.assertEqual(population["slots"], BATCH_RUNS)
        self.assertEqual(population["valid"], 4)
        self.assertEqual(population["invalid"], 1)
        self.assertEqual(population["invalidCodes"], {"call-nonzero-exit": 1})
        self.assertEqual(population["pipelineInvalidRate"]["rate"], 0.2)
        self.assertEqual(population["authoringEmpty"], 1)
        self.assertEqual(population["unexpectedEntries"], [])
        self.assertEqual(population["shortfall"], 0)
        # One stated caution over the batch, and no class's tier moved for it.
        self.assertTrue(population["pipelineCaution"])

        expected = {0: 1, 1: 3, 2: 0, 3: 3, 4: 3, 5: 0}
        for entry in results["classes"]:
            block = entry["coverage"]
            self.assertEqual(block["trials"], 4)
            self.assertEqual(block["count"], expected[entry["index"]],
                             "class %d coverage" % entry["index"])
            self.assertEqual(entry["reviewTier"]["escalations"] or ["none"],
                             ["mislabel"] if entry["index"] == 2 else ["none"])
        raw = {entry["index"]: entry["rawIntersection"]["count"] for entry in results["classes"]}
        self.assertEqual(raw, {0: 1, 1: 3, 2: 3, 3: 3, 4: 3, 5: 0})
        q_only = {entry["index"]: entry["qOnlyIntersection"]["count"]
                  for entry in results["classes"]}
        self.assertEqual(q_only, {0: 0, 1: 0, 2: 3, 3: 0, 4: 0, 5: 0})
        q_any = {entry["index"]: entry["qIntersection"]["count"] for entry in results["classes"]}
        self.assertEqual(q_any, {0: 0, 1: 0, 2: 3, 3: 3, 4: 0, 5: 0})
        # S2's mislabel share: class 2 was reached in three runs and never by
        # a correctly-labelled record, so the share is 1.0 and §5 escalates.
        shares = {entry["index"]: entry["mislabelShare"] for entry in results["classes"]}
        self.assertEqual(shares[2], 1.0)
        self.assertEqual(shares[3], 0.0)
        self.assertEqual(shares[5], 0.0)

        # 3/4 with an exact interval, and the drift sequence in run order.
        one = [entry for entry in results["classes"] if entry["index"] == 1][0]
        self.assertEqual(one["coverage"]["rate"], 0.75)
        self.assertEqual(round(one["coverage"]["ci95"][0], 4), 0.1941)
        self.assertEqual(round(one["coverage"]["ci95"][1], 4), 0.9937)
        self.assertEqual(one["drift"]["sequence"], [1, 1, 1, 0])

        self.assertEqual(results["coverageBreadth"]["distribution"],
                         {"0": 1, "1": 0, "2": 0, "3": 2, "4": 1, "5": 0, "6": 0})
        self.assertEqual(results["coverageBreadth"]["allSix"]["count"], 0)
        self.assertEqual(results["labelAccuracy"]["h"], 13)
        self.assertEqual(results["labelAccuracy"]["q"], 3)
        self.assertEqual(results["labelAccuracy"]["rate"], 0.8125)
        self.assertEqual(results["records"]["acceptedTotal"], 16)
        self.assertEqual(results["records"]["droppedTotal"], 6)
        self.assertEqual(results["records"]["dropCodes"],
                         {"decimal-form": 3, "duplicate-id": 3})
        self.assertEqual(results["distinctOutputs"]["distinctCompletions"], 3)
        self.assertEqual(results["distinctOutputs"]["largestIdenticalGroup"], 2)
        self.assertEqual([row["slot"] for row in results["runs"]],
                         ["run-00%d" % index for index in range(1, BATCH_RUNS + 1)])
        self.assertEqual([row["coveredClasses"] for row in results["runs"][:4]],
                         [[1, 3, 4], [0, 1, 3, 4], [1, 3, 4], []])
        self.assertTrue(results["runs"][3]["authoringEmpty"])
        self.assertTrue(results["runs"][3]["noParseableArray"])
        self.assertTrue(results["runs"][3]["valid"])
        self.assertFalse(results["runs"][4]["valid"])

    def test_the_report_renders_every_class_run_and_tier(self):
        self.recapture_then_batch()
        report = score_rates.render_markdown(self.score())
        for entry in ("run-001", "run-005", "call-nonzero-exit", "Clopper-Pearson",
                      "authoring-empty", "FULL", "Stated caution",
                      "Byte-lineage, not truth"):
            self.assertIn(entry, report)
        self.assertEqual(report.count("| 0 | no sanctions hit"), 1)


if __name__ == "__main__":
    unittest.main()
