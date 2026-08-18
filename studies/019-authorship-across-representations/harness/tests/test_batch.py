#!/usr/bin/env python3
"""The driver's calling half — SCAFFOLD items D1–D8 and G1–G2, and T1.

Two halves, and the division is deliberate.

**The wrapper-driven half** (`WrapperDriven`, `Controls`) runs the REAL
`harness/authoring_call.sh`: the same bash, the same `env -i` scrub, the same
fresh HOME and CODEX_HOME per run, the same binary-digest and CLI-version gates
(the stand-in's digest is pinned in a stand-in registry, so the check passes
because it was SATISFIED and not because it was skipped), the same arm-keyed slot
rule, the same registered timeout ceiling, and the same slot retention. Only the
binary, the operator's home and the directory the wrapper resolves as its own
study are stand-ins — the wrapper's bytes are the committed ones, reached through
a symlinked `harness/` — and none of them reaches a network or a model. `$HOME`
is redirected for every case, so the operator's real credential is never copied
anywhere by this suite.

**The in-process half** runs the driver's own refusals over trees built in a
temporary directory. It needs neither bash nor a CLI, so it runs everywhere.

WHAT IS PATCHED, and why each one. `harness/PINS.json` [D-23]'s rule is that the
population root is DERIVED and no argument names it, so a test that must not
write into the committed tree points the derived constants at its own root
instead. The refusal lines under test are the registered ones; only the roots
move. `batch.STUDY` moves with them, because the wrapper anchors its slot guard
at the `$STUDY` it resolves for ITSELF and a tree it will write into therefore
has to BE a study — the alternative would be an override argument, which the
wrapper's registered interface caps out.

`batch.verify_ported_bytes` is stubbed in the fixtures, and that is a real gap
stated rather than hidden: `integrity.verify()` refuses today for SCAFFOLD item
T3's reason (untracked Python under `design/`, and a `__pycache__` from a 3.8
interpreter), so every case here would fail on a condition none of them is about.
Two cases hold the gate itself instead — that `verify_ported_bytes()` converts an
`IntegrityError` into a `BatchError`, and that `preflight()` calls it BEFORE
anything else — so the gate is exercised as a gate and only the tree hygiene is
someone else's item.

`STUDY_CLI_STANDIN` is the seam that makes every model-call path reachable
without codex. It removes no gate, and `test_the_standin_seam_is_still_digest_gated`
is the proof: pointed at anything under the COMMITTED registry, it refuses at the
same digest check `--cli-override` refuses at.
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import batch
import integrity
import leak_tokens
import make_manifest
import transcript_check

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
STUDY = os.path.dirname(HARNESS)
REGISTRY = os.path.join(HARNESS, "PINS.json")

ENTRIES = batch.schedule_entries()
# One whole round of the registered order — three slots, one per arm, in the
# order the registration puts them (round 1 is W1: A, B, C). The batch is 150
# slots and no test runs it; every case below runs a bounded prefix through
# `--runs`, which is the registered way to run less than the whole order.
ROUND = 3

SENTINEL_CREDENTIAL = '{"OPENAI_API_KEY": "sk-s019-sentinel-never-retained"}\n'
SENTINEL_TOKEN = "sk-s019-sentinel-never-retained"

# codex's own pre-prompt boilerplate, in the shape a real session carries it: it
# quotes the sandbox root and the session home (both normalized away before the
# golden digests are taken) and a date (normalized too). It is arm-INDEPENDENT,
# which is why one golden capture serves all three arms. `_screen_prior()` below
# asserts it carries no leak token, so a fixture cannot pass the golden
# derivation by accident.
PRIOR = (
    ("developer",
     "<permissions_instructions>\nYou are running with a workspace sandbox "
     "rooted at %(cwd)s. Files outside it are read-only.\n"
     "</permissions_instructions>"),
    ("developer",
     "<agent_identity>\nYou are a general coding agent. Current date: "
     "2026-08-15.\nSession files live under %(home)s.\n</agent_identity>"),
    ("user", "<recommended_plugins>\nAirtable, Apollo, Asana\n"
             "</recommended_plugins>"),
)

# The stand-in CLI. It answers --version, writes a session into $CODEX_HOME,
# prints a planned completion and exits with a planned status; it never calls a
# model and never reaches the network. The plan, the counter and the version
# live BESIDE this file, because the wrapper scrubs the environment with `env -i`
# and because a plan inside the binary would change the digest the wrapper checks
# for real.
FAKE_CLI = r'''#!__PYTHON__
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ITEM_KIND = {"user": "input_text", "developer": "input_text",
             "assistant": "output_text"}
PRIOR = __PRIOR__


def message(role, text):
    return {"type": "response_item",
            "payload": {"type": "message", "role": role,
                        "content": [{"type": ITEM_KIND[role], "text": text}]}}


def entries(prompt, answer, cwd, home, model, session_id):
    rows = [{"type": "session_meta",
             "payload": {"id": session_id, "cwd": cwd,
                         "cli_version": "0.145.0-fake"}}]
    for role, template in PRIOR:
        rows.append(message(role, template % {"cwd": cwd, "home": home}))
    rows.append({"type": "response_item",
                 "payload": {"type": "reasoning", "id": "rs_1",
                             "summary": [], "encrypted_content": "opaque"}})
    rows.append({"type": "turn_context",
                 "payload": {"model": model, "cwd": cwd,
                             "current_date": "2026-08-15"}})
    rows.append(message("user", prompt))
    rows.append({"type": "event_msg",
                 "payload": {"type": "agent_message", "message": answer}})
    rows.append(message("assistant", answer))
    return rows


def drop_assistant(rows):
    """A session the CLI wrote with no assistant message in it. Retained
    transcripts like this exist — the process exits 0 after writing a rollout it
    never finished — and `transcript_check.extract_completion()` raises on one,
    which is the POST-CALL helper failure R1-4 is about."""
    return [row for row in rows
            if not (row.get("type") == "response_item"
                    and row["payload"].get("role") == "assistant")]


def poison_prior(rows, needle):
    """A lone surrogate planted in a PRE-prompt developer message. It survives
    `json.dumps` (escaped), it survives `_events` (decoded back to a lone
    surrogate), the last assistant message is untouched so the completion
    extraction succeeds — and `context_digests()` fails on it, because a lone
    surrogate has no UTF-8 encoding. That is a DIFFERENT post-call stage from the
    completion extraction, which is why it is here: the trap has to cover the
    stage nobody thought of, not only the one the review constructed."""
    for row in rows:
        if row.get("type") == "response_item" \
                and row["payload"].get("role") == "developer":
            row["payload"]["content"][0]["text"] += needle
            break
    return rows


def main(argv):
    if "--version" in argv:
        marker = os.path.join(HERE, "version.txt")
        if os.path.exists(marker):
            with open(marker) as handle:
                print(handle.read().strip())
            return 0
        print("codex-cli 0.145.0-fake")
        return 0
    with open(os.path.join(HERE, "plan.json")) as handle:
        plan = json.load(handle)
    counter = os.path.join(HERE, "counter")
    index = 0
    if os.path.exists(counter):
        with open(counter) as handle:
            index = int(handle.read().strip())
    with open(counter, "w") as handle:
        handle.write(str(index + 1))
    step = plan[index] if index < len(plan) else plan[-1]
    if step.get("sleep"):
        time.sleep(step["sleep"])
    prompt = argv[-1]
    model = argv[argv.index("-m") + 1]
    home = os.environ["HOME"]
    sessions = os.path.join(os.environ["CODEX_HOME"], "sessions")
    if step.get("no_session"):
        sys.stdout.write(step["completion"])
        return int(step.get("exit", 0))
    os.makedirs(sessions, exist_ok=True)
    rows = entries(prompt, step["completion"], os.getcwd(), home, model,
                   "00000000-0000-4000-8000-%012d" % (index + 1))
    if step.get("no_assistant"):
        rows = drop_assistant(rows)
    if step.get("poison_prior"):
        rows = poison_prior(rows, step["poison_prior"])
    if step.get("tool_call"):
        rows.insert(-1, {"type": "response_item",
                         "payload": {"type": "function_call", "name": "shell",
                                     "arguments": "{}", "call_id": "c1"}})
    if step.get("extra_turn"):
        rows.append(message("user", "and now revise it"))
        rows.append(message("assistant", step["completion"]))
    path = os.path.join(sessions, "rollout-%d.jsonl" % index)
    with open(path, "wb") as handle:
        for row in rows:
            handle.write((json.dumps(row) + "\n").encode("utf-8"))
    sys.stdout.write(step["completion"])
    return int(step.get("exit", 0))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
'''


# --- fixtures ---------------------------------------------------------------

def _digest(path: str) -> str:
    with open(path, "rb") as handle:
        return "sha256:" + hashlib.sha256(handle.read()).hexdigest()


def throwaway_root(prefix: str = "s019-tests-") -> str:
    """A temporary root whose PATH carries no leak token.

    The wrapper screens the scratch path it builds beneath this root, and every
    slot's recorded working directory lives under it. A machine whose temp
    directory spells a study term — or a random `mkdtemp` suffix that happens to
    contain `d1` — would fail every fixture with a true refusal about the machine
    and a useless one about the code, so the name is re-rolled and, if it cannot
    be found clean, refused loudly."""
    for _attempt in range(64):
        root = tempfile.mkdtemp(prefix=prefix)
        leaked = sorted(token for token in leak_tokens.SCRATCH_TOKENS
                        if token in root.lower())
        if not leaked:
            return root
        shutil.rmtree(root, True)
    raise RuntimeError(
        "could not draw a temporary directory free of this study's leak tokens; "
        "set TMPDIR to a path with no study vocabulary in it and re-run")


def _screen_prior(cwd: str, home: str) -> None:
    """The fixture's own boilerplate must pass the screen the golden derivation
    runs. A fixture that leaked would make `capture_golden()` refuse for a reason
    that is about the fixture, and the refusal would read as a finding."""
    events = [(role, template % {"cwd": cwd, "home": home})
              for role, template in PRIOR]
    transcript_check.screen_prior_context(events, len(events), [cwd, home])


def write_fake_cli(directory: str, plan: list, python: str) -> str:
    """The stand-in CLI plus its plan; returns the binary path whose digest the
    stand-in registry pins, so the wrapper's digest check runs for real."""
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, "codex")
    body = FAKE_CLI.replace("__PYTHON__", python).replace(
        "__PRIOR__", repr([[role, template] for role, template in PRIOR]))
    with open(path, "w") as handle:
        handle.write(body)
    os.chmod(path, 0o755)
    write_plan(directory, plan)
    return path


def write_plan(directory: str, plan: list) -> None:
    """The plan, rewritten without touching the binary — so the digest the
    registry pins does not move and the wrapper's binary check is still a check."""
    with open(os.path.join(directory, "plan.json"), "w") as handle:
        json.dump(plan, handle)


def registered_interpreter() -> str:
    """The running interpreter if it is the one the registry registers, else "".

    Every wrapper-driven case here goes through the wrapper's FIRST gate, the
    registry's `python` member: `batch.invoke()` passes `sys.executable` as
    `PYTHON_BIN`, so under any other interpreter every call would be refused by
    the study's own registration rather than by anything under test."""
    with open(REGISTRY) as handle:
        pins = json.load(handle)
    try:
        return integrity.verify_interpreter(pins)
    except integrity.IntegrityError:
        return ""


RUNNING_REGISTERED = registered_interpreter()
HAVE_TOOLS = all(shutil.which(name) for name in ("bash", "git", "timeout"))


