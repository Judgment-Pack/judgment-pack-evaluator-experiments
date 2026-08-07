#!/usr/bin/env python3
"""The batch driver: N sequential runs of the one registered authoring call,
the pre-batch golden recapture that admission depends on, and the §6 C7
isolation negative control.

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

Preflight refuses, before a single call is spent, when: the ported bytes are
not the registered ones and the interpreter is not the registered one
(harness/integrity.py, §6 C1, §2.6); the preregistration's freeze digest is
unregistered or does not match this file (§2.6); the prompt is not the pinned
prompt; a named CLI is not the pinned binary; `RESULTS.json` exists; a planned
slot exists; or — for the registered prompt — the golden capture is absent or
its digest is not the one `harness/PINS.json` registers (§3.2). The last one is
why the golden recapture cannot be skipped: no slot is created until the
capture is taken, registered and committed. That digest is then stamped into
every slot's `CALL.json`, so a capture substituted after the batch does not
change which runs were admissible — the scorer scores those slots
`golden-mismatch` instead (§3.3).

Commands:

  run                        N sequential authoring calls into run-001…run-NNN
  capture                    the §3.2 golden recapture: two probe calls into a
                             numbered attempt directory, whose pre-prompt
                             contexts must agree, then the golden derivation
  capture-golden             derive a golden capture from retained capture
                             slots (the second half of `capture`, for the case
                             where the calls were made and the derivation was
                             not). At least two agreeing captures, always:
                             --min-slots cannot ask for fewer, and the captures
                             must come from distinct sessions — a copied slot
                             or a transcript retained twice agrees with itself
                             and refuses
  capture-isolation-negative §6 C7: ONE probe call with the operator's real
                             HOME, expected to FAIL the golden match. Retains
                             the verdict and a stripped call record always, and
                             the context digests when the call produced them;
                             never the transcript, whose deletion it verifies.
                             Exits non-zero if it reached neither comparison.
  shortfall                  declare a short batch before anything is scored

What this file deliberately does NOT do: score anything, judge a completion,
decide admissibility (score_rates.py recomputes all of that from the retained
bytes and never trusts a REFUSAL.json), retry a run, choose N after seeing
results, or delete a slot.

Wrapper exit status → refusal code:

  0   the run completed and the slot is admissible-shaped (scoring decides)
  1   preflight-refused    nothing was called
  10  call-nonzero-exit    the process exited non-zero; slot retained
  11  session-count        the call produced other than one new session
  *   wrapper-error        any other status, retained with the stderr tail

Usage:
  batch.py run --scratch-parent DIR [--slots DIR] [--runs N] [--start K]
               [--pins PATH] [--golden PATH] [--cli-override PATH] [--dry-run]
  batch.py capture --scratch-parent DIR [--captures DIR] [--out PATH]
               [--runs N] [--pins PATH] [--cli-override PATH]
  batch.py capture-golden --slots DIR --out PATH [--min-slots N]
  batch.py capture-isolation-negative --scratch-parent DIR [--out DIR]
               [--pins PATH] [--golden PATH] [--cli-override PATH]
  batch.py shortfall --slots DIR --reason TEXT [--pins PATH]
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import integrity  # noqa: E402
import score_rates  # noqa: E402  (one slot-naming rule and one JSON loader, not two)
import transcript_check  # noqa: E402

SCRIPT = os.path.join(STUDY, "transcription", "authoring_call.sh")
DEFAULT_PINS = os.path.join(HERE, "PINS.json")
DEFAULT_SLOTS = os.path.join(STUDY, "transcription", "authoring")
DEFAULT_CAPTURES = os.path.join(STUDY, "controls", "recapture")
DEFAULT_NEGATIVE = os.path.join(STUDY, "controls", "isolation-negative")
DEFAULT_GOLDEN = os.path.join(STUDY, "transcription", "GOLDEN-CONTEXT.json")
RESULTS = os.path.join(STUDY, "RESULTS.json")

WRAPPER_CODES = {0: None, 1: "preflight-refused", 10: "call-nonzero-exit",
                 11: "session-count"}
STDERR_TAIL = 4000
# §3.2: a golden capture is derived from at least TWO independent captures whose
# normalized pre-prompt contexts agree. One capture cannot show that a context
# reproduces, and an allowlist built from a context that might vary is not an
# allowlist. This is the floor, not a default: a smaller --min-slots refuses.
MIN_CAPTURE_SLOTS = 2
# …and the two must be two CALLS. The rule's meaning is that two independent
# probe invocations reproduced the same context; a copied slot, or one call's
# transcript retained twice, satisfies "two agreeing captures" and shows
# nothing at all. Each member below is a piece of RAW retained evidence that
# says WHICH call produced a capture, and two capture slots that share any of
# them are one call — the normalized digests are deliberately not among them,
# because two genuinely independent calls SHOULD agree there and that agreement
# is the point of the derivation, not a defect in it.
CAPTURE_IDENTITY = (
    ("sessionSha256", "the retained transcript bytes"),
    ("sessionId", "the session id the transcript records"),
    ("callIdentity", "the call record's own start, end, working directory and "
                     "isolated home"),
)
# §6 C7: what a retained negative-control CALL.json may not carry. The control
# runs against the operator's real environment, so every member that names or
# enumerates it is dropped before the file is written into the study.
C7_REDACTED = ("environment", "environmentValues", "home", "codexHome", "cwd",
               "isolatedHomeInventory", "operatorHomeSkillsPresent")


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


def verify_ported_bytes() -> dict:
    """§6 C1 as a precondition of the batch, not only of CI. A drifted mirror
    or compiler changes every count; the digest table is checked before a call
    is spent, because afterwards it is too late for the batch."""
    try:
        return integrity.verify()
    except integrity.IntegrityError as error:
        raise BatchError("the ported bytes are not the registered ones: %s" % error)


def preflight(runs: int, start: int, slots: list, scratch_parent: str,
              pins_path: str, cli_override: str, prompt_kind: str,
              golden_path: str = None) -> dict:
    """The pins, or BatchError. Everything checkable before the first call is
    checked before the first call: a batch that would run drifted bytes,
    collide with retained slots, publish after results exist, run a prompt that
    is not the pinned one, or run without the registered golden capture must
    not spend a single invocation."""
    verify_ported_bytes()
    if runs < 1:
        raise BatchError("a batch needs at least one run")
    if not os.path.isfile(SCRIPT):
        raise BatchError("no authoring wrapper at %s" % SCRIPT)
    if not os.path.isdir(scratch_parent):
        raise BatchError("scratch parent %s is not a directory" % scratch_parent)
    pins = _load_json(pins_path)
    require_freeze(pins)
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
    if prompt_kind == "registered":
        if os.path.exists(RESULTS):
            # §2.4: no slot after a rate has been computed. Adding runs once the
            # numbers are visible is the one thing a rate study must never do.
            raise BatchError("%s exists: no slot may be created after a rate has been "
                             "computed" % RESULTS)
        require_golden(pins, golden_path)
    # `lexists`, not `exists`: a DANGLING symlink at a planned slot path is
    # absent to `exists()` and present to `mkdir`, so the batch used to pass
    # preflight and then die of an uncaught FileExistsError in refuse_slot() —
    # no call spent, no refusal recorded, and BATCH.json left behind. A link
    # at a planned slot path is a slot that already exists, whatever it points
    # at, and it refuses here through the registered path.
    existing = [os.path.basename(slot) for slot in slots if os.path.lexists(slot)]
    if existing:
        raise BatchError("these slots already exist and are never rewritten: %s"
                         % ", ".join(existing))
    return pins


def require_freeze(pins: dict) -> str:
    """§2.6: the preregistration's freeze digest, before anything is called.

    The freeze precedes the recapture, which precedes the batch, so the pin is
    already fillable at every point this runs. Registering it as a precondition
    of the CALLS as well as of the scoring is what makes it more than an
    intention: a registry merged with its null intact spends no quota."""
    entry = pins.get("preregistration") or {}
    pinned = entry.get("sha256")
    if not pinned:
        raise BatchError(
            "harness/PINS.json registers no preregistration.sha256: the frozen "
            "PREREGISTRATION.md's digest replaces the null at the freeze, before any "
            "call is made, so that a post-freeze edit is detectable (§2.6)")
    path = os.path.join(STUDY, entry.get("path", "PREREGISTRATION.md"))
    if not os.path.isfile(path):
        raise BatchError("the preregistration is missing from %s" % STUDY)
    actual = _digest(path)
    if actual != pinned:
        raise BatchError("PREREGISTRATION.md is %s, not the %s registered at the "
                         "freeze: it was edited after the freeze" % (actual, pinned))
    return actual


def golden_path_for(pins: dict, override: str = None) -> str:
    return override or os.path.join(STUDY, pins.get("golden", {}).get(
        "path", "transcription/GOLDEN-CONTEXT.json"))


def require_golden(pins: dict, golden_path: str = None) -> str:
    """§3.2 step 3, as much of it as a driver can check: the capture is on disk
    and the registry's `golden.sha256` is non-null and equal to its digest,
    before any slot is created. A skipped recapture therefore costs nothing
    instead of costing fifty calls, and the digest verified here is stamped
    into every slot's CALL.json so the binding is per run and not per batch.

    What this does NOT check, stated here so no caller can read more into it:
    that either file was COMMITTED. Nothing in this study compares a worktree
    file to a HEAD blob (§7, "deliberately not claimed"); committing the
    capture and the registry before slot 1 is ledger discipline the study
    records, not an ordering the driver enforces."""
    path = golden_path_for(pins, golden_path)
    pinned = pins.get("golden", {}).get("sha256")
    if not os.path.isfile(path):
        raise BatchError(
            "no golden context at %s: run the §3.2 recapture (batch.py capture "
            "--scratch-parent DIR) and commit it before the first slot" % path)
    if not pinned:
        raise BatchError(
            "harness/PINS.json registers no golden.sha256: the capture's digest must "
            "replace the null and be committed before the first slot (§3.2 step 3)")
    actual = _digest(path)
    if actual != pinned:
        raise BatchError("the golden capture at %s is %s, not the registered %s"
                         % (path, actual, pinned))
    return path


def invoke(slot: str, scratch_parent: str, pins_path: str, cli_override: str,
           prompt_kind: str, isolation: str = "isolated",
           golden_sha256: str = None) -> tuple:
    """(wrapper exit status, refusal code or None, stderr) for one call.

    `golden_sha256` is the digest `require_golden()` verified at preflight; the
    wrapper stamps it into the slot's CALL.json, so the scorer can check the
    golden-before-slots ordering per slot instead of taking it on trust (§3.2).
    The probe calls — the recapture and §6 C7 — precede the golden and pass
    none.
    """
    argv = ["bash", SCRIPT, scratch_parent, slot, pins_path]
    if cli_override is not None:
        argv.append(cli_override)
    environment = dict(os.environ)
    environment["PYTHON_BIN"] = sys.executable
    environment["PROMPT_KIND"] = prompt_kind
    environment["ISOLATION"] = isolation
    environment["GOLDEN_SHA256"] = golden_sha256 or ""
    completed = subprocess.run(argv, env=environment, capture_output=True, text=True)
    return (completed.returncode, WRAPPER_CODES.get(completed.returncode, "wrapper-error"),
            completed.stderr)


def refuse_slot(slot: str, code: str, status: int, stderr: str) -> None:
    """Terminate one slot with its refusal record. A pre-flight refusal may
    leave no slot at all; the record still gets one, so every attempted run is
    on disk and the population has no invisible members.

    `exist_ok=True` covers the ordinary case of a slot the wrapper created. It
    does not cover a path that exists and is not a directory — a link, a file,
    a FIFO — where `makedirs` raises `FileExistsError` and the batch would end
    in a bare traceback. Preflight already refuses those, so reaching this is a
    bug; it refuses as a BatchError rather than as a traceback so that the
    driver's failure is one of its own registered refusals either way."""
    if os.path.lexists(slot) and not os.path.isdir(slot):
        raise BatchError(
            "%s exists and is not a directory, so no refusal record can be written "
            "into it: remove it by hand and record the cause in DEVIATIONS.md" % slot)
    os.makedirs(slot, exist_ok=True)
    _write_json(os.path.join(slot, "REFUSAL.json"), {
        "run": os.path.basename(slot),
        "code": code,
        "wrapperExit": status,
        "wrapperStderrTail": stderr[-STDERR_TAIL:],
        "note": "Recorded by batch.py. score_rates.py recomputes admission from the "
                "retained bytes and does not trust this record.",
    })


