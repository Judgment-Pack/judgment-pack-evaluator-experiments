#!/usr/bin/env python3
"""The batch driver: N sequential runs of the one registered authoring call,
plus the pre-batch golden recapture that admission depends on.

Each run is an independent invocation of `transcription/authoring_call.sh` with
its own scratch directory, its own fresh HOME, its own fresh CODEX_HOME, and
its own slot under the authoring tree. Runs are sequential, never parallel
(PREREGISTRATION.md §2.4: parallel calls would share provider-side backpressure
and correlate in ways nothing here could measure), and share no state. The
pinned binary digest, model, and prompt digest come from a registry file
(`harness/PINS.json` by default), not from anything this driver computes.

**The registered difference from Study 010** (§7): a run that fails or is
refused terminates its own slot with a REFUSAL.json and the batch CONTINUES.
Study 010 had one slot and a zero-retry rule because a retained transcript from
a killed call would let an operator read the answer and try again for a single
unrepeatable draw. Study 011 makes no draw: every invocation leaves its own
slot, no slot is ever written twice, and the authoring-failure rate is one of
the endpoints — so stopping at the first failure would destroy data the study
exists to collect. What that does NOT license is re-running a slot: the wrapper
refuses an existing slot, and the driver refuses a batch whose target slots are
already on disk or whose results have already been published.

Commands:

  run             N sequential authoring calls into run-001…run-NNN
  capture         the §3.2 golden recapture: two probe calls, whose pre-prompt
                  contexts must agree, into GOLDEN-CONTEXT.json
  capture-golden  derive a golden capture from already-retained capture slots
  shortfall       declare a short batch before anything is scored (§2.4)

What this file deliberately does NOT do: score anything, judge a completion,
decide admissibility (score_rates.py recomputes all of that from the retained
bytes and never trusts a REFUSAL.json), retry a run, choose N after seeing
results, or delete a slot.

Wrapper exit status → refusal code:

  0   the run completed and the slot is admissible-shaped (scoring decides)
  1   preflight-refused    nothing was called
  10  call-nonzero-exit    the process exited non-zero; slot retained
  11  session-count        the isolated home held other than one session
  *   wrapper-error        any other status, retained with the stderr tail

Usage:
  batch.py run --scratch-parent DIR [--slots DIR] [--runs N] [--start K]
               [--pins PATH] [--cli-override PATH] [--dry-run]
  batch.py capture --scratch-parent DIR [--captures DIR] [--out PATH]
               [--runs N] [--pins PATH] [--cli-override PATH]
  batch.py capture-golden --slots DIR --out PATH [--min-slots N]
  batch.py shortfall --slots DIR --reason TEXT [--pins PATH]
"""
from __future__ import annotations
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import score_rates  # noqa: E402  (one slot-naming rule and one JSON loader, not two)
import transcript_check  # noqa: E402

SCRIPT = os.path.join(STUDY, "transcription", "authoring_call.sh")
DEFAULT_PINS = os.path.join(HERE, "PINS.json")
DEFAULT_SLOTS = os.path.join(STUDY, "transcription", "authoring")
DEFAULT_CAPTURES = os.path.join(STUDY, "controls", "recapture")
DEFAULT_GOLDEN = os.path.join(STUDY, "transcription", "GOLDEN-CONTEXT.json")
RESULTS = os.path.join(STUDY, "RESULTS.json")

WRAPPER_CODES = {0: None, 1: "preflight-refused", 10: "call-nonzero-exit",
                 11: "session-count"}
STDERR_TAIL = 4000


class BatchError(Exception):
    """A refusal that stops the batch before any call is made."""


def _load_json(path: str):
    with open(path, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"),
                          object_pairs_hook=score_rates._refuse_duplicate_keys)


def _digest(path: str) -> str:
    with open(path, "rb") as handle:
        return "sha256:" + hashlib.sha256(handle.read()).hexdigest()