class StandInStudy(unittest.TestCase):
    """The stand-in study, registry, HOME and roots every case here runs
    against. It carries no test of its own."""

    #: cases that need a fake CLI answering more than one call override this
    PLAN = [{"completion": "ready"}] * 12

    def setUp(self):
        self.root = throwaway_root()
        self.addCleanup(shutil.rmtree, self.root, True)
        self.scratch = os.path.join(self.root, "scratch")
        os.makedirs(self.scratch)
        self.home = os.path.join(self.root, "home")
        os.makedirs(os.path.join(self.home, ".codex"))
        with open(os.path.join(self.home, ".codex", "auth.json"), "w") as handle:
            handle.write(SENTINEL_CREDENTIAL)
        environment = mock.patch.dict(os.environ, {"HOME": self.home})
        environment.start()
        self.addCleanup(environment.stop)
        # `STUDY_CLI_STANDIN` must not leak in from the operator's own shell
        # into a case that is about `--cli-override` or about no CLI at all.
        seam = mock.patch.dict(os.environ)
        seam.start()
        self.addCleanup(seam.stop)
        os.environ.pop(batch.STANDIN_ENV, None)

        self.study = self.build_standin_study()
        self.patch("STUDY", self.study)
        self.patch("SCRIPT", os.path.join(self.study, "harness",
                                          "authoring_call.sh"))
        self.arms_root = os.path.join(self.study, "arms")
        self.patch("ARMS_ROOT", self.arms_root)
        self.patch("ATTEMPT_ROOT", os.path.join(self.study, "results",
                                                "primary-attempt-001"))
        self.patch("DEFAULT_NEGATIVE", os.path.join(self.study, "controls",
                                                    "isolation-negative"))
        self.patch("DEFAULT_CAPTURES", os.path.join(self.study, "controls",
                                                    "recapture"))
        self.probe_prompt = os.path.join(self.study, "transcription",
                                         "PROBE-PROMPT.txt")
        self.patch("PROBE_PROMPT", self.probe_prompt)
        self.golden = os.path.join(self.root, "GOLDEN-CONTEXT.json")
        self.patch("DEFAULT_GOLDEN", self.golden)
        # SCAFFOLD T3: `integrity.verify()` refuses on the untracked `design/`
        # sources, which no case here is about. The gate itself is held by
        # `PortedBytesGate` below.
        self.patch("verify_ported_bytes", lambda: {"stubbed": True})

        self.cli_dir = os.path.join(self.root, "cli")
        self.cli = write_fake_cli(self.cli_dir, list(self.PLAN), sys.executable)
        self.pins_path = os.path.join(self.root, "PINS.json")
        self.write_pins(self.stand_in_registry())

    # -- construction ------------------------------------------------------

    def patch(self, name: str, value):
        patched = mock.patch.object(batch, name, value)
        patched.start()
        self.addCleanup(patched.stop)

    def build_standin_study(self) -> str:
        """A stand-in study whose OWN path is what the wrapper resolves as
        `$STUDY`: the committed harness symlinked in — so the bytes that run are
        the committed bytes and only the path they are invoked by moves — the
        three arm prompts, the probe prompt, the preregistration, and a git repo
        so the wrapper's worktree line sees production's shape.

        The returned path is RESOLVED, because the wrapper's anchor compares
        against `pwd -P` and slots built from a symlinked spelling of the same
        directory would every one of them be refused. `arms/` is deliberately NOT
        pre-created: the wrapper's registered branch makes its own anchor, and a
        fixture that made the population root first would falsify every case that
        reads its absence as "no slot was created"."""
        study = os.path.realpath(os.path.join(self.root, "study"))
        os.makedirs(study)
        os.symlink(HARNESS, os.path.join(study, "harness"))
        os.makedirs(os.path.join(study, "transcription"))
        with open(os.path.join(study, "transcription", "PROBE-PROMPT.txt"),
                  "w") as handle:
            handle.write("Reply with the single word ready.\n")
        shutil.copyfile(os.path.join(STUDY, "PREREGISTRATION.md"),
                        os.path.join(study, "PREREGISTRATION.md"))
        for arm in batch.ARMS:
            os.makedirs(os.path.join(study, "arms", arm))
            with open(os.path.join(study, "arms", arm, "PROMPT.txt"), "w") as handle:
                handle.write("Arm %s prompt for the stand-in study.\n" % arm)
        subprocess.run(["git", "init", "-q", study], check=True)
        return study

    def stand_in_registry(self, **edits) -> dict:
        """The committed registry with every freeze pin FILLED, the stand-in
        binary's digest and version moved, and the two lifecycle members
        (`golden.sha256`, `isolationNegative.assent`) left null.

        Everything the batch checks about the ORDER — N, the slot count, the
        block order, the tail, the ceiling — is the committed registry's, so
        these cases run the real `check_registry()` and not a relaxed one. The
        lifecycle members are WRITTEN null rather than inherited because they are
        the study's STAGE and not its registration: `register_golden()` and
        `record_negative_control()` below are this fixture's own ceremony steps,
        and a value read off the committed registry would make every case here a
        function of how far the real ceremony has got."""
        with open(REGISTRY) as handle:
            pins = json.load(handle)
        for name, path in integrity.FREEZE_PINS:
            node = pins
            for key in path[:-1]:
                node = node.setdefault(key, {})
            node[path[-1]] = "sha256:" + hashlib.sha256(name.encode()).hexdigest()
        pins["preregistration"]["sha256"] = _digest(
            os.path.join(self.study, "PREREGISTRATION.md"))
        for arm in batch.ARMS:
            pins["arms"][arm]["promptSha256"] = _digest(
                os.path.join(self.study, "arms", arm, "PROMPT.txt"))
        pins["probePrompt"]["sha256"] = _digest(self.probe_prompt)
        pins["golden"]["sha256"] = None
        pins["isolationNegative"]["assent"] = None
        pins["codex"]["binarySha256"] = _digest(self.cli)
        pins["codex"]["version"] = "codex-cli 0.145.0-fake"
        pins["codex"]["model"] = "s019-stand-in-model"
        pins.update(edits)
        return pins

    def write_pins(self, pins: dict) -> None:
        self.pins = pins
        with open(self.pins_path, "w") as handle:
            json.dump(pins, handle, indent=2)

    def alternate_registry(self, name: str, **edits) -> str:
        pins = json.loads(json.dumps(self.pins))
        pins.update(edits)
        path = os.path.join(self.root, name)
        with open(path, "w") as handle:
            json.dump(pins, handle, indent=2)
        return path

    # -- the ceremony steps the batch is a successor to --------------------

    def write_golden(self, entries=None) -> str:
        """A golden capture on disk and its digest in the registry — the
        recapture's outcome, written rather than run for the cases that are not
        about the recapture itself."""
        with open(self.golden, "w") as handle:
            json.dump({"contextVersion": "1",
                       "entries": entries if entries is not None else [],
                       "capturedFrom": ["capture-001", "capture-002"]},
                      handle, indent=2)
        pins = json.loads(json.dumps(self.pins))
        pins["golden"]["sha256"] = _digest(self.golden)
        self.write_pins(pins)
        return pins["golden"]["sha256"]

    def record_negative_control(self, **edits) -> str:
        """The isolation negative control's record and its assent, as the
        ceremony leaves them — written with the members the REAL writer writes,
        so no case here stands on a record `capture_isolation_negative()` could
        never have produced."""
        pins = json.loads(json.dumps(self.pins))
        pins["isolationNegative"]["assent"] = "granted"
        self.write_pins(pins)
        verdict = {"control": "the isolation gate's power",
                   "registeredExpectation": "the golden match FAILS",
                   "registeredOutcomes": list(batch.C7_OUTCOMES),
                   "outcome": "refused",
                   "message": "the golden pre-prompt context was not reproduced",
                   "wrapperExit": 0,
                   "wrapperCode": None,
                   "goldenSha256": _digest(self.golden),
                   "deletedByCode": {"session.jsonl": "sha256:" + "0" * 64},
                   "assent": "granted",
                   "retention": "This file and a stripped CALL.json are always "
                                "retained."}
        verdict.update(edits)
        os.makedirs(batch.DEFAULT_NEGATIVE, exist_ok=True)
        path = os.path.join(batch.DEFAULT_NEGATIVE, "VERDICT.json")
        with open(path, "w") as handle:
            json.dump(verdict, handle, indent=2)
        return path

    def ready(self) -> None:
        """Both ceremony steps, in the registered order: the golden first, the
        control behind it."""
        self.write_golden()
        self.record_negative_control()

    # -- the registered commands, as an operator would give them -----------

    def run_command(self, *extra, pins_path: str = None):
        return batch.main(["batch.py", "run", "--scratch-parent", self.scratch,
                           "--pins", pins_path or self.pins_path,
                           "--cli-override", self.cli] + list(extra))

    def refusal(self, callable_, *args, **kwargs) -> str:
        with self.assertRaises(batch.BatchError) as caught:
            callable_(*args, **kwargs)
        return str(caught.exception)


# --- the pieces that need no wrapper and no CLI -----------------------------

class RegisteredConstants(unittest.TestCase):
    """The constants the port's two known-owed edits are about."""

    def test_the_wrapper_code_table_is_derived_and_carries_status_twelve(self):
        """SCAFFOLD's second known-owed edit. Study 012 mapped 10 and 11 in a
        second hand-written table; this study's status 12 is exactly the case
        where two hand-written tables drift, so there is one table and the other
        is derived from it."""
        self.assertEqual(
            batch.WRAPPER_CODES,
            {status: (None if code == "complete" else code)
             for status, (code, _gloss) in batch.WRAPPER_EXIT_MEANINGS.items()})
        self.assertEqual(batch.WRAPPER_CODES[12], "call-timeout")
        self.assertIsNone(batch.WRAPPER_CODES[0])
        # …and every code it can emit that is not a success is on §1a's
        # apparatus side or is the pre-call refusal that spends nothing.
        for status, code in batch.WRAPPER_CODES.items():
            if code in (None, "preflight-refused"):
                continue
            self.assertEqual(batch.CODE_PARTITION[code][0], "apparatus", status)

    def test_the_ledger_temporary_is_a_registered_constant_path(self):
        """SCAFFOLD's first known-owed edit. A `mkstemp` name is not statically
        readable, so no reader of this file can resolve it and no test can check
        it. A constant can be both."""
        self.assertEqual(batch.LEDGER_TEMP_NAME, "BATCH.json.partial")
        self.assertIn("LEDGER_TEMP_NAME", batch.__dict__)

    def test_the_ledger_temporary_needs_no_exclusion_entry_here(self):
        """Study 012 needed `arms/BATCH.json.partial` in a `freeze.excluded`
        list because its manifest scanned the whole tree. This study's manifest
        is ADR 0004's EXACT SET, which reaches no byte under `arms/`, so the
        exclusion is by construction — asserted here rather than assumed."""
        relative = "arms/" + batch.LEDGER_TEMP_NAME
        self.assertNotIn(relative, make_manifest.manifest_entries())
        self.assertFalse(batch.covered_by_manifest(relative))
        self.assertFalse(batch.covered_by_manifest("arms/BATCH.json"))
        self.assertFalse(batch.covered_by_manifest("arms/SHORTFALL.json"))

    def test_the_attempt_root_is_the_no_new_slots_marker(self):
        self.assertEqual(os.path.relpath(batch.ATTEMPT_ROOT, STUDY),
                         os.path.join("results", "primary-attempt-001"))

    def test_the_wrapper_lives_beside_this_driver(self):
        self.assertEqual(batch.SCRIPT,
                         os.path.join(HARNESS, "authoring_call.sh"))
        self.assertTrue(os.path.isfile(batch.SCRIPT))

    def test_an_unknown_command_prints_the_usage_and_returns_two(self):
        import contextlib
        import io
        buffer = io.StringIO()
        with contextlib.redirect_stderr(buffer):
            self.assertEqual(batch.main(["batch.py"]), 2)
            self.assertEqual(batch.main(["batch.py", "score"]), 2)
        for command in batch.COMMANDS:
            self.assertIn("batch.py " + command, buffer.getvalue())

    def test_the_plan_command_publishes_the_order_without_a_registry(self):
        """The command the module had while the calling half was unported, kept
        because it is the one way to read the registered order without a
        registry, a wrapper or a call."""
        import contextlib
        import io
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.assertEqual(batch.main(["batch.py", "plan"]), 0)
        printed = buffer.getvalue()
        self.assertIn("150 slots, 50 rounds, 3 arms", printed)
        self.assertIn("position spread 1, transition spread 1, "
                      "self-successions 0", printed)
        self.assertIn("2700 s", printed)

    def test_the_c7_outcome_set_is_defined_here_for_the_scorer_to_read(self):
        """Change 10: Study 012 kept this in `score_rates.py`. The driver's
        preflight is one of the two gates that must read it and this study's
        scorer does not exist yet, so it is defined here — one list, not two."""
        self.assertEqual(batch.C7_OUTCOMES, ("refused", "matched", "no-context"))

    def test_a_manifest_covered_destination_refuses(self):
        """`require_lawful_destination()` rewritten for ADR 0004's exact set
        (change 11): a destination is lawful when writing into it cannot add a
        covered entry."""
        for relative in ("harness", "harness/tests", "PREREGISTRATION.md",
                         "harness/PORTS.md"):
            message = self.assertRaises(batch.BatchError)
            with message:
                batch.require_lawful_destination(
                    os.path.join(STUDY, relative), "--out")
        for relative in ("controls/recapture", "transcription", "arms",
                         "results/x"):
            batch.require_lawful_destination(os.path.join(STUDY, relative), "--out")

    def test_a_destination_outside_the_study_is_lawful(self):
        root = throwaway_root()
        self.addCleanup(shutil.rmtree, root, True)
        batch.require_lawful_destination(root, "--captures")

    def test_a_second_name_for_the_study_refuses_rather_than_guessing(self):
        """Fails closed on what it cannot decide: a target outside the study by
        name that shares a directory OBJECT with it has no computable
        study-relative path."""
        root = throwaway_root()
        self.addCleanup(shutil.rmtree, root, True)
        alias = os.path.join(root, "alias")
        os.symlink(STUDY, alias)
        # A symlink resolves, so this one is decided; the undecidable case is an
        # ancestor sharing identity, which `_identity_overlap()` answers.
        self.assertTrue(batch._identity_overlap(os.path.realpath(STUDY),
                                                os.path.realpath(alias)))