def load_ledger(slots_dir: str) -> list:
    """The per-slot records BATCH.json already holds. A resumed batch MERGES
    into these rather than replacing them: §2.5 registers the wrapper's exit
    status as retained per slot, and a slot that exited 0 carries it nowhere
    else, so overwriting the ledger would delete the only record of runs the
    resume did not make."""
    path = os.path.join(slots_dir, "BATCH.json")
    if not os.path.isfile(path):
        return []
    ledger = _load_json(path)
    records = ledger.get("records")
    if records is None:
        raise BatchError(
            "%s is a pre-merge ledger (batchVersion %r) and cannot be resumed into: "
            "move it aside and record why in DEVIATIONS.md"
            % (path, ledger.get("batchVersion")))
    if not isinstance(records, list):
        raise BatchError("%s's records member is not a list" % path)
    return records


def write_ledger(slots_dir: str, records: list, pins: dict, cli_override: str,
                 golden_path: str) -> None:
    _write_json(os.path.join(slots_dir, "BATCH.json"), {
        "batchVersion": "2",
        "registeredRuns": pins.get("batch", {}).get("runs"),
        "model": pins["codex"]["model"],
        "binarySha256": pins["codex"]["binarySha256"],
        "promptSha256": pins["prompt"]["sha256"],
        "goldenSha256": pins.get("golden", {}).get("sha256"),
        "cliOverride": cli_override,
        "records": sorted(records, key=lambda row: row["slot"]),
        "note": "One append-only record per slot, written after every run and MERGED "
                "by a resumed invocation (batch.py run --start K), which refuses if "
                "it would overlap a slot already recorded here. No clock is recorded; "
                "each slot's CALL.json carries its own start and end.",
    })