def _write_json(path: str, body: dict) -> None:
    with open(path, "wb") as handle:
        handle.write((json.dumps(body, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def plan(runs: int, start: int, slots_dir: str, stem: str = "run") -> list:
    """The slot paths this batch will create, in order. Named run-NNN with a
    three-digit index: the run order IS the on-disk order, so a drift read is
    a sort, not a join."""
    return [os.path.join(slots_dir, "%s-%03d" % (stem, index))
            for index in range(start, start + runs)]


def preflight(runs: int, start: int, slots: list, scratch_parent: str,
              pins_path: str, cli_override: str, prompt_kind: str) -> dict:
    """The pins, or BatchError. Everything checkable before the first call is
    checked before the first call: a batch that would collide with retained
    slots, publish after results exist, or run a prompt that is not the pinned
    one must not spend a single invocation."""
    if runs < 1:
        raise BatchError("a batch needs at least one run")
    if not os.path.isfile(SCRIPT):
        raise BatchError("no authoring wrapper at %s" % SCRIPT)
    if not os.path.isdir(scratch_parent):
        raise BatchError("scratch parent %s is not a directory" % scratch_parent)
    pins = _load_json(pins_path)
    member = "prompt" if prompt_kind == "registered" else "probePrompt"
    prompt = os.path.join(STUDY, pins[member]["path"])
    actual = _digest(prompt)
    if actual != pins[member]["sha256"]:
        raise BatchError("%s is %s, not the pinned %s"
                         % (pins[member]["path"], actual, pins[member]["sha256"]))
    if cli_override is not None:
        if not os.path.isfile(cli_override):
            raise BatchError("no CLI at %s" % cli_override)
        override_digest = _digest(cli_override)
        if override_digest != pins["codex"]["binarySha256"]:
            raise BatchError("the CLI at %s is %s, not the pinned %s"
                             % (cli_override, override_digest, pins["codex"]["binarySha256"]))
    if prompt_kind == "registered" and os.path.exists(RESULTS):
        # §2.4: no slot after a rate has been computed. Adding runs once the
        # numbers are visible is the one thing a rate study must never do.
        raise BatchError("%s exists: no slot may be created after a rate has been "
                         "computed" % RESULTS)
    existing = [os.path.basename(slot) for slot in slots if os.path.exists(slot)]
    if existing:
        raise BatchError("these slots already exist and are never rewritten: %s"
                         % ", ".join(existing))
    return pins


def invoke(slot: str, scratch_parent: str, pins_path: str, cli_override: str,
           prompt_kind: str) -> tuple:
    """(wrapper exit status, refusal code or None, stderr) for one call."""
    argv = ["bash", SCRIPT, scratch_parent, slot, pins_path]
    if cli_override is not None:
        argv.append(cli_override)
    environment = dict(os.environ)
    environment["PYTHON_BIN"] = sys.executable
    environment["PROMPT_KIND"] = prompt_kind
    completed = subprocess.run(argv, env=environment, capture_output=True, text=True)
    return (completed.returncode, WRAPPER_CODES.get(completed.returncode, "wrapper-error"),
            completed.stderr)


def refuse_slot(slot: str, code: str, status: int, stderr: str) -> None:
    """Terminate one slot with its refusal record. A pre-flight refusal may
    leave no slot at all; the record still gets one, so every attempted run is
    on disk and the population has no invisible members."""
    os.makedirs(slot, exist_ok=True)
    _write_json(os.path.join(slot, "REFUSAL.json"), {
        "run": os.path.basename(slot),
        "code": code,
        "wrapperExit": status,
        "wrapperStderrTail": stderr[-STDERR_TAIL:],
        "note": "Recorded by batch.py. score_rates.py recomputes admission from the "
                "retained bytes and does not trust this record.",
    })


def run_batch(runs: int, start: int, slots_dir: str, scratch_parent: str,
              pins_path: str, cli_override: str, dry_run: bool) -> int:
    slots = plan(runs, start, slots_dir)
    pins = preflight(runs, start, slots, scratch_parent, pins_path, cli_override,
                     "registered")
    if dry_run:
        print("dry run: %d slots, none created" % len(slots))
        print("  model      %s" % pins["codex"]["model"])
        print("  binary     %s" % pins["codex"]["binarySha256"])
        print("  prompt     %s" % pins["prompt"]["sha256"])
        print("  wrapper    %s" % SCRIPT)
        print("  cli        %s" % (cli_override or "codex on PATH"))
        for slot in slots:
            print("  would create %s" % slot)
        return 0
    os.makedirs(slots_dir, exist_ok=True)
    rows = []
    for slot in slots:
        status, code, stderr = invoke(slot, scratch_parent, pins_path, cli_override,
                                      "registered")
        rows.append({"slot": os.path.basename(slot), "wrapperExit": status, "code": code})
        if code is not None:
            refuse_slot(slot, code, status, stderr)
        print("%s: exit %d%s" % (os.path.basename(slot), status,
                                 "" if code is None else " (%s)" % code))
        _write_json(os.path.join(slots_dir, "BATCH.json"), {
            "batchVersion": "1",
            "registeredRuns": pins.get("batch", {}).get("runs"),
            "requestedRuns": runs,
            "startIndex": start,
            "model": pins["codex"]["model"],
            "binarySha256": pins["codex"]["binarySha256"],
            "promptSha256": pins["prompt"]["sha256"],
            "cliOverride": cli_override,
            "runs": rows,
            "note": "Written after every run, so an interrupted batch still says what "
                    "it attempted. No clock is recorded here; each slot's CALL.json "
                    "carries its own start and end.",
        })
    refused = [row for row in rows if row["code"] is not None]
    print("batch: %d runs, %d refused" % (len(rows), len(refused)))
    return 0


def capture_slots(directory: str) -> list:
    """Every retained slot beneath a directory that has a session and a call
    record, in name order. Used by the recapture: capture slots are not batch
    slots, are not named run-NNN, and never enter any denominator."""
    if not os.path.isdir(directory):
        raise BatchError("%s is not a directory" % directory)
    found = []
    for name in sorted(os.listdir(directory)):
        path = os.path.join(directory, name)
        if os.path.isdir(path) and not os.path.islink(path) \
                and os.path.isfile(os.path.join(path, "session.jsonl")) \
                and os.path.isfile(os.path.join(path, "CALL.json")):
            found.append(path)
    return found


def capture_golden(slots_dir: str, out_path: str, min_slots: int) -> int:
    """Derive this study's golden pre-prompt context from retained capture
    slots (PREREGISTRATION.md §3.2).

    Study 010 locked a capture taken from two independent real runs that
    reproduced identically; this repeats that procedure in this environment,
    because a golden capture pins one machine's codex boilerplate and 010's
    would refuse every honest run here. The captures must AGREE — a context
    that varies run to run cannot be an allowlist — and none of them may carry
    a leak token before the prompt, or the capture would bless a planted turn.
    """
    if os.path.exists(out_path):
        raise BatchError("%s already exists; a registered capture is never rewritten"
                         % out_path)
    usable, contexts = [], []
    for slot in capture_slots(slots_dir):
        session = os.path.join(slot, "session.jsonl")
        call = _load_json(os.path.join(slot, "CALL.json"))
        events, turn_contexts = transcript_check._events(session)
        positions = [index for index, (role, _) in enumerate(events) if role == "user"]
        position = positions[-1] if positions else len(events)
        transcript_check.screen_prior_context(
            events, position, transcript_check.environment_paths(turn_contexts, call))
        usable.append(os.path.basename(slot))
        contexts.append(transcript_check.context_digests(session, call))
    if len(usable) < min_slots:
        raise BatchError("a capture needs at least %d capture slots with a session; found %d"
                         % (min_slots, len(usable)))
    first = contexts[0]
    for name, context in zip(usable[1:], contexts[1:]):
        if context != first:
            raise BatchError("capture %s does not reproduce %s's pre-prompt context; "
                             "a varying context cannot be an allowlist" % (name, usable[0]))
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    _write_json(out_path, {
        "contextVersion": first["contextVersion"],
        "entries": first["entries"],
        "capturedFrom": usable,
        "note": "The pre-prompt context of this study's registered invocation, captured "
                "from independent probe-prompt runs that reproduced identically after "
                "normalization. Any deviation in a batch run's context refuses that run "
                "(score_rates.py, code transcript-refused).",
    })
    print("captured: %d entries from %d agreeing captures" % (len(first["entries"]), len(usable)))
    return 0


def run_capture(runs: int, captures_dir: str, out_path: str, scratch_parent: str,
                pins_path: str, cli_override: str) -> int:
    """The §3.2 recapture, end to end: N probe calls, then the derivation.

    The probe prompt — not the registered one — is deliberate. The pre-prompt
    context precedes the prompt and does not depend on it, and running the
    registered prompt here would show the operator coverage profiles before the
    batch, which is exactly the cost Study 010's DEVIATIONS §1 records.
    """
    slots = plan(runs, 1, captures_dir, stem="capture")
    preflight(runs, 1, slots, scratch_parent, pins_path, cli_override, "probe")
    os.makedirs(captures_dir, exist_ok=True)
    for slot in slots:
        status, code, stderr = invoke(slot, scratch_parent, pins_path, cli_override, "probe")
        if code is not None:
            refuse_slot(slot, code, status, stderr)
            raise BatchError("capture %s failed (%s); the batch does not start until two "
                             "captures agree" % (os.path.basename(slot), code))
        print("%s: exit %d" % (os.path.basename(slot), status))
    return capture_golden(captures_dir, out_path, runs)


def declare_shortfall(slots_dir: str, reason: str, pins_path: str) -> int:
    """§2.4: a batch that cannot finish declares the shortfall BEFORE anything
    is scored. The scorer refuses an incomplete batch without this file, so the
    declaration cannot be written after the rates are seen."""
    if os.path.exists(RESULTS):
        raise BatchError("%s exists: a shortfall may not be declared after a rate has "
                         "been computed" % RESULTS)
    out_path = os.path.join(slots_dir, "SHORTFALL.json")
    if os.path.exists(out_path):
        raise BatchError("%s already exists" % out_path)
    if not reason:
        raise BatchError("--reason is required: a shortfall without a reason is a gap")
    pins = _load_json(pins_path)
    slots, _ = score_rates.collect_slots(slots_dir)
    _write_json(out_path, {
        "registeredRuns": pins.get("batch", {}).get("runs"),
        "completedSlots": len(slots),
        "reason": reason,
        "note": "Declared before scoring. The headline reports 'S of N slots completed' "
                "and rates are computed over the valid runs among the S.",
    })
    print("shortfall declared: %d slots completed" % len(slots))
    return 0


def _argument(argv: list, flag: str, default=None):
    if flag not in argv:
        return default
    index = argv.index(flag)
    if index + 1 >= len(argv):
        raise BatchError("%s needs a value" % flag)
    return argv[index + 1]


USAGE = (
    "usage: batch.py run --scratch-parent DIR [--slots DIR] [--runs N] [--start K]\n"
    "                    [--pins PATH] [--cli-override PATH] [--dry-run]\n"
    "       batch.py capture --scratch-parent DIR [--captures DIR] [--out PATH]\n"
    "                    [--runs N] [--pins PATH] [--cli-override PATH]\n"
    "       batch.py capture-golden --slots DIR --out PATH [--min-slots N]\n"
    "       batch.py shortfall --slots DIR --reason TEXT [--pins PATH]")


def main(argv: list) -> int:
    if len(argv) < 2 or argv[1] not in ("run", "capture", "capture-golden", "shortfall"):
        print(USAGE, file=sys.stderr)
        return 2
    command = argv[1]
    try:
        pins_path = _argument(argv, "--pins", DEFAULT_PINS)
        if command == "run":
            runs = _argument(argv, "--runs")
            if runs is None:
                runs = _load_json(pins_path).get("batch", {}).get("runs")
                if runs is None:
                    raise BatchError("--runs is required when the pins name no batch size")
            scratch_parent = _argument(argv, "--scratch-parent")
            if scratch_parent is None:
                raise BatchError("--scratch-parent is required")
            return run_batch(int(runs), int(_argument(argv, "--start", 1)),
                             _argument(argv, "--slots", DEFAULT_SLOTS),
                             scratch_parent, pins_path,
                             _argument(argv, "--cli-override"),
                             "--dry-run" in argv)
        if command == "capture":
            scratch_parent = _argument(argv, "--scratch-parent")
            if scratch_parent is None:
                raise BatchError("--scratch-parent is required")
            return run_capture(int(_argument(argv, "--runs", 2)),
                               _argument(argv, "--captures", DEFAULT_CAPTURES),
                               _argument(argv, "--out", DEFAULT_GOLDEN),
                               scratch_parent, pins_path,
                               _argument(argv, "--cli-override"))
        slots_dir = _argument(argv, "--slots")
        if slots_dir is None:
            raise BatchError("--slots is required")
        if command == "capture-golden":
            return capture_golden(slots_dir, _argument(argv, "--out", DEFAULT_GOLDEN),
                                  int(_argument(argv, "--min-slots", 2)))
        return declare_shortfall(slots_dir, _argument(argv, "--reason"), pins_path)
    except (BatchError, score_rates.ScoreError, transcript_check.TranscriptError) as error:
        print("refused: %s" % error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