class PortedBytesGate(unittest.TestCase):
    """`verify_ported_bytes()` is stubbed by the fixtures above, so it is held
    here instead — as a gate, and as the FIRST thing preflight does."""

    def test_an_integrity_refusal_becomes_a_batch_refusal(self):
        with mock.patch.object(
                integrity, "verify",
                side_effect=integrity.IntegrityError("the port drifted")):
            with self.assertRaises(batch.BatchError) as caught:
                batch.verify_ported_bytes()
        self.assertIn("the ported bytes are not the registered ones",
                      str(caught.exception))
        self.assertIn("the port drifted", str(caught.exception))

    def test_preflight_verifies_the_ported_bytes_before_anything_else(self):
        """Given arguments that are wrong in every other way as well, the
        refusal is still this one: a drifted port is checked before a call is
        spent, and before any cheaper refusal can mask it."""
        with mock.patch.object(batch, "verify_ported_bytes",
                               side_effect=batch.BatchError("ported bytes")):
            with self.assertRaises(batch.BatchError) as caught:
                batch.preflight([], [], "/nonexistent", "/nonexistent",
                                None, "registered")
        self.assertEqual(str(caught.exception), "ported bytes")


class PreflightGates(StandInStudy):
    """D2 — every refusal that must land before a single invocation."""

    def plan_first_round(self):
        entries = ENTRIES[:ROUND]
        return entries, [batch.slot_path(entry) for entry in entries]

    def preflight(self, pins_path: str = None):
        entries, slots = self.plan_first_round()
        return batch.preflight(entries, slots, self.scratch,
                               pins_path or self.pins_path, self.cli,
                               "registered")

    def test_the_registered_ceremony_passes(self):
        """The positive case, first: with the golden registered and the control
        on record, preflight returns the pins rather than refusing. Without it
        every refusal below could be passing for the wrong reason."""
        self.ready()
        self.assertEqual(self.preflight()["codex"]["model"], "s019-stand-in-model")

    def test_a_pilot_registry_spends_nothing(self):
        """Change 6: the freeze gate is the whole registered label rule, not one
        pin. Study 014's round 3 found a registered run reachable with only the
        preregistration digest filled."""
        self.ready()
        for name, path in integrity.FREEZE_PINS:
            if name in integrity.CEREMONY_LIFECYCLE_PINS:
                # `golden.sha256` and `isolationNegative.assent` are freeze pins
                # (round-1 R1-9) that the PRE-FREEZE ceremony writes, so this
                # gate cannot demand them without demanding the values the
                # capture and the control exist to create. Their own gates
                # refuse them at this stage — `Controls` below drives both — and
                # `test_pins.py` asserts the exemption is exactly these two.
                continue
            pins = json.loads(json.dumps(self.pins))
            node = pins
            for key in path[:-1]:
                node = node[key]
            node[path[-1]] = None
            registry = self.alternate_registry("pilot.json", **pins)
            message = self.refusal(self.preflight, registry)
            self.assertIn("labels this study PILOT", message)
            self.assertIn(name, message)

    def test_an_edited_preregistration_refuses(self):
        self.ready()
        with open(os.path.join(self.study, "PREREGISTRATION.md"), "a") as handle:
            handle.write("\nedited after the freeze\n")
        self.assertIn("it was edited after the freeze",
                      self.refusal(self.preflight))

    def test_a_registry_naming_another_order_refuses(self):
        """The registry's order is EXPANDED and compared, not read member by
        member: a registry holding the same letters in another arrangement is a
        different call order.

        Both refusals are exercised, because a registry can name an order that
        is lawful-but-other or one that is not lawful at all. `W1 W2 W3 W5 W4 W6`
        with the tail `W2 W3` also attains the registered floor and is still a
        different order; `W1…W6` in their natural order self-succeeds seventeen
        times and is refused by `schedule()`'s own floor guard."""
        self.ready()
        order = json.loads(json.dumps(self.pins["batch"]))
        order["order"]["blockOrder"] = ["W1", "W2", "W3", "W5", "W4", "W6"]
        order["order"]["tail"] = ["W2", "W3"]
        registry = self.alternate_registry("order.json", batch=order)
        self.assertIn("expands to a different call order",
                      self.refusal(self.preflight, registry))
        order["order"]["blockOrder"] = ["W1", "W2", "W3", "W4", "W5", "W6"]
        order["order"]["tail"] = ["W4", "W6"]
        registry = self.alternate_registry("unbalanced.json", batch=order)
        self.assertIn("self-successions", self.refusal(self.preflight, registry))

    def test_a_registry_naming_another_n_refuses(self):
        self.ready()
        for member, value in (("n", 25), ("slots", 75), ("arms", ["A", "B"])):
            block = json.loads(json.dumps(self.pins["batch"]))
            block[member] = value
            registry = self.alternate_registry("n.json", batch=block)
            self.assertIn("harness/PINS.json registers batch.%s" % member,
                          self.refusal(self.preflight, registry))

    def test_a_registry_naming_another_ceiling_refuses(self):
        """Three files must not hold three ceilings: the wrapper reads the
        registry's number, the driver classifies on its own constant, and the
        two are compared before any call."""
        self.ready()
        block = json.loads(json.dumps(self.pins["batch"]))
        block["callTimeoutSeconds"] = 60
        registry = self.alternate_registry("ceiling.json", batch=block)
        message = self.refusal(self.preflight, registry)
        self.assertIn("60 s ceiling", message)
        self.assertIn("2700 s", message)

    def test_every_arms_prompt_is_checked_before_slot_one(self):
        """All three arms exist from round 1 under the interleaved order, so all
        three are checked before slot 1 — not the first arm's alone."""
        self.ready()
        for arm in batch.ARMS:
            path = os.path.join(self.study, "arms", arm, "PROMPT.txt")
            original = open(path).read()
            with open(path, "w") as handle:
                handle.write(original + "drifted")
            message = self.refusal(self.preflight)
            self.assertIn("arm %s's arms/%s/PROMPT.txt" % (arm, arm), message)
            with open(path, "w") as handle:
                handle.write(original)

    def test_no_slot_is_created_after_a_rate_has_been_computed(self):
        self.ready()
        os.makedirs(batch.ATTEMPT_ROOT)
        self.assertIn("no slot may be created in any arm after a rate has been "
                      "computed", self.refusal(self.preflight))

    def test_a_ledger_temporary_residue_refuses_before_a_call(self):
        """`_write_json_atomic()` refuses to write over the temporary, and that
        refusal would otherwise land AFTER the first call had been spent."""
        self.ready()
        os.makedirs(self.arms_root, exist_ok=True)
        open(os.path.join(self.arms_root, batch.LEDGER_TEMP_NAME), "w").close()
        self.assertIn("left the ledger's temporary behind",
                      self.refusal(self.preflight))

    def test_no_slot_is_created_before_the_golden_is_registered(self):
        """Both halves: the capture must be on disk AND its digest must be in
        the registry. A skipped recapture then costs nothing instead of costing a
        hundred and fifty calls."""
        self.ready()
        pins = json.loads(json.dumps(self.pins))
        pins["golden"]["sha256"] = None
        registry = self.alternate_registry("nogolden.json", **pins)
        self.assertIn("registers no golden.sha256",
                      self.refusal(self.preflight, registry))
        os.unlink(self.golden)
        self.assertIn("no golden context at", self.refusal(self.preflight))

    def test_a_swapped_golden_refuses(self):
        self.ready()
        with open(self.golden, "a") as handle:
            handle.write("\n")
        self.assertIn("not the registered", self.refusal(self.preflight))

    def test_the_isolation_control_is_a_precondition_of_the_batch(self):
        """Study 012's round 9 finding 3: the assent gated the control's own
        command and nothing else, so 150 calls were reachable with the control
        never run."""
        self.write_golden()
        self.assertIn("records isolationNegative.assent None",
                      self.refusal(self.preflight))

    def test_a_control_record_that_is_not_this_batchs_refuses(self):
        self.write_golden()
        self.record_negative_control(goldenSha256="sha256:" + "0" * 64)
        self.assertIn("demonstrates the power of the gate THIS batch runs behind",
                      self.refusal(self.preflight))

    def test_a_control_record_the_writer_could_not_have_written_refuses(self):
        """The shape check both gates share: three members whose shape is fixed
        on every path the writer takes."""
        self.write_golden()
        for edits, fragment in (
                ({"registeredOutcomes": ["refused"]}, "registeredOutcomes"),
                ({"deletedByCode": []}, "deletedByCode"),
                ({"wrapperExit": True}, "wrapperExit")):
            self.record_negative_control(**edits)
            message = self.refusal(self.preflight)
            self.assertIn("the record is not one this driver wrote", message)
            self.assertIn(fragment, message)

    def test_an_unregistered_control_outcome_refuses(self):
        self.write_golden()
        self.record_negative_control(outcome="inconclusive")
        self.assertIn("is not a control that ran", self.refusal(self.preflight))

    def test_a_retained_slot_is_never_rewritten(self):
        self.ready()
        entries, slots = self.plan_first_round()
        os.makedirs(slots[1])
        self.assertIn("these slots already exist and are never rewritten",
                      self.refusal(self.preflight))

    def test_a_dangling_link_at_a_slot_path_is_a_slot_that_exists(self):
        """`lexists`, not `exists`: a dangling symlink is absent to `exists()`
        and present to `mkdir`, so the batch used to pass preflight and then die
        of an uncaught FileExistsError with no call spent and no refusal
        recorded."""
        self.ready()
        entries, slots = self.plan_first_round()
        os.makedirs(os.path.dirname(slots[0]))
        os.symlink(os.path.join(self.root, "nothing-here"), slots[0])
        self.assertIn("these slots already exist", self.refusal(self.preflight))

    def test_a_cli_override_that_is_not_the_pinned_binary_refuses(self):
        self.ready()
        other = os.path.join(self.root, "other-codex")
        with open(other, "w") as handle:
            handle.write("#!/bin/sh\nexit 0\n")
        entries, slots = self.plan_first_round()
        message = self.refusal(batch.preflight, entries, slots, self.scratch,
                               self.pins_path, other, "registered")
        self.assertIn("not the pinned", message)

    def test_the_standin_seam_resolves_like_an_override(self):
        """Change 12. The seam names a CLI when `--cli-override` does not, and
        one resolution point serves preflight, the invocation and the ledger
        header alike."""
        self.assertIsNone(batch.resolve_cli(None))
        os.environ[batch.STANDIN_ENV] = self.cli
        self.assertEqual(batch.resolve_cli(None), self.cli)
        self.assertEqual(batch.resolve_cli("/elsewhere"), "/elsewhere")

    def test_the_standin_seam_is_still_digest_gated(self):
        """The seam removes NO gate. Under a registry that pins the real codex
        digest, a stand-in named through the environment refuses at exactly the
        check `--cli-override` refuses at."""
        self.ready()
        with open(REGISTRY) as handle:
            committed = json.load(handle)
        pins = json.loads(json.dumps(self.pins))
        pins["codex"]["binarySha256"] = committed["codex"]["binarySha256"]
        registry = self.alternate_registry("committed-binary.json", **pins)
        os.environ[batch.STANDIN_ENV] = self.cli
        entries, slots = self.plan_first_round()
        message = self.refusal(batch.preflight, entries, slots, self.scratch,
                               registry, batch.resolve_cli(None), "registered")
        self.assertIn("not the pinned", message)
        self.assertIn(committed["codex"]["binarySha256"], message)