def run_batch(runs: int, start: int, slots_dir: str, scratch_parent: str,
              pins_path: str, cli_override: str, dry_run: bool,
              golden_override: str = None) -> int:
    slots = plan(runs, start, slots_dir)
    pins = preflight(runs, start, slots, scratch_parent, pins_path, cli_override,
                     "registered", golden_override)
    golden = golden_path_for(pins, golden_override)
    if dry_run:
        print("dry run: %d slots, none created" % len(slots))
        print("  model      %s" % pins["codex"]["model"])
        print("  binary     %s" % pins["codex"]["binarySha256"])
        print("  prompt     %s" % pins["prompt"]["sha256"])
        print("  golden     %s" % pins.get("golden", {}).get("sha256"))
        print("  wrapper    %s" % SCRIPT)
        print("  cli        %s" % (cli_override or "codex on PATH"))
        for slot in slots:
            print("  would create %s" % slot)
        return 0
    os.makedirs(slots_dir, exist_ok=True)
    rows = load_ledger(slots_dir)
    recorded = set(row["slot"] for row in rows)
    overlap = sorted(recorded & set(os.path.basename(slot) for slot in slots))
    if overlap:
        raise BatchError("BATCH.json already records %s: a resumed batch merges into "
                         "the ledger, it never re-runs a recorded slot"
                         % ", ".join(overlap))
    # The digest preflight verified, stamped into every slot this invocation
    # makes: a golden swapped after the batch changes the pin, and every slot
    # then names a digest that is not the pin it is being scored under.
    golden_pin = pins.get("golden", {}).get("sha256")
    for slot in slots:
        status, code, stderr = invoke(slot, scratch_parent, pins_path, cli_override,
                                      "registered", golden_sha256=golden_pin)
        rows.append({"slot": os.path.basename(slot), "wrapperExit": status, "code": code,
                     "startIndex": start})
        if code is not None:
            refuse_slot(slot, code, status, stderr)
        print("%s: exit %d%s" % (os.path.basename(slot), status,
                                 "" if code is None else " (%s)" % code))
        write_ledger(slots_dir, rows, pins, cli_override, golden)
    made = [row for row in rows if row["startIndex"] == start]
    refused = [row for row in made if row["code"] is not None]
    print("batch: %d runs this invocation (%d refused), %d slots in the ledger"
          % (len(made), len(refused), len(rows)))
    return 0