class OutOfSchedule(StandInStudy):
    """D7 — no invocation plans a slot the registered order does not have."""

    def test_runs_past_the_end_of_the_order_refuses(self):
        self.ready()
        self.assertIn("asks for more slots than the registered order has left",
                      self.refusal(batch.run_batch, batch.REGISTERED_SLOTS + 1,
                                   False, self.scratch, self.pins_path,
                                   self.cli, True))

    def test_a_zero_run_batch_refuses(self):
        self.ready()
        self.assertIn("a batch needs at least one run",
                      self.refusal(batch.run_batch, 0, False, self.scratch,
                                   self.pins_path, self.cli, True))

    def test_preflight_bounds_the_last_planned_global_index(self):
        """Checked even though the entries are a slice of the expansion and
        cannot exceed it by construction: "cannot happen by construction" is a
        claim about today's code, and this is a claim about the study."""
        self.ready()
        beyond = dict(ENTRIES[-1])
        beyond["globalIndex"] = batch.REGISTERED_SLOTS + 1
        message = self.refusal(batch.preflight, [beyond],
                               [os.path.join(self.arms_root, "x")], self.scratch,
                               self.pins_path, self.cli, "registered")
        self.assertIn("no invocation may plan a slot past the registered order",
                      message)

    def test_resume_with_no_ledger_refuses(self):
        self.ready()
        self.assertIn("there is nothing to resume at",
                      self.refusal(batch.run_batch, 1, True, self.scratch,
                                   self.pins_path, self.cli, True))

    def test_the_removed_flags_refuse_by_name(self):
        for flag in batch.REMOVED:
            self.assertEqual(1, batch.main(
                ["batch.py", "run", "--scratch-parent", self.scratch, flag, "x"]))


class SealAndLedger(StandInStudy):
    """D4, D5 and D6 over slots built in process — no bash and no CLI."""

    def build_slot(self, entry: dict, *, refusal: tuple = None) -> str:
        """One slot in the shape the wrapper retains plus the three schedule
        stamps the driver adds, built in process."""
        slot = batch.slot_path(entry)
        os.makedirs(slot)
        call = {"slot": os.path.basename(slot), "slotIndex": entry["slotIndex"],
                "arm": entry["arm"],
                "armPromptSha256": batch.arm_prompt(self.pins, entry["arm"])[1],
                "promptKind": "registered", "exitStatus": 0,
                "startedAt": "2026-08-15T00:0%d:00Z" % entry["globalIndex"],
                "endedAt": "2026-08-15T00:1%d:00Z" % entry["globalIndex"],
                "cwd": os.path.join(self.scratch, "cwd-%d" % entry["globalIndex"]),
                "home": os.path.join(self.scratch, "home-%d" % entry["globalIndex"])}
        if refusal is None:
            with open(os.path.join(slot, "CALL.json"), "w") as handle:
                json.dump(call, handle)
            batch.stamp_slot(slot, entry, self.pins)
        else:
            status, code = refusal
            batch.refuse_slot(slot, code, status, "stderr tail")
        return slot

    def seal_and_record(self, count: int) -> list:
        records, previous = [], None
        for entry in ENTRIES[:count]:
            slot = self.build_slot(entry)
            manifest = batch.seal_slot(slot, entry)
            records.append(batch.ledger_record(entry, slot, 0, None, manifest,
                                               previous))
            previous = batch.record_digest(records[-1])
        return records

    # -- D4 ---------------------------------------------------------------

    def test_the_seal_lists_the_root_and_every_entry_beneath_it(self):
        entry = ENTRIES[0]
        slot = self.build_slot(entry)
        os.symlink("/nowhere", os.path.join(slot, "dangling"))
        os.mkdir(os.path.join(slot, "sub"))
        files = batch.slot_files(slot)
        rows = {row[0]: row for row in files}
        self.assertEqual(rows["."][1:], [batch.NON_FILE_LENGTH, "type:directory"])
        self.assertEqual(rows["dangling"][1:], [batch.NON_FILE_LENGTH,
                                                "type:symlink"])
        self.assertEqual(rows["sub"][1:], [batch.NON_FILE_LENGTH,
                                           "type:directory"])
        self.assertIn("CALL.json", rows)
        self.assertNotIn(batch.MANIFEST_NAME, rows)

    def test_a_slot_is_sealed_once(self):
        entry = ENTRIES[0]
        slot = self.build_slot(entry)
        batch.seal_slot(slot, entry)
        self.assertIn("a slot is sealed once",
                      self.refusal(batch.seal_slot, slot, entry))

    def test_a_seal_recomputes_and_an_added_entry_breaks_it(self):
        entry = ENTRIES[0]
        slot = self.build_slot(entry)
        digest = batch.seal_slot(slot, entry)
        self.assertEqual(batch.verify_seal_of(slot, entry), digest)
        os.symlink("/nowhere", os.path.join(slot, "added-after-the-seal"))
        self.assertIn("does not verify against the slot it seals",
                      self.refusal(batch.verify_seal_of, slot, entry))

    def test_a_manifest_that_is_not_this_slots_refuses(self):
        entry, other = ENTRIES[0], ENTRIES[3]
        slot = self.build_slot(entry)
        batch.seal_slot(slot, entry)
        self.assertIn("the manifest is not this slot's",
                      self.refusal(batch.verify_seal_of, slot, other))

    def test_an_unreadable_seal_refuses_through_the_registered_path(self):
        entry = ENTRIES[0]
        slot = self.build_slot(entry)
        with open(os.path.join(slot, batch.MANIFEST_NAME), "w") as handle:
            handle.write('{"slot": 1, "slot": 2}')
        self.assertIn("cannot be read as duplicate-free JSON",
                      self.refusal(batch.verify_seal_of, slot, entry))

    # -- the stamps -------------------------------------------------------

    def test_the_driver_writes_the_three_schedule_stamps_once(self):
        entry = ENTRIES[0]
        slot = self.build_slot(entry)
        call = json.load(open(os.path.join(slot, "CALL.json")))
        for member in ("globalIndex", "round", "position"):
            self.assertEqual(call[member], entry[member])
        self.assertIn("the schedule stamps are written once",
                      self.refusal(batch.stamp_slot, slot, entry, self.pins))

    def test_a_wrapper_that_names_the_wrong_arm_stops_the_batch(self):
        entry = ENTRIES[0]
        slot = batch.slot_path(entry)
        os.makedirs(slot)
        wrong = "B" if entry["arm"] != "B" else "C"
        with open(os.path.join(slot, "CALL.json"), "w") as handle:
            json.dump({"arm": wrong, "slotIndex": entry["slotIndex"],
                       "armPromptSha256":
                           batch.arm_prompt(self.pins, entry["arm"])[1]}, handle)
        self.assertIn("the batch stops here rather than spending the remaining "
                      "slots", self.refusal(batch.stamp_slot, slot, entry,
                                            self.pins))

    def test_a_run_made_with_another_arms_bytes_stops_the_batch(self):
        entry = ENTRIES[0]
        slot = batch.slot_path(entry)
        os.makedirs(slot)
        other = "B" if entry["arm"] != "B" else "C"
        with open(os.path.join(slot, "CALL.json"), "w") as handle:
            json.dump({"arm": entry["arm"], "slotIndex": entry["slotIndex"],
                       "armPromptSha256":
                           batch.arm_prompt(self.pins, other)[1]}, handle)
        self.assertIn("made with bytes that are not the arm's",
                      self.refusal(batch.stamp_slot, slot, entry, self.pins))

    def test_a_slot_with_no_call_record_is_left_to_the_scorer(self):
        entry = ENTRIES[0]
        slot = self.build_slot(entry, refusal=(10, "call-nonzero-exit"))
        batch.stamp_slot(slot, entry, self.pins)           # returns, silently
        self.assertFalse(os.path.exists(os.path.join(slot, "CALL.json")))

    # -- D5 ---------------------------------------------------------------

    def test_the_ledger_is_a_chain_in_schedule_order(self):
        records = self.seal_and_record(ROUND)
        batch.verify_prefix(records, ENTRIES)
        self.assertIsNone(records[0]["previousSha256"])
        for earlier, later in zip(records, records[1:]):
            self.assertEqual(later["previousSha256"],
                             batch.record_digest(earlier))

    def test_a_broken_chain_refuses(self):
        records = self.seal_and_record(ROUND)
        records[2]["previousSha256"] = "sha256:" + "0" * 64
        self.assertIn("the ledger's hash chain breaks",
                      self.refusal(batch.verify_ledger_chain, records))

    def test_a_record_naming_the_wrong_path_is_not_the_registered_prefix(self):
        """Study 012's round 8 finding 5: the path is DERIVED and compared, so a
        record carrying the right schedule keys and a path the order never
        assigns cannot verify as the prefix."""
        records = self.seal_and_record(1)
        records[0]["path"] = "README.md"
        self.assertIn("diverges from §2's registered call order at position 1",
                      self.refusal(batch.verify_prefix, records, ENTRIES))

    def test_a_ledger_longer_than_the_order_is_not_a_prefix(self):
        records = self.seal_and_record(1) * (batch.REGISTERED_SLOTS + 1)
        self.assertIn("is not a prefix of it",
                      self.refusal(batch.verify_prefix, records, ENTRIES))

    def test_the_ledger_is_refused_rather_than_re_sorted(self):
        records = self.seal_and_record(ROUND)
        batch.write_ledger(list(reversed(records)), self.pins, None)
        # `write_ledger` sorts by global index, so a REORDERED file has to be
        # written by hand — which is exactly the state the driver refuses.
        path = os.path.join(self.arms_root, batch.LEDGER_NAME)
        body = json.load(open(path))
        body["records"] = list(reversed(body["records"]))
        with open(path, "w") as handle:
            json.dump(body, handle)
        self.assertIn("the ledger is append-only", self.refusal(batch.load_ledger))

    def test_a_ledger_that_is_not_an_object_refuses_by_name(self):
        os.makedirs(self.arms_root, exist_ok=True)
        path = os.path.join(self.arms_root, batch.LEDGER_NAME)
        for body, fragment in (("[]", "decodes to a JSON list"),
                               ('{"records": 3}', "records member is a JSON int"),
                               ('{"batchVersion": "0"}', "carries no records member")):
            with open(path, "w") as handle:
                handle.write(body)
            self.assertIn(fragment, self.refusal(batch.load_ledger))

    def test_the_ledger_is_written_atomically_through_the_registered_temporary(self):
        records = self.seal_and_record(1)
        batch.write_ledger(records, self.pins, None)
        temporary = os.path.join(self.arms_root, batch.LEDGER_TEMP_NAME)
        self.assertFalse(os.path.exists(temporary))
        open(temporary, "w").close()
        self.assertIn("already exists and this run did not create it",
                      self.refusal(batch.write_ledger, records, self.pins, None))

    # -- D6 ---------------------------------------------------------------

    def test_a_ledger_and_a_tree_that_agree_reconcile_to_nothing(self):
        records = self.seal_and_record(ROUND)
        self.assertIsNone(batch.reconcile_ledger(records, ENTRIES))

    def test_one_sealed_unrecorded_slot_is_completed_from_its_own_seal(self):
        """The seal-then-record window. The slot RAN — the wrapper returned, the
        driver stamped and sealed it — and only the append was interrupted."""
        records = self.seal_and_record(ROUND)
        orphan = ENTRIES[ROUND]
        slot = self.build_slot(orphan)
        manifest = batch.seal_slot(slot, orphan)
        completed = batch.reconcile_ledger(records, ENTRIES)
        self.assertEqual(completed["globalIndex"], orphan["globalIndex"])
        self.assertEqual(completed["manifestSha256"], manifest)
        self.assertEqual(completed["previousSha256"],
                         batch.record_digest(records[-1]))
        self.assertEqual(completed["code"], None)

    def test_a_refused_orphan_is_completed_with_its_own_code(self):
        records = self.seal_and_record(ROUND)
        orphan = ENTRIES[ROUND]
        slot = self.build_slot(orphan, refusal=(12, "call-timeout"))
        batch.seal_slot(slot, orphan)
        completed = batch.reconcile_ledger(records, ENTRIES)
        self.assertEqual((completed["wrapperExit"], completed["code"]),
                         (12, "call-timeout"))

    def test_two_orphans_are_not_an_interrupted_append(self):
        records = self.seal_and_record(ROUND)
        for orphan in ENTRIES[ROUND:ROUND + 2]:
            slot = self.build_slot(orphan)
            batch.seal_slot(slot, orphan)
        self.assertIn("can leave at most ONE",
                      self.refusal(batch.reconcile_ledger, records, ENTRIES))

    def test_an_unsealed_orphan_is_not_admitted(self):
        records = self.seal_and_record(ROUND)
        self.build_slot(ENTRIES[ROUND])
        self.assertIn("is not sealed",
                      self.refusal(batch.reconcile_ledger, records, ENTRIES))

    def test_a_recorded_slot_that_is_gone_refuses(self):
        records = self.seal_and_record(ROUND)
        shutil.rmtree(batch.slot_path(ENTRIES[1]))
        self.assertIn("slot(s) that are not on disk",
                      self.refusal(batch.reconcile_ledger, records, ENTRIES))

    def test_a_slot_at_an_index_the_order_never_assigns_refuses(self):
        """Study 012's round 7 finding 4: reconciliation is over every slot
        PRESENT, not over the canonical paths the order would name next, so a
        `run-099` in an arm's tree is not invisible to it."""
        records = self.seal_and_record(ROUND)
        stray = os.path.join(self.arms_root, "A", "authoring", "run-099")
        os.makedirs(stray)
        self.assertIn("registered order does not put next",
                      self.refusal(batch.reconcile_ledger, records, ENTRIES))

    def test_a_slot_outcome_is_read_from_the_slots_own_bytes(self):
        entry = ENTRIES[0]
        slot = self.build_slot(entry)
        self.assertEqual(batch.slot_outcome(slot), (0, None))
        shutil.rmtree(slot)
        slot = self.build_slot(entry, refusal=(11, "slot-shape"))
        self.assertEqual(batch.slot_outcome(slot), (11, "slot-shape"))

    def test_a_refusal_record_naming_a_code_this_driver_never_writes_refuses(self):
        entry = ENTRIES[0]
        slot = self.build_slot(entry, refusal=(12, "call-timeout"))
        path = os.path.join(slot, "REFUSAL.json")
        body = json.load(open(path))
        body["code"] = "session-count"
        with open(path, "w") as handle:
            json.dump(body, handle)
        self.assertIn("is not one this batch produced",
                      self.refusal(batch.slot_outcome, slot))

    def test_a_slot_with_neither_artifact_is_not_terminal(self):
        entry = ENTRIES[0]
        os.makedirs(batch.slot_path(entry))
        self.assertIn("it is not a terminal slot",
                      self.refusal(batch.slot_outcome, batch.slot_path(entry)))

    # -- D8 ---------------------------------------------------------------

    def test_completed_rounds_counts_whole_rounds_only(self):
        """Study 012's round 3 finding 15: a prefix that ends mid-round declares
        the round BEFORE it, and zero when none is whole. The declaration used
        the LAST SLOT's round, so a batch that died two slots into round 1
        reported a round that never finished."""
        records = self.seal_and_record(ROUND + 1)
        self.assertEqual(batch.completed_rounds([]), 0)
        self.assertEqual(batch.completed_rounds(records[:ROUND - 1]), 0)
        self.assertEqual(batch.completed_rounds(records[:ROUND]), 1)
        self.assertEqual(batch.completed_rounds(records), 1)

    def test_the_shortfall_reads_a_clock_it_does_not_hold(self):
        self.ready()
        records = self.seal_and_record(ROUND)
        batch.write_ledger(records, self.pins, None)
        self.assertEqual(batch.declare_shortfall("the window closed",
                                                 self.pins_path), 0)
        declared = json.load(open(os.path.join(self.arms_root,
                                               batch.SHORTFALL_NAME)))
        self.assertEqual(declared["completedRounds"], 1)
        self.assertEqual(declared["completedThroughGlobalIndex"], ROUND)
        self.assertEqual(declared["completedSlots"], ROUND)
        self.assertEqual(declared["registeredSlots"], batch.REGISTERED_SLOTS)
        self.assertEqual(declared["reason"], "the window closed")
        self.assertEqual(declared["lastSlotEndedAt"], "2026-08-15T00:13:00Z")
        self.assertEqual(declared["lastSlotEndedAtFrom"], declared["lastSlot"])

    def test_the_clock_falls_back_and_names_the_slot_it_came_from(self):
        """A tail whose wrapper refused at preflight wrote no CALL.json and
        therefore stamped no clock; the declaration names the slot the clock it
        publishes came from rather than recording a bare null."""
        self.ready()
        records, previous = [], None
        for offset, entry in enumerate(ENTRIES[:ROUND]):
            slot = self.build_slot(entry, refusal=(1, "preflight-refused")
                                   if offset == ROUND - 1 else None)
            manifest = batch.seal_slot(slot, entry)
            status, code = batch.slot_outcome(slot)
            records.append(batch.ledger_record(entry, slot, status, code,
                                               manifest, previous))
            previous = batch.record_digest(records[-1])
        batch.write_ledger(records, self.pins, None)
        batch.declare_shortfall("stopped", self.pins_path)
        declared = json.load(open(os.path.join(self.arms_root,
                                               batch.SHORTFALL_NAME)))
        self.assertNotEqual(declared["lastSlotEndedAtFrom"], declared["lastSlot"])
        self.assertEqual(declared["lastSlotEndedAt"], "2026-08-15T00:12:00Z")

    def test_a_batch_that_is_not_short_may_not_declare_one(self):
        """A terminal batch is exactly 150 slots or a SHORTFALL.json, never
        both: this is the half that refuses the declaration."""
        self.ready()
        records, previous = [], None
        for entry in ENTRIES:
            slot = batch.slot_path(entry)
            os.makedirs(slot)
            open(os.path.join(slot, "CALL.json"), "w").write("{}")
            records.append(batch.ledger_record(entry, slot, 0, None, "sha256:x",
                                               previous))
            previous = batch.record_digest(records[-1])
        self.assertIn("a shortfall declares a SHORT batch, and this one is not "
                      "short", self.refusal(batch.declare_shortfall, "why",
                                            self.pins_path))

    def test_a_shortfall_is_never_declared_twice_or_after_a_rate(self):
        self.ready()
        records = self.seal_and_record(1)
        batch.write_ledger(records, self.pins, None)
        batch.declare_shortfall("first", self.pins_path)
        self.assertIn("already exists",
                      self.refusal(batch.declare_shortfall, "second",
                                   self.pins_path))
        os.unlink(os.path.join(self.arms_root, batch.SHORTFALL_NAME))
        os.makedirs(batch.ATTEMPT_ROOT)
        self.assertIn("may not be declared after a rate has been computed",
                      self.refusal(batch.declare_shortfall, "third",
                                   self.pins_path))

    def test_a_shortfall_needs_a_reason(self):
        self.ready()
        self.assertIn("a shortfall without a reason is a gap",
                      self.refusal(batch.declare_shortfall, "", self.pins_path))

    def test_a_declaration_over_a_disagreeing_tree_refuses(self):
        self.ready()
        records = self.seal_and_record(ROUND)
        batch.write_ledger(records, self.pins, None)
        stray = os.path.join(self.arms_root, "A", "authoring", "run-099")
        os.makedirs(stray)
        self.assertIn("registered order does not put next",
                      self.refusal(batch.declare_shortfall, "x", self.pins_path))


# --- the wrapper-driven half ------------------------------------------------

@unittest.skipUnless(RUNNING_REGISTERED and HAVE_TOOLS,
                     "the wrapper refuses an interpreter harness/PINS.json does "
                     "not register, and needs bash, git and timeout(1)")