def capture_slots(directory: str) -> list:
    """Every retained slot beneath a directory that has a session and a call
    record, in name order. Used by the recapture: capture slots are not batch
    slots, are not named run-NNN, and never enter any denominator — a
    directory named run-<digits> refuses outright, so a golden capture can
    never be derived from the batch's own runs."""
    if not os.path.isdir(directory):
        raise BatchError("%s is not a directory" % directory)
    found = []
    for name in sorted(os.listdir(directory)):
        path = os.path.join(directory, name)
        parts = name.split("-", 1)
        if os.path.isdir(path) and len(parts) == 2 and parts[0] == "run" \
                and parts[1].isdigit():
            raise BatchError(
                "%s holds the batch slot %s: a golden capture is derived from probe "
                "captures taken before the batch, never from the batch's own runs"
                % (directory, name))
        if os.path.isdir(path) and not os.path.islink(path) \
                and os.path.isfile(os.path.join(path, "session.jsonl")) \
                and os.path.isfile(os.path.join(path, "CALL.json")):
            found.append(path)
    return found


def session_identity(session_path: str):
    """The session id the transcript records for itself, or None.

    `session_meta` is metadata the transcript checker skips — no conversation
    content reaches the model through it — but it is exactly the right
    evidence here: it names the session, and two capture slots naming one
    session are one call however their directories are named.
    """
    with open(session_path, "rb") as handle:
        for raw in handle:
            raw = raw.strip()
            if not raw:
                continue
            entry = json.loads(raw.decode("utf-8"),
                               object_pairs_hook=score_rates._refuse_duplicate_keys)
            if not isinstance(entry, dict) or entry.get("type") != "session_meta":
                continue
            payload = entry.get("payload")
            if isinstance(payload, dict):
                for key in ("id", "session_id"):
                    if isinstance(payload.get(key), str) and payload[key]:
                        return payload[key]
    return None


def capture_identity(slot: str) -> dict:
    """The raw retained evidence of WHICH call produced this capture (§3.2).

    Raw, deliberately: the session file's bytes, the session id, and the call
    record's own wall clock, working directory and isolated home. Not the
    normalized context digests — those are what two independent calls are
    SUPPOSED to share.
    """
    call = _load_json(os.path.join(slot, "CALL.json"))
    return {
        "slot": os.path.basename(slot),
        "sessionSha256": _digest(os.path.join(slot, "session.jsonl")),
        "sessionId": session_identity(os.path.join(slot, "session.jsonl")),
        "callIdentity": (call.get("startedAt"), call.get("endedAt"),
                         call.get("cwd"), call.get("home")),
    }