class WrapperDriven(StandInStudy):
    """D3, D7 and D8 with the REAL wrapper in the loop.

    What this proves that a unit test cannot: that a failing run terminates its
    own slot with a refusal record and the batch CONTINUES; that the slots the
    wrapper writes carry the arm, the arm prompt digest and the three schedule
    stamps, in the arm's own tree; that resumption by global schedule index
    merges the ledger rather than replacing it; and that no retained byte carries
    the credential."""

    PLAN = [{"completion": "records for A"},
            {"completion": "records for B"},
            {"completion": "records for C", "exit": 3},
            {"completion": "records for the fourth slot"},
            {"completion": "records for the fifth slot"},
            {"completion": "records for the sixth slot"}]

    def test_a_round_runs_seals_and_records_and_a_failure_does_not_stop_it(self):
        self.ready()
        self.assertEqual(self.run_command("--runs", str(ROUND)), 0)
        ledger = json.load(open(os.path.join(self.arms_root, batch.LEDGER_NAME)))
        self.assertEqual(len(ledger["records"]), ROUND)
        self.assertEqual([row["code"] for row in ledger["records"]],
                         [None, None, "call-nonzero-exit"])
        for record, entry in zip(ledger["records"], ENTRIES):
            slot = os.path.join(self.study, record["path"])
            self.assertTrue(os.path.isdir(slot))
            # the slot is in the ARM's own tree, at the arm's own index
            self.assertEqual(os.path.basename(os.path.dirname(
                os.path.dirname(slot))), entry["arm"])
            call = json.load(open(os.path.join(slot, "CALL.json")))
            self.assertEqual(call["arm"], entry["arm"])
            self.assertEqual(call["armPromptSha256"],
                             batch.arm_prompt(self.pins, entry["arm"])[1])
            self.assertEqual(call["globalIndex"], entry["globalIndex"])
            self.assertEqual(call["round"], entry["round"])
            self.assertEqual(call["position"], entry["position"])
            self.assertEqual(call["slotIndex"], entry["slotIndex"])
            self.assertEqual(call["goldenSha256"], self.pins["golden"]["sha256"])
            self.assertEqual(call["timeoutSeconds"], batch.CALL_TIMEOUT_SECONDS)
            self.assertFalse(call["timedOut"])
            # …and it is sealed, and the seal recomputes
            self.assertEqual(batch.verify_seal_of(slot, entry),
                             record["manifestSha256"])
        # the refused slot carries its refusal record and no completion
        refused = os.path.join(self.study, ledger["records"][2]["path"])
        self.assertTrue(os.path.isfile(os.path.join(refused, "REFUSAL.json")))
        self.assertFalse(os.path.exists(os.path.join(refused, "completion.txt")))

    def test_no_retained_byte_carries_the_credential(self):
        self.ready()
        self.run_command("--runs", "1")
        found = []
        for base, _dirs, names in os.walk(self.arms_root):
            for name in names:
                with open(os.path.join(base, name), "rb") as handle:
                    if SENTINEL_TOKEN.encode() in handle.read():
                        found.append(os.path.join(base, name))
        self.assertEqual(found, [])

    def test_a_batch_is_resumed_and_never_restarted(self):
        self.ready()
        self.run_command("--runs", "1")
        self.assertIn("never restarted", _stderr(self.run_command, "--runs", "1"))
        self.assertEqual(self.run_command("--resume", "--runs", "1"), 0)
        ledger = json.load(open(os.path.join(self.arms_root, batch.LEDGER_NAME)))
        self.assertEqual([row["globalIndex"] for row in ledger["records"]], [1, 2])
        # the resume MERGED: the first record still carries the status the first
        # invocation retained, which is recorded nowhere else.
        self.assertEqual(ledger["records"][0]["wrapperExit"], 0)

    def test_a_resume_completes_the_interrupted_append_before_it_calls(self):
        """The crash window closed on the resume that follows it."""
        self.ready()
        self.run_command("--runs", "2")
        path = os.path.join(self.arms_root, batch.LEDGER_NAME)
        body = json.load(open(path))
        body["records"] = body["records"][:1]          # the append never landed
        with open(path, "w") as handle:
            json.dump(body, handle)
        self.assertEqual(self.run_command("--resume", "--runs", "1"), 0)
        ledger = json.load(open(path))
        self.assertEqual([row["globalIndex"] for row in ledger["records"]],
                         [1, 2, 3])
        batch.verify_prefix(ledger["records"], ENTRIES)

    def test_a_dry_run_creates_nothing(self):
        self.ready()
        self.assertEqual(self.run_command("--runs", "2", "--dry-run"), 0)
        self.assertFalse(os.path.exists(os.path.join(self.arms_root,
                                                     batch.LEDGER_NAME)))
        self.assertFalse(os.path.exists(os.path.join(self.arms_root, "A",
                                                     "authoring")))

    def test_the_standin_seam_reaches_the_wrapper(self):
        """Every model-call path is reachable without codex — and by the seam
        alone, with no `--cli-override` on the command line."""
        self.ready()
        os.environ[batch.STANDIN_ENV] = self.cli
        self.assertEqual(batch.main(["batch.py", "run", "--scratch-parent",
                                     self.scratch, "--pins", self.pins_path,
                                     "--runs", "1"]), 0)
        ledger = json.load(open(os.path.join(self.arms_root, batch.LEDGER_NAME)))
        self.assertEqual(ledger["cliOverride"], self.cli)

    def test_a_shortfall_over_a_wrapper_written_prefix(self):
        self.ready()
        self.run_command("--runs", str(ROUND))
        self.assertEqual(batch.declare_shortfall("the window closed",
                                                 self.pins_path), 0)
        declared = json.load(open(os.path.join(self.arms_root,
                                               batch.SHORTFALL_NAME)))
        self.assertEqual(declared["completedSlots"], ROUND)
        self.assertEqual(declared["completedRounds"], 1)
        self.assertTrue(declared["lastSlotEndedAt"].endswith("Z"))

    # -- R1-7: the declaration schema ---------------------------------------

    def declared_shortfall(self, runs=ROUND):
        """A real batch, a real declaration, and the declaration read back."""
        self.ready()
        self.run_command("--runs", str(runs))
        self.assertEqual(batch.declare_shortfall("the window closed",
                                                 self.pins_path), 0)
        path = os.path.join(self.arms_root, batch.SHORTFALL_NAME)
        with open(path) as handle:
            return json.load(handle), path

    def test_the_declaration_carries_the_ledger_head_and_the_seal_inventory(self):
        """R1-7. The declaration used to be a bag of counts over which `{}` was
        accepted; it carries the evidence now — the ledger's file digest, the
        chain head the records compute to, and one row per slot with its place
        in §2's order, its path, its SEAL and its §1a code."""
        declared, _path = self.declared_shortfall()
        ledger_path = os.path.join(self.arms_root, batch.LEDGER_NAME)
        ledger = json.load(open(ledger_path))
        self.assertEqual(declared["declarationVersion"], batch.SHORTFALL_VERSION)
        self.assertEqual(declared["ledgerSha256"], _digest(ledger_path))
        self.assertEqual(declared["ledgerHeadSha256"],
                         batch.record_digest(ledger["records"][-1]))
        self.assertEqual(len(declared["slots"]), ROUND)
        for row, record, entry in zip(declared["slots"], ledger["records"],
                                      ENTRIES):
            self.assertEqual(sorted(row), sorted(batch.SHORTFALL_SLOT_SCHEMA))
            self.assertEqual(row["globalIndex"], entry["globalIndex"])
            self.assertEqual(row["path"], record["path"])
            self.assertEqual(row["manifestSha256"], record["manifestSha256"])
            # …and the seal the row names recomputes from the slot on disk
            self.assertEqual(
                batch.verify_seal_of(os.path.join(self.study, row["path"]),
                                     entry),
                row["manifestSha256"])

    def test_the_driver_validates_its_own_declaration_on_write(self):
        """The declaration goes through the SAME two functions the scorer runs
        on read, before it is written. A declaration the driver cannot validate
        is one the driver does not write — the alternative is a file that
        unblocks scoring and describes nothing."""
        declared, _path = self.declared_shortfall()
        batch.validate_shortfall(declared)
        records = json.load(open(os.path.join(self.arms_root,
                                              batch.LEDGER_NAME)))["records"]
        batch.verify_shortfall(declared, records, declared["ledgerSha256"])

    def test_an_empty_object_is_not_a_declaration(self):
        """The exact fail-open R1-7 names: `{}` made an arbitrary incomplete set
        terminal and the scorer went on to compute ordinary endpoints over it."""
        self.assertIn("carries no completedRounds member",
                      self.refusal(batch.validate_shortfall, {}))

    def test_a_declaration_over_a_non_prefix_refuses(self):
        """Outcome-selective deletion, which counts alone can never see: keep
        the slots you liked, declare the rest short. A set chosen by what its
        slots CONTAINED is not a prefix of the registered order."""
        declared, _path = self.declared_shortfall()
        declared["slots"] = [declared["slots"][0], declared["slots"][2]]
        declared["completedSlots"] = 2
        declared["completedRounds"] = 0
        declared["completedThroughGlobalIndex"] = declared["slots"][-1]["globalIndex"]
        declared["lastSlot"] = declared["slots"][-1]["path"]
        self.assertIn("A declaration is a PREFIX of the registered order",
                      self.refusal(batch.validate_shortfall, declared))

    def test_a_count_that_outruns_the_inventory_refuses(self):
        """Every count is DERIVED from the inventory under it, so a declaration
        cannot claim more slots than it can name."""
        declared, _path = self.declared_shortfall()
        declared["completedSlots"] = ROUND + 1
        self.assertIn("no count can outlive the evidence",
                      self.refusal(batch.validate_shortfall, declared))

    def test_a_declaration_naming_another_ledger_refuses(self):
        """Both bindings, because they fail differently: the chain head moves if
        a record's content changed, and the file digest moves if the file was
        rewritten around the same records."""
        declared, _path = self.declared_shortfall()
        records = json.load(open(os.path.join(self.arms_root,
                                              batch.LEDGER_NAME)))["records"]
        moved = json.loads(json.dumps(declared))
        moved["ledgerHeadSha256"] = "sha256:" + "0" * 64
        self.assertIn("names a ledger this one is not",
                      self.refusal(batch.verify_shortfall, moved, records,
                                   declared["ledgerSha256"]))
        moved = json.loads(json.dumps(declared))
        moved["ledgerSha256"] = "sha256:" + "0" * 64
        self.assertIn("declares the ledger file digest",
                      self.refusal(batch.verify_shortfall, moved, records,
                                   declared["ledgerSha256"]))

    def test_a_declaration_whose_seal_is_not_the_ledgers_refuses(self):
        declared, _path = self.declared_shortfall()
        records = json.load(open(os.path.join(self.arms_root,
                                              batch.LEDGER_NAME)))["records"]
        declared["slots"][1]["manifestSha256"] = "sha256:" + "0" * 64
        self.assertIn("is not the ledger's record",
                      self.refusal(batch.verify_shortfall, declared, records,
                                   declared["ledgerSha256"]))

    def test_a_declaration_carrying_an_unpartitioned_code_refuses(self):
        """R1-4 and R1-7 meet here: the sentinel that used to reach every
        denominator cannot reach a declaration either."""
        declared, _path = self.declared_shortfall()
        declared["slots"][0]["code"] = "wrapper-error"
        self.assertIn("on neither side of §1a's partition",
                      self.refusal(batch.validate_shortfall, declared))

    def test_a_declaration_carrying_an_unregistered_member_refuses(self):
        declared, _path = self.declared_shortfall()
        declared["scoreThisAnyway"] = True
        self.assertIn("members the declaration schema does not name",
                      self.refusal(batch.validate_shortfall, declared))

    def test_a_declaration_over_a_full_batch_is_not_short(self):
        declared, _path = self.declared_shortfall()
        declared["slots"] = declared["slots"] * 60
        self.assertIn("a shortfall declares a SHORT batch",
                      self.refusal(batch.validate_shortfall, declared))


@unittest.skipUnless(RUNNING_REGISTERED and HAVE_TOOLS,
                     "the wrapper refuses an interpreter harness/PINS.json does "
                     "not register, and needs bash, git and timeout(1)")
class TimeoutCeiling(StandInStudy):
    """T1's middle case, which was smoke-tested by hand and by nothing that
    re-runs: the ceiling FIRES, the wrapper exits 12, and `CALL.json` carries
    `timedOut: true` with the ceiling and the grace stamped.

    Driven through the PROBE path, because `check_registry()` refuses a
    registered-order batch whose registry names a ceiling other than the
    registered 2700 s — which is itself the guarantee working."""

    PLAN = [{"completion": "never printed", "sleep": 30}]

    def test_the_ceiling_fires_and_stamps_the_slot(self):
        pins = json.loads(json.dumps(self.pins))
        pins["batch"]["callTimeoutSeconds"] = 2
        pins["batch"]["timeoutKillAfterSeconds"] = 1
        registry = self.alternate_registry("fast-ceiling.json", **pins)
        slot = os.path.join(self.root, "captures", "capture-001")
        status, code, _stderr = batch.invoke(slot, self.scratch, registry,
                                             self.cli, "probe", batch.PROBE_ARM,
                                             self.probe_prompt)
        self.assertEqual((status, code), (12, "call-timeout"))
        call = json.load(open(os.path.join(slot, "CALL.json")))
        self.assertTrue(call["timedOut"])
        self.assertEqual(call["timeoutSeconds"], 2)
        self.assertEqual(call["timeoutKillAfterSeconds"], 1)
        self.assertFalse(os.path.exists(os.path.join(slot, "completion.txt")))

    def test_a_timeout_is_an_apparatus_failure_and_not_an_authoring_outcome(self):
        """The design-phase lesson, asserted at the code that classifies rather
        than in the table alone: whatever the wrapper's exit 12 means, the
        driver's own map puts it on §1a's apparatus side."""
        self.assertEqual(batch.CODE_PARTITION[batch.WRAPPER_CODES[12]][0],
                         "apparatus")

    def test_a_registry_without_a_usable_ceiling_refuses_before_the_call(self):
        for value in (0, "soon", None):
            pins = json.loads(json.dumps(self.pins))
            pins["batch"]["callTimeoutSeconds"] = value
            registry = self.alternate_registry("bad-ceiling.json", **pins)
            slot = os.path.join(self.root, "captures-%s" % value, "capture-001")
            status, code, stderr = batch.invoke(
                slot, self.scratch, registry, self.cli, "probe",
                batch.PROBE_ARM, self.probe_prompt)
            self.assertEqual((status, code), (1, "preflight-refused"), stderr)
            self.assertFalse(os.path.exists(slot))