def require_distinct_sessions(identities: list) -> None:
    """Every capture slot is a different call, or BatchError naming the pair.

    The hole this closes: `capture-golden` counted slots and compared
    normalized contexts, so two slots holding one call's evidence — a copied
    directory, or one transcript retained twice — agreed perfectly and derived
    an allowlist from a context that had never been shown to reproduce. The
    floor of two is a floor of two INDEPENDENT calls.
    """
    for index, first in enumerate(identities):
        for second in identities[index + 1:]:
            for member, prose in CAPTURE_IDENTITY:
                if first[member] is None or second[member] is None:
                    continue
                if first[member] != second[member]:
                    continue
                raise BatchError(
                    "capture %s and capture %s share %s (%r): a golden capture is "
                    "derived from at least two INDEPENDENT calls that reproduced "
                    "the same context, and two slots holding one call's evidence "
                    "agree by construction rather than by reproduction (§3.2)"
                    % (first["slot"], second["slot"], prose, first[member]))


def capture_golden(slots_dir: str, out_path: str, min_slots: int,
                   pins_path: str = DEFAULT_PINS) -> int:
    """Derive this study's golden pre-prompt context from retained capture
    slots (PREREGISTRATION.md §3.2).

    Study 010 locked a capture taken from two independent real runs that
    reproduced identically; this repeats that procedure in this environment,
    because a golden capture pins one machine's codex boilerplate and 010's
    would refuse every honest run here. The captures must AGREE — a context
    that varies run to run cannot be an allowlist — and none of them may carry
    a leak token before the prompt, or the capture would bless a planted turn.

    The two-capture rule is enforced HERE, where the derivation happens, and
    not only in the command that makes the calls: `MIN_CAPTURE_SLOTS` is a
    floor, so `--min-slots 1` refuses rather than deriving an allowlist from a
    single unreproduced context — and the two must be two independent CALLS,
    which `require_distinct_sessions()` checks on the raw retained evidence
    rather than on the normalized digests two honest calls are supposed to
    share.

    It runs the same preflight the command that makes the calls runs — the
    ported bytes, the registered interpreter, and the preregistration's freeze
    digest — because this half derives the artifact every later admission is
    checked against. Without it a golden capture could be derived under an
    unregistered interpreter from an unfrozen study, which is exactly what the
    round-3 review demonstrated on CPython 3.8. And it requires every capture
    slot to be a PROBE call at the pinned probe-prompt digest: `capture_slots()`
    refuses batch-shaped names, but a name is not evidence of which prompt was
    answered, and a golden derived from registered-prompt runs would pin a
    context the operator had already seen coverage profiles from (§3.2 step 2).
    """
    if not out_path:
        raise BatchError("--out is required: a golden capture is written where the "
                         "operator names it, never into the study tree by default")
    if os.path.exists(out_path):
        raise BatchError("%s already exists; a registered capture is never rewritten"
                         % out_path)
    if min_slots < MIN_CAPTURE_SLOTS:
        raise BatchError(
            "a golden capture is derived from at least %d agreeing captures and "
            "--min-slots %d asks for fewer: one capture cannot show that a "
            "pre-prompt context reproduces, and a context that might vary is not "
            "an allowlist (§3.2)" % (MIN_CAPTURE_SLOTS, min_slots))
    verify_ported_bytes()
    pins = _load_json(pins_path)
    require_freeze(pins)
    probe_pin = pins.get("probePrompt", {}).get("sha256")
    if not probe_pin:
        raise BatchError("%s pins no probePrompt.sha256: a capture is derived only "
                         "from runs of the registered probe prompt (§3.2)" % pins_path)
    usable, contexts, identities = [], [], []
    for slot in capture_slots(slots_dir):
        session = os.path.join(slot, "session.jsonl")
        call = _load_json(os.path.join(slot, "CALL.json"))
        if call.get("promptKind") != "probe" or call.get("promptSha256") != probe_pin:
            raise BatchError(
                "capture %s records promptKind %r and prompt %r: a golden capture is "
                "derived only from calls that answered the registered PROBE prompt "
                "(%s). Running the registered prompt before the batch would show the "
                "operator coverage profiles first, which is the cost Study 010's "
                "DEVIATIONS §1 records (§3.2 step 2)"
                % (os.path.basename(slot), call.get("promptKind"),
                   call.get("promptSha256"), probe_pin))
        events, turn_contexts = transcript_check._events(session)
        positions = [index for index, (role, _) in enumerate(events) if role == "user"]
        position = positions[-1] if positions else len(events)
        transcript_check.screen_prior_context(
            events, position, transcript_check.environment_paths(turn_contexts, call))
        usable.append(os.path.basename(slot))
        contexts.append(transcript_check.context_digests(session, call))
        identities.append(capture_identity(slot))
    required = max(min_slots, MIN_CAPTURE_SLOTS)
    if len(usable) < required:
        raise BatchError("a capture needs at least %d capture slots with a session; found %d"
                         % (required, len(usable)))
    # …and they are that many CALLS: agreement between two copies of one
    # transcript is not reproduction (§3.2). Checked before the contexts are
    # compared, because a duplicate agrees by construction and the comparison
    # below would report success.
    require_distinct_sessions(identities)
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
        "capturedIn": os.path.basename(os.path.abspath(slots_dir)),
        "note": "The pre-prompt context of this study's registered invocation, captured "
                "from independent probe-prompt runs that reproduced identically after "
                "normalization. Any deviation in a batch run's context refuses that run "
                "(score_rates.py, code transcript-refused). Its digest goes into "
                "harness/PINS.json golden.sha256 and both are committed before slot 1.",
    })
    print("captured: %d entries from %d agreeing captures" % (len(first["entries"]), len(usable)))
    print("next: put %s into harness/PINS.json golden.sha256 and commit both before "
          "the first slot" % _digest(out_path))
    return 0


def next_attempt(captures_dir: str) -> str:
    """`controls/recapture/attempt-N/`, the next unused N.

    §3.2 step 3 registers that a disagreeing recapture may be repeated after
    the environmental cause is fixed. A repeat needs somewhere to go: slots are
    never rewritten, so attempt 2 is its own directory and every attempt stays
    published (§8)."""
    used = []
    if os.path.isdir(captures_dir):
        for name in os.listdir(captures_dir):
            parts = name.split("-", 1)
            if len(parts) == 2 and parts[0] == "attempt" and parts[1].isdigit():
                used.append(int(parts[1]))
    return os.path.join(captures_dir, "attempt-%d" % ((max(used) + 1) if used else 1))


def run_capture(runs: int, captures_dir: str, out_path: str, scratch_parent: str,
                pins_path: str, cli_override: str) -> int:
    """The §3.2 recapture, end to end: N probe calls into a numbered attempt
    directory, then the derivation.

    The probe prompt — not the registered one — is deliberate. The pre-prompt
    context precedes the prompt and does not depend on it, and running the
    registered prompt here would show the operator coverage profiles before the
    batch, which is exactly the cost Study 010's DEVIATIONS §1 records.
    """
    if os.path.exists(out_path):
        raise BatchError("%s already exists; a registered capture is never rewritten"
                         % out_path)
    if runs < MIN_CAPTURE_SLOTS:
        # Before a single call is spent: a recapture that could only produce one
        # context could never derive a capture from it.
        raise BatchError(
            "the recapture makes at least %d probe calls and --runs %d asks for "
            "fewer: the capture is derived only from contexts that agree, so one "
            "call could never produce one (§3.2)" % (MIN_CAPTURE_SLOTS, runs))
    attempt = next_attempt(captures_dir)
    slots = plan(runs, 1, attempt, stem="capture")
    preflight(runs, 1, slots, scratch_parent, pins_path, cli_override, "probe")
    os.makedirs(attempt, exist_ok=True)
    print("capture attempt: %s" % attempt)
    for slot in slots:
        status, code, stderr = invoke(slot, scratch_parent, pins_path, cli_override, "probe")
        if code is not None:
            refuse_slot(slot, code, status, stderr)
            raise BatchError("capture %s failed (%s); the batch does not start until two "
                             "captures agree. Fix the cause and run capture again: the "
                             "next attempt gets its own directory."
                             % (os.path.basename(slot), code))
        print("%s: exit %d" % (os.path.basename(slot), status))
    return capture_golden(attempt, out_path, runs, pins_path)