@unittest.skipUnless(RUNNING_REGISTERED and HAVE_TOOLS,
                     "the wrapper refuses an interpreter harness/PINS.json does "
                     "not register, and needs bash, git and timeout(1)")
class WrapperExitPaths(StandInStudy):
    """R1-4: EVERY exit path of the real wrapper, end to end through the real
    bash, and the code each one lands on.

    The finding this class exists for: the wrapper runs under `set -euo
    pipefail`, and its three POST-CALL stages — the completion extraction, the
    CALL.json write, the context digests — are plain commands under it. A helper
    that raised killed the shell with status 1, the driver's table read status 1
    as "a pre-call refusal; nothing was called", and `preflight-refused` was in
    neither side of §1a's partition — so `population()`, which excludes only the
    codes it recognises as apparatus, put a slot whose call HAD been made and
    whose completion was MISSING into the arm's denominator as an ordinary
    authoring run scoring zero. Two statuses, one partition, no sentinel.

    Every case here runs the committed `authoring_call.sh` through
    `batch.invoke()` or through the driver's own `run` command; nothing is
    stubbed but the CLI, whose digest the stand-in registry pins."""

    #: index 0 exits 0; the plan is rewritten per case by `plan()`
    PLAN = [{"completion": "ready"}] * 6

    def plan(self, *steps):
        """Rewrite the stand-in CLI's plan without touching the binary, so the
        wrapper's digest gate still runs for real, and reset the counter so the
        next call is step 0."""
        write_plan(self.cli_dir, list(steps))
        counter = os.path.join(self.cli_dir, "counter")
        if os.path.exists(counter):
            os.unlink(counter)

    def probe(self, name):
        slot = os.path.join(self.root, name, "capture-001")
        return batch.invoke(slot, self.scratch, self.pins_path, self.cli,
                            "probe", batch.PROBE_ARM, self.probe_prompt), slot

    # -- one case per registered status ------------------------------------

    def test_status_zero_is_a_complete_slot(self):
        self.plan({"completion": "an answer"})
        (status, code, stderr), slot = self.probe("complete")
        self.assertEqual((status, code), (0, None), stderr)
        self.assertTrue(os.path.isfile(os.path.join(slot, "completion.txt")))
        self.assertTrue(os.path.isfile(os.path.join(slot, "context.json")))

    def test_status_one_is_the_pre_call_refusal_and_nothing_was_called(self):
        """The wrapper's own pre-call guard, reached before any plan step: the
        slot path already exists."""
        slot = os.path.join(self.root, "taken", "capture-001")
        os.makedirs(slot)
        status, code, stderr = batch.invoke(slot, self.scratch, self.pins_path,
                                            self.cli, "probe", batch.PROBE_ARM,
                                            self.probe_prompt)
        self.assertEqual((status, code), (1, "preflight-refused"), stderr)
        self.assertFalse(os.path.exists(os.path.join(self.cli_dir, "counter")))

    def test_status_ten_is_the_nonzero_call(self):
        self.plan({"completion": "partial", "exit": 3})
        (status, code, stderr), slot = self.probe("nonzero")
        self.assertEqual((status, code), (10, "call-nonzero-exit"), stderr)
        self.assertFalse(os.path.exists(os.path.join(slot, "completion.txt")))

    def test_status_eleven_is_the_slot_shape(self):
        self.plan({"completion": "no rollout", "no_session": True})
        (status, code, stderr), _slot = self.probe("shape")
        self.assertEqual((status, code), (11, "slot-shape"), stderr)

    def test_status_thirteen_is_the_post_call_helper_the_review_constructed(self):
        """THE regression. The call succeeds, the transcript is retained, and
        `extract_completion()` raises on a session that holds no assistant
        message — the first post-call stage. Before R1-4 this exited 1 and the
        slot was filed as a pre-call refusal that had spent nothing."""
        self.plan({"completion": "written nowhere", "no_assistant": True})
        (status, code, stderr), slot = self.probe("post-call-extract")
        self.assertEqual((status, code), (13, "post-call-failure"), stderr)
        self.assertIn("a post-call wrapper stage failed", stderr)
        # the call HAPPENED and the slot IS retained: the two facts status 1
        # asserted the opposite of
        self.assertTrue(os.path.isfile(os.path.join(slot, "session.jsonl")))
        self.assertFalse(os.path.exists(os.path.join(slot, "completion.txt")))

    def test_status_thirteen_covers_a_later_post_call_stage_too(self):
        """The trap is a PHASE, not a wrapper around one helper: a lone
        surrogate in the pre-prompt context leaves the completion extraction and
        the CALL.json write intact and fails `context_digests()`, the last stage.
        It lands on the same status and the same code."""
        self.plan({"completion": "an answer", "poison_prior": "\ud800"})
        (status, code, stderr), slot = self.probe("post-call-context")
        self.assertEqual((status, code), (13, "post-call-failure"), stderr)
        self.assertTrue(os.path.isfile(os.path.join(slot, "completion.txt")))
        self.assertTrue(os.path.isfile(os.path.join(slot, "CALL.json")))
        self.assertFalse(os.path.exists(os.path.join(slot, "context.json")))

    # -- and what the driver then does with them ----------------------------

    def test_every_wrapper_status_this_suite_reaches_is_in_the_partition(self):
        """The three diffs §1a registers, closed over the statuses the cases
        above actually produced rather than over the table alone."""
        for status in (0, 1, 10, 11, 12, 13):
            code = batch.wrapper_code(status)
            if code is None:
                continue
            self.assertIn(code, batch.CODE_PARTITION, status)
            self.assertEqual(batch.CODE_PARTITION[code][0], "apparatus", status)

    def test_a_post_call_failure_is_sealed_ledgered_and_excluded(self):
        """End to end through `batch.py run`: the failing slot is retained,
        refused, sealed and ledgered under a code the partition names on the
        APPARATUS side — the denominator it used to enter as an authoring run."""
        self.ready()
        self.plan({"completion": "first", },
                  {"completion": "second", "no_assistant": True},
                  {"completion": "third"})
        self.assertEqual(self.run_command("--runs", str(ROUND)), 0)
        ledger = json.load(open(os.path.join(self.arms_root, batch.LEDGER_NAME)))
        codes = [row["code"] for row in ledger["records"]]
        self.assertEqual(codes, [None, "post-call-failure", None])
        record = ledger["records"][1]
        self.assertEqual(record["wrapperExit"], 13)
        self.assertEqual(batch.CODE_PARTITION[record["code"]][0], "apparatus")
        slot = os.path.join(self.study, record["path"])
        refusal = json.load(open(os.path.join(slot, "REFUSAL.json")))
        self.assertEqual(refusal["code"], "post-call-failure")
        # the seal covers it, and the driver's own reader agrees with the record
        self.assertEqual(batch.verify_seal_of(slot, ENTRIES[1]),
                         record["manifestSha256"])
        self.assertEqual(batch.slot_outcome(slot), (13, "post-call-failure"))

    def test_no_slot_is_ever_written_under_a_code_outside_the_partition(self):
        """The fail-closed half, at the three writers: the refusal record, the
        ledger record, and the slot reader. `wrapper-error` was the sentinel that
        reached all three."""
        slot = os.path.join(self.root, "unpartitioned", "run-001")
        self.assertIn("§1a's partition does not name it",
                      self.refusal(batch.refuse_slot, slot, "wrapper-error", 7, ""))
        self.assertFalse(os.path.exists(slot))
        self.assertIn("§1a's partition does not name it",
                      self.refusal(batch.ledger_record, ENTRIES[0], slot, 7,
                                   "wrapper-error", "sha256:0", None))
        # and a REFUSAL.json planted with the sentinel refuses on the way back in
        os.makedirs(slot)
        with open(os.path.join(slot, "REFUSAL.json"), "w") as handle:
            json.dump({"code": "wrapper-error", "wrapperExit": 7}, handle)
        self.assertIn("unregistered status is not a refusal code",
                      self.refusal(batch.slot_outcome, slot))


@unittest.skipUnless(RUNNING_REGISTERED and HAVE_TOOLS,
                     "the wrapper refuses an interpreter harness/PINS.json does "
                     "not register, and needs bash, git and timeout(1)")