def capture_isolation_negative(out_dir: str, scratch_parent: str, pins_path: str,
                               cli_override: str, golden_override: str) -> int:
    """§6 C7: the isolation gate's power, demonstrated rather than assumed.

    ONE probe call with the operator's REAL home — everything else exactly as
    registered — whose registered expectation is that it FAILS the golden
    match. If it matches instead, the gate has no demonstrated power against
    home leakage in this environment; that is recorded and the batch proceeds
    unchanged. Registering both outcomes before the batch is what keeps this a
    control rather than a decision.

    THREE outcomes are registered, not two (§6 C7): `refused` (the expectation),
    `matched` (the limitation), and `no-context` — the call produced nothing
    comparable, so neither comparison happened. `no-context` returns NON-ZERO:
    it is a control that did not run, and returning 0 for it would report a
    step as done that reached neither registered comparison. Its verdict is
    still retained, so the failure is on disk rather than only in a shell's
    exit status.

    Retention is done by code, not by the operator's care: the call is made
    into a scratch slot, and the only bytes that reach the study are the
    comparison verdict, a CALL.json stripped of every member that names or
    enumerates the operator's environment, and — when the call produced one —
    the context digests. session.jsonl, stdout.raw and stderr.raw are digested
    and deleted here — publishing the transcript of a non-isolated run would
    publish an inventory of the operator's own machine, which is the thing the
    control exists to detect. The deletion is VERIFIED, not attempted: if the
    scratch slot survives the removal this refuses and names it, because
    "deleted by the driver" is a claim about the disk and `ignore_errors` would
    make it a claim about the call that was made.
    """
    verify_ported_bytes()
    pins = _load_json(pins_path)
    require_freeze(pins)
    assent = pins.get("isolationNegative", {}).get("operatorAssent")
    if assent != "granted":
        raise BatchError(
            "harness/PINS.json records operatorAssent %r: C7 is the one registered "
            "step that exposes the operator's real environment to the pinned CLI and "
            "it runs only with recorded assent (§6 C7)" % (assent,))
    if not os.path.isdir(scratch_parent):
        raise BatchError("scratch parent %s is not a directory" % scratch_parent)
    golden = require_golden(pins, golden_override)
    if os.path.exists(out_dir):
        raise BatchError("%s already exists; a registered control is never rewritten"
                         % out_dir)
    raw = os.path.join(scratch_parent, "s011-c7-raw-%d" % os.getpid())
    if os.path.exists(raw):
        raise BatchError("%s already exists" % raw)
    status, code, stderr = invoke(raw, scratch_parent, pins_path, cli_override,
                                  "probe", isolation="operator-home")
    try:
        call_path = os.path.join(raw, "CALL.json")
        if not os.path.isfile(call_path):
            raise BatchError("the control left no CALL.json (wrapper exit %d): %s"
                             % (status, stderr[-STDERR_TAIL:]))
        call = _load_json(call_path)
        session = os.path.join(raw, "session.jsonl")
        context_path = os.path.join(raw, "context.json")
        if os.path.isfile(session) and os.path.isfile(context_path):
            try:
                transcript_check.check_golden(session, call, golden)
                outcome, message = "matched", (
                    "the non-isolated call reproduced the golden pre-prompt context: "
                    "the golden gate has no demonstrated power against home leakage "
                    "in this environment (§6 C7, recorded as a limitation)")
            except transcript_check.TranscriptError as error:
                outcome, message = "refused", str(error)
        else:
            outcome, message = "no-context", (
                "the control produced no comparable context (wrapper exit %d, code %r): "
                "neither registered outcome occurred and the gate's power is "
                "undemonstrated" % (status, code))
        digests = {}
        for name in ("session.jsonl", "stdout.raw", "stderr.raw", "completion.txt"):
            path = os.path.join(raw, name)
            if os.path.isfile(path):
                digests[name] = _digest(path)
        os.makedirs(out_dir)
        if os.path.isfile(context_path):
            shutil.copyfile(context_path, os.path.join(out_dir, "context.json"))
        stripped = {key: value for key, value in call.items() if key not in C7_REDACTED}
        stripped["redacted"] = sorted(key for key in C7_REDACTED if key in call)
        stripped["note"] = ("§6 C7's CALL.json, stripped by batch.py of every member "
                            "that names or enumerates the operator's real environment. "
                            "The transcript was digested and deleted, not retained.")
        _write_json(os.path.join(out_dir, "CALL.json"), stripped)
        _write_json(os.path.join(out_dir, "VERDICT.json"), {
            "control": "C7 — the isolation gate's power",
            "registeredExpectation": "the golden match FAILS",
            "registeredOutcomes": ["refused", "matched", "no-context"],
            "outcome": outcome,
            "message": message,
            "wrapperExit": status,
            "wrapperCode": code,
            "goldenSha256": _digest(golden),
            "deletedByCode": digests,
            "operatorAssent": assent,
            "retention": "This file and a stripped CALL.json are always retained, and "
                         "context.json whenever the call produced a comparable "
                         "context (outcome 'no-context' is the case where it did "
                         "not). session.jsonl, stdout.raw, stderr.raw and any "
                         "completion were digested above and deleted by batch.py, and "
                         "the deletion is verified: publishing the transcript of a "
                         "deliberately non-isolated run would publish an inventory of "
                         "the operator's environment.",
        })
    finally:
        # Every exit from the block above passes here, including the ones that
        # are already carrying an exception — so the warning is printed on all
        # of them and the refusal is raised on the one that would otherwise
        # have reported success.
        shutil.rmtree(raw, ignore_errors=True)
        if os.path.exists(raw):
            print("WARNING: the control's scratch slot %s survived removal" % raw,
                  file=sys.stderr)
    if os.path.exists(raw):
        raise BatchError(
            "the control's scratch slot %s survived removal: its transcript is an "
            "inventory of the operator's environment and is still on disk. Remove it "
            "by hand and record the cause in DEVIATIONS.md before publishing anything "
            "from %s" % (raw, out_dir))
    print("C7: %s — %s" % (outcome, message))
    print("retained under %s: %s" % (out_dir, ", ".join(sorted(os.listdir(out_dir)))))
    if outcome == "no-context":
        print("refused: the control reached neither registered comparison; its verdict "
              "is retained and the gate's power is undemonstrated", file=sys.stderr)
        return 1
    return 0


def declare_shortfall(slots_dir: str, reason: str, pins_path: str) -> int:
    """§2.4: a batch that cannot finish declares the shortfall BEFORE anything
    is scored. The scorer refuses an incomplete batch without this file, so the
    declaration cannot be written after the rates are seen — and it refuses a
    declaration over a batch that is not short, so this file cannot be used to
    unblock scoring of a full or over-full one.

    It runs the same ported-bytes, interpreter and freeze preflight the calls
    and the scoring run: this file enters the published population arithmetic
    (§2.4), so it is not a step that may be taken under an unregistered
    interpreter or against an unfrozen preregistration."""
    verify_ported_bytes()
    if os.path.exists(RESULTS):
        raise BatchError("%s exists: a shortfall may not be declared after a rate has "
                         "been computed" % RESULTS)
    out_path = os.path.join(slots_dir, "SHORTFALL.json")
    if os.path.exists(out_path):
        raise BatchError("%s already exists" % out_path)
    if not reason:
        raise BatchError("--reason is required: a shortfall without a reason is a gap")
    pins = _load_json(pins_path)
    require_freeze(pins)
    registered = pins.get("batch", {}).get("runs")
    slots, _ = score_rates.collect_slots(slots_dir)
    if registered is not None and len(slots) >= registered:
        raise BatchError(
            "%d slots are present and %d were registered: a shortfall declares a SHORT "
            "batch, and this one is not short" % (len(slots), registered))
    _write_json(out_path, {
        "registeredRuns": registered,
        "completedSlots": len(slots),
        "reason": reason,
        "note": "Declared before scoring. The headline reports 'S of N slots completed' "
                "and rates are computed over the valid runs among the S. The scorer "
                "refuses if this count is not the contiguous slots actually present.",
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
    "                    [--pins PATH] [--golden PATH] [--cli-override PATH] [--dry-run]\n"
    "       batch.py capture --scratch-parent DIR [--captures DIR] [--out PATH]\n"
    "                    [--runs N] [--pins PATH] [--cli-override PATH]\n"
    "       batch.py capture-golden --slots DIR --out PATH [--min-slots N]\n"
    "       batch.py capture-isolation-negative --scratch-parent DIR [--out DIR]\n"
    "                    [--pins PATH] [--golden PATH] [--cli-override PATH]\n"
    "       batch.py shortfall --slots DIR --reason TEXT [--pins PATH]")

COMMANDS = ("run", "capture", "capture-golden", "capture-isolation-negative",
            "shortfall")


def main(argv: list) -> int:
    if len(argv) < 2 or argv[1] not in COMMANDS:
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
                             "--dry-run" in argv,
                             _argument(argv, "--golden"))
        if command == "capture":
            scratch_parent = _argument(argv, "--scratch-parent")
            if scratch_parent is None:
                raise BatchError("--scratch-parent is required")
            return run_capture(int(_argument(argv, "--runs", 2)),
                               _argument(argv, "--captures", DEFAULT_CAPTURES),
                               _argument(argv, "--out", DEFAULT_GOLDEN),
                               scratch_parent, pins_path,
                               _argument(argv, "--cli-override"))
        if command == "capture-isolation-negative":
            scratch_parent = _argument(argv, "--scratch-parent")
            if scratch_parent is None:
                raise BatchError("--scratch-parent is required")
            return capture_isolation_negative(
                _argument(argv, "--out", DEFAULT_NEGATIVE), scratch_parent,
                pins_path, _argument(argv, "--cli-override"),
                _argument(argv, "--golden"))
        slots_dir = _argument(argv, "--slots")
        if slots_dir is None:
            raise BatchError("--slots is required")
        if command == "capture-golden":
            return capture_golden(slots_dir, _argument(argv, "--out"),
                                  int(_argument(argv, "--min-slots", 2)), pins_path)
        return declare_shortfall(slots_dir, _argument(argv, "--reason"), pins_path)
    except (BatchError, score_rates.ScoreError, transcript_check.TranscriptError) as error:
        print("refused: %s" % error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