class TranscriptBindingAtTheSeal(StandInStudy):
    """R1-5, driver side: the full binding runs on every completed slot, its
    verdict is retained INSIDE the seal, and each refusal names the side §1a
    puts the run on.

    `harness/tests/test_transcript_binding.py` holds the adversarial cases over
    synthetic transcripts. What is here is the WIRING: that the driver reaches
    `transcript_check.classify()` at all (the finding was that no scored slot
    ever did), that the verdict is sealed with the slot, and that the two sides
    reach the two codes end to end through the real wrapper and the real bash."""

    PLAN = [{"completion": "an artifact"}] * 8

    def plan(self, *steps):
        write_plan(self.cli_dir, list(steps))
        counter = os.path.join(self.cli_dir, "counter")
        if os.path.exists(counter):
            os.unlink(counter)

    def golden_from_a_real_call(self) -> None:
        """The stand-in fixture's `write_golden()` writes an EMPTY entry list,
        which no real session reproduces; every case here needs a golden the
        apparatus actually produces. So one probe call is made and its own
        `context.json` becomes the golden — the derivation the recapture command
        performs, reduced to the one capture these cases need."""
        slot = os.path.join(self.root, "seed", "capture-001")
        status, code, stderr = batch.invoke(slot, self.scratch, self.pins_path,
                                            self.cli, "probe", batch.PROBE_ARM,
                                            self.probe_prompt)
        self.assertEqual((status, code), (0, None), stderr)
        with open(os.path.join(slot, "context.json")) as handle:
            self.write_golden(json.load(handle)["entries"])
        self.record_negative_control()

    def bound(self, index=0):
        ledger = json.load(open(os.path.join(self.arms_root, batch.LEDGER_NAME)))
        record = ledger["records"][index]
        slot = os.path.join(self.study, record["path"])
        with open(os.path.join(slot, batch.TRANSCRIPT_NAME)) as handle:
            return json.load(handle), slot, record

    def test_a_clean_slot_binds_and_the_verdict_is_inside_the_seal(self):
        """The prompt bytes, the golden context, the completion, the model, the
        cwd and the exit status — all six gates, on a slot the batch produced,
        which is the invocation R1-5 says never happened."""
        self.golden_from_a_real_call()
        self.plan({"completion": "an artifact"})
        self.assertEqual(self.run_command("--runs", "1"), 0)
        verdict, slot, record = self.bound()
        self.assertTrue(verdict["admissible"], verdict)
        self.assertIsNone(verdict["reason"])
        self.assertIsNone(verdict["code"])
        # inside the seal: the manifest lists it, and the seal recomputes
        manifest = json.load(open(os.path.join(slot, batch.MANIFEST_NAME)))
        self.assertIn(batch.TRANSCRIPT_NAME,
                      [row[0] for row in manifest["files"]])
        self.assertEqual(batch.verify_seal_of(slot, ENTRIES[0]),
                         record["manifestSha256"])

    def test_the_prompt_reaches_the_transcript_byte_exact(self):
        """The trailing newline. `$(cat FILE)` strips it, so the argv the model
        received was not the bytes the wrapper's own digest gate had just pinned,
        and gate 2 could never have passed for a prompt file ending in one —
        which every arm prompt here does. Unreachable while the gate was
        unwired, and load-bearing the moment it is."""
        self.golden_from_a_real_call()
        prompt_path = os.path.join(self.study, "arms", "A", "PROMPT.txt")
        with open(prompt_path, "rb") as handle:
            self.assertTrue(handle.read().endswith(b"\n"))
        self.plan({"completion": "an artifact"})
        self.assertEqual(self.run_command("--runs", "1"), 0)
        self.assertTrue(self.bound()[0]["admissible"])

    def test_a_tool_call_in_the_transcript_is_an_authoring_outcome(self):
        """The attribution R1-5 turns on: the author disobeyed §3's no-tools
        instruction, so the run STAYS in the denominator wearing an authoring
        code and scoring zero. Excluding it as apparatus would delete exactly
        the runs the instruction exists to catch."""
        self.golden_from_a_real_call()
        self.plan({"completion": "an artifact", "tool_call": True})
        self.assertEqual(self.run_command("--runs", "1"), 0)
        verdict, _slot, _record = self.bound()
        self.assertFalse(verdict["admissible"])
        self.assertEqual(verdict["reason"], "tool-use")
        self.assertEqual(verdict["side"], "authoring")
        self.assertEqual(verdict["code"], "author-protocol-violation")
        self.assertEqual(batch.CODE_PARTITION[verdict["code"]][0], "authoring")

    def test_an_extra_turn_after_the_prompt_is_an_authoring_outcome(self):
        self.golden_from_a_real_call()
        self.plan({"completion": "an artifact", "extra_turn": True})
        self.assertEqual(self.run_command("--runs", "1"), 0)
        verdict, _slot, _record = self.bound()
        self.assertEqual((verdict["reason"], verdict["side"]),
                         ("extra-turn", "authoring"))

    def test_a_drifted_golden_context_is_apparatus(self):
        """The other side of the same wire. The pre-prompt context is not what
        the pinned capture says, so the run leaves every denominator — and the
        code is the one §1a already registered for it."""
        self.golden_from_a_real_call()
        drifted = json.load(open(self.golden))["entries"]
        drifted[0]["sha256"] = "0" * 64
        self.write_golden(drifted)
        # …and the negative control is re-recorded against the capture THIS
        # batch runs behind, which §6 requires and the driver enforces.
        self.record_negative_control()
        self.plan({"completion": "an artifact"})
        self.assertEqual(self.run_command("--runs", "1"), 0)
        verdict, _slot, _record = self.bound()
        self.assertEqual((verdict["reason"], verdict["side"], verdict["code"]),
                         ("context-mismatch", "apparatus", "transcript-refused"))
        self.assertEqual(batch.CODE_PARTITION[verdict["code"]][0], "apparatus")

    def test_a_refused_slot_is_not_bound(self):
        """A slot the wrapper refused already carries an apparatus code naming
        the cause, and half its bytes are missing by construction; binding it
        would answer 'unreadable' over a fact REFUSAL.json states precisely."""
        self.golden_from_a_real_call()
        self.plan({"completion": "no rollout", "no_session": True})
        self.assertEqual(self.run_command("--runs", "1"), 0)
        ledger = json.load(open(os.path.join(self.arms_root, batch.LEDGER_NAME)))
        slot = os.path.join(self.study, ledger["records"][0]["path"])
        self.assertEqual(ledger["records"][0]["code"], "slot-shape")
        self.assertFalse(os.path.exists(os.path.join(slot,
                                                     batch.TRANSCRIPT_NAME)))

    def test_the_binding_never_stops_the_batch(self):
        """A per-slot verdict is a per-slot outcome. The driver records it and
        keeps going; the population rule — not D3 — decides what it costs."""
        self.golden_from_a_real_call()
        self.plan({"completion": "one", "tool_call": True},
                  {"completion": "two"},
                  {"completion": "three", "extra_turn": True})
        self.assertEqual(self.run_command("--runs", str(ROUND)), 0)
        sides = [self.bound(index)[0]["side"] for index in range(ROUND)]
        self.assertEqual(sides, ["authoring", None, "authoring"])


@unittest.skipUnless(RUNNING_REGISTERED and HAVE_TOOLS,
                     "the wrapper refuses an interpreter harness/PINS.json does "
                     "not register, and needs bash, git and timeout(1)")
class Controls(StandInStudy):
    """G1 and G2 — the golden capture and the isolation negative control."""

    PLAN = [{"completion": "ready"}] * 6

    def setUp(self):
        super().setUp()
        _screen_prior(os.path.join(self.scratch, "cwd"),
                      os.path.join(self.scratch, "home"))
        self.captures = os.path.join(self.root, "recapture")
        self.out = os.path.join(self.root, "captured", "GOLDEN.json")

    def capture(self, *extra):
        return batch.main(["batch.py", "capture", "--scratch-parent", self.scratch,
                           "--pins", self.pins_path, "--cli-override", self.cli,
                           "--captures", self.captures, "--out", self.out]
                          + list(extra))

    # -- G1 ---------------------------------------------------------------

    def test_two_agreeing_probe_captures_derive_the_golden(self):
        self.assertEqual(self.capture("--runs", "2"), 0)
        golden = json.load(open(self.out))
        self.assertEqual(golden["contextVersion"], "1")
        self.assertEqual(len(golden["capturedFrom"]), 2)
        # three pre-prompt items, and their normalized digests reproduced across
        # two calls made in two different scratch directories and two homes
        self.assertEqual([entry["role"] for entry in golden["entries"]],
                         ["developer", "developer", "user"])

    def test_one_capture_can_never_derive_a_golden(self):
        """The floor is enforced where the DERIVATION happens, not only in the
        command that makes the calls."""
        self.assertIn("could never produce one", _stderr(self.capture, "--runs", "1"))
        self.assertFalse(os.path.exists(self.captures))

    def test_two_copies_of_one_call_are_not_two_captures(self):
        """The hole `require_distinct_sessions()` closes: two slots holding one
        call's evidence agree by construction rather than by reproduction."""
        self.capture("--runs", "2")
        attempt = batch.next_attempt(self.captures)
        os.makedirs(attempt)
        source = os.path.join(self.captures, "attempt-1", "capture-001")
        for name in ("capture-001", "capture-002"):
            shutil.copytree(source, os.path.join(attempt, name))
        out = os.path.join(self.root, "second.json")
        self.assertIn("agree by construction rather than by reproduction",
                      self.refusal(batch.capture_golden, attempt, out, 2,
                                   self.pins_path))

    def test_a_golden_is_never_derived_from_the_batchs_own_runs(self):
        directory = os.path.join(self.root, "not-a-capture")
        os.makedirs(os.path.join(directory, "run-001"))
        self.assertIn("never from the batch's own runs",
                      self.refusal(batch.capture_slots, directory))

    def test_a_capture_is_never_rewritten_and_a_recapture_cannot_redefine_it(self):
        """A capture taken after the batch scores golden-mismatch; it does not
        redefine the golden. The command refuses to rewrite, and the registry
        pins the file the slots were made under."""
        self.capture("--runs", "2")
        self.assertIn("a registered capture is never rewritten",
                      _stderr(self.capture, "--runs", "2"))

    def test_a_capture_destination_inside_the_manifest_refuses(self):
        self.assertIn("moves the manifest",
                      self.refusal(batch.capture_golden,
                                   os.path.join(self.captures, "attempt-1"),
                                   os.path.join(self.study, "gold", "GOLD.json"),
                                   2, self.pins_path))

    def test_a_capture_slot_that_answered_an_arms_prompt_is_refused(self):
        """A name is not evidence of which prompt was answered, and a golden
        derived from an arm's own runs would pin a context the operator had
        already seen coverage profiles from."""
        self.capture("--runs", "2")
        attempt = os.path.join(self.captures, "attempt-1")
        call_path = os.path.join(attempt, "capture-001", "CALL.json")
        call = json.load(open(call_path))
        call["promptKind"] = "registered"
        with open(call_path, "w") as handle:
            json.dump(call, handle)
        out = os.path.join(self.root, "third.json")
        self.assertIn("derived only from calls that answered the registered "
                      "PROBE prompt",
                      self.refusal(batch.capture_golden, attempt, out, 2,
                                   self.pins_path))

    # -- G2 ---------------------------------------------------------------

    def negative(self, *extra):
        return batch.main(["batch.py", "capture-isolation-negative",
                           "--scratch-parent", self.scratch,
                           "--pins", self.pins_path, "--cli-override", self.cli,
                           "--out", os.path.join(self.root, "negative"),
                           "--golden", self.golden] + list(extra))

    def test_the_control_refuses_without_recorded_assent(self):
        """It runs only under recorded operator assent, at the member name the
        REGISTRY uses — Study 012's round 3 found the driver reading another."""
        self.write_golden()
        message = _stderr(self.negative)
        self.assertIn("records isolationNegative.assent None", message)
        self.assertIn("runs only with recorded assent", message)
        self.assertFalse(os.path.exists(os.path.join(self.root, "negative")))

    def test_the_control_refuses_before_the_golden_is_registered(self):
        pins = json.loads(json.dumps(self.pins))
        pins["isolationNegative"]["assent"] = "granted"
        self.write_pins(pins)
        self.assertIn("no golden context at", _stderr(self.negative))

    def test_the_control_runs_under_assent_and_retains_no_transcript(self):
        self.capture("--runs", "2")
        shutil.copyfile(self.out, self.golden)
        pins = json.loads(json.dumps(self.pins))
        pins["golden"]["sha256"] = _digest(self.golden)
        pins["isolationNegative"]["assent"] = "granted"
        self.write_pins(pins)
        status = self.negative()
        out = os.path.join(self.root, "negative")
        verdict = json.load(open(os.path.join(out, "VERDICT.json")))
        self.assertIn(verdict["outcome"], batch.C7_OUTCOMES)
        self.assertEqual(verdict["assent"], "granted")
        self.assertEqual(verdict["registeredOutcomes"], list(batch.C7_OUTCOMES))
        self.assertEqual(verdict["goldenSha256"], _digest(self.golden))
        self.assertEqual(batch.c7_record_shape_problems(verdict), [])
        self.assertEqual(status, 0 if verdict["outcome"] != "no-context" else 1)
        # the transcript is digested and DELETED, and the retained call record
        # names no member of the operator's environment
        self.assertNotIn("session.jsonl", os.listdir(out))
        call = json.load(open(os.path.join(out, "CALL.json")))
        for member in batch.C7_REDACTED:
            self.assertNotIn(member, call)
        self.assertEqual(call["redacted"], sorted(
            member for member in batch.C7_REDACTED
            if member in ("environment", "environmentValues", "home",
                          "codexHome", "cwd", "isolatedHomeInventory",
                          "operatorHomeSkillsPresent")))
        self.assertFalse(any(name.startswith("s019-c7-raw-")
                             for name in os.listdir(self.scratch)))

    def test_the_control_is_never_rewritten(self):
        self.write_golden()
        pins = json.loads(json.dumps(self.pins))
        pins["isolationNegative"]["assent"] = "granted"
        self.write_pins(pins)
        os.makedirs(os.path.join(self.root, "negative"))
        self.assertIn("a registered control is never rewritten",
                      _stderr(self.negative))


def _stderr(callable_, *args, **kwargs) -> str:
    """Run a command that refuses through `main()` and return what it printed on
    stderr, asserting the exit status is the registered 1."""
    import contextlib
    import io
    buffer = io.StringIO()
    with contextlib.redirect_stderr(buffer):
        status = callable_(*args, **kwargs)
    assert status == 1, "expected the registered refusal status 1, got %r" % status
    return buffer.getvalue()


if __name__ == "__main__":
    unittest.main()
