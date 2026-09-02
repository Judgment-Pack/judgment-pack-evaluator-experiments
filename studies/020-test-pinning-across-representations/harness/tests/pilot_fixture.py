"""A SEALED, CHAINED pilot tree built without the wrapper — the fixture round-2
findings R2-7 and R2-8 made necessary.

R2-7's executed attack was a directory holding a two-counter `PILOT.json` and
a hand-authored rates record, which the freeze gate accepted. The gate now
authenticates the pilot from its ledger through `batch.py`'s own readers
(`pilot_replay`, `verify_seal_of`, `slot_outcome`), so a fixture that wants to
PASS it has to be the real thing: every slot stamped and sealed by
`batch.seal_slot()`, every record chained by `batch.ledger_record()`, the
round robin replayable from the records' own codes. This module builds
exactly that, with the per-arm outcomes a case asks for, and it is used by
`test_pilot.py` (the rates publisher and the freeze gate) and by
`test_manifest.py` (the calibration permit/require halves).

What it does NOT do: run the wrapper. `ThePilotEndToEnd` in `test_pilot.py`
drives the real wrapper through the stand-in CLI; this builder exists so the
gate's and the publisher's OWN rules can be driven in isolation, mutation by
mutation, without 36 subprocesses per case.

The transcript binding is the one thing a synthesized slot cannot satisfy
honestly (it needs the pinned prompt, model, effort and golden context), so
`stub_transcript()` patches `batch.transcript_verdict()` to read a per-slot
marker file — and the SEALED `TRANSCRIPT.json` is written to agree with that
marker, so `agreesWithSeal` is a real comparison here rather than a fiction.
"""
from __future__ import annotations

import hashlib
import json
import os
from unittest import mock

import batch

ARMS = ("A", "B", "C")
STAND_IN_EFFORT = "s020-stand-in-effort"
STAND_IN_MODEL = "s020-stand-in-model"


def _digest_bytes(body: bytes) -> str:
    return "sha256:" + hashlib.sha256(body).hexdigest()


class PilotTree:
    """One synthesized pilot under `<study>/calibration/<label>/`.

    `outcomes` maps an arm to a LIST of per-attempt outcome names, consumed in
    round-robin order; attempts past the end of an arm's list are ``clean``,
    so ``{"A": ["clean", "clean", "refused"]}`` refuses exactly the third
    attempt and ``{"C": ["timeout"] * 21}`` exhausts the cap. Outcome names:

    * ``clean``     — exit 0, completion present, transcript admissible
    * ``refused``   — wrapper exit 10 (`call-nonzero-exit`): REFUSAL.json, no
                      CALL.json, no completion
    * ``timeout``   — wrapper exit 12 (`call-timeout`), same shape
    * ``tool``      — exit 0, NO completion (the wrapper writes none for a
                      tool-using author), transcript `tool-use` / authoring
    * ``no-completion`` — exit 0, no completion, transcript admissible: the
                      unexplained `slot-shape` state

    The completion text is the same POLICY/TESTS pair for every clean slot;
    the scoring stubs in the tests decide what it scores as."""

    def __init__(self, study: str, label: str, pins: dict, outcomes=None,
                 completion: str = None, golden_sha256: str = None,
                 pins_sha256: str = None):
        self.study = study
        self.label = label
        self.pins = pins
        self.root = os.path.join(study, "calibration", label)
        self.outcomes = dict(outcomes or {})
        self.completion = completion or (
            "POLICY:\n```rego\npackage x\n```\nTESTS:\n```rego\npackage t\n```\n")
        self.golden_sha256 = golden_sha256 or (
            (pins.get("golden") or {}).get("sha256") or "sha256:" + "0" * 64)
        self.pins_sha256 = pins_sha256 or "sha256:" + "1" * 64
        self.records = []
        self.calls = []
        self.slots = []

    # -- construction --------------------------------------------------------

    def outcome_for(self, arm: str, attempt: int) -> str:
        plan = self.outcomes.get(arm) or []
        return plan[attempt - 1] if attempt <= len(plan) else "clean"

    def build(self) -> "PilotTree":
        os.makedirs(self.root, exist_ok=True)
        previous = None
        attempts = {arm: 0 for arm in ARMS}
        while True:
            entry = batch.pilot_next_entry(self.records)
            if entry is None:
                break
            attempts[entry["arm"]] += 1
            outcome = self.outcome_for(entry["arm"], attempts[entry["arm"]])
            slot = os.path.join(self.root, "arm-%s" % entry["arm"],
                                "run-%03d" % entry["slotIndex"])
            status, code = self._write_slot(slot, entry, outcome)
            if code is not None:
                batch.refuse_slot(slot, code, status, "stand-in refusal")
            self._stamp(slot, entry)
            manifest = batch.seal_slot(slot, entry)
            record = batch.ledger_record(entry, slot, status, code, manifest,
                                         previous)
            # `ledger_record()` records the path relative to batch.STUDY;
            # a stand-in study is the study here.
            record["path"] = os.path.relpath(slot, self.study)
            self.records.append(record)
            previous = batch.record_digest(record)
            self.calls.append({"arm": entry["arm"],
                               "runIndex": entry["runIndex"],
                               "indexWithinPilot": entry["globalIndex"],
                               "slot": record["path"], "code": code,
                               "wrapperExit": status, "citable": False})
            self.slots.append(slot)
        self.write_ledger()
        return self

    def _write_slot(self, slot: str, entry: dict, outcome: str) -> tuple:
        os.makedirs(slot)
        if outcome in ("refused", "timeout"):
            return (10, "call-nonzero-exit") if outcome == "refused" \
                else (12, "call-timeout")
        session = [
            {"type": "session_meta", "payload": {"id": "00000000-0000-4000-"
                                                        "8000-%012d"
                                                        % entry["globalIndex"],
                                                 "cwd": "/scratch"}},
            {"type": "turn_context",
             "payload": {"model": STAND_IN_MODEL, "cwd": "/scratch",
                         "effort": STAND_IN_EFFORT,
                         "collaboration_mode": {"settings": {
                             "reasoning_effort": STAND_IN_EFFORT}}}},
        ]
        if outcome == "tool":
            session.append({"type": "response_item",
                            "payload": {"type": "function_call",
                                        "name": "shell", "arguments": "{}",
                                        "call_id": "c1"}})
        with open(os.path.join(slot, "session.jsonl"), "wb") as handle:
            for row in session:
                handle.write((json.dumps(row) + "\n").encode("utf-8"))
        if outcome == "clean":
            with open(os.path.join(slot, "completion.txt"), "w",
                      encoding="utf-8") as handle:
                handle.write(self.completion)
        # The C4 members the real wrapper writes (R2-11): the transfer gate's
        # eight exact rows and the duration the executed-call cohort keys on.
        seconds = 90 + 7 * entry["globalIndex"]
        call = {
            "slot": os.path.basename(slot),
            "slotIndex": entry["slotIndex"],
            "arm": entry["arm"],
            "argv": ["codex", "exec", "--ignore-user-config", "-m",
                     STAND_IN_MODEL, "--sandbox", "workspace-write", "-c",
                     "mcp_servers={}"],
            "model": STAND_IN_MODEL,
            "cli": "codex-cli 0.145.0-fake",
            "binarySha256": "sha256:" + "2" * 64,
            "codexHomeIsolated": True,
            "environmentScrubbed": True,
            "isolatedHomeInventory": [".codex/auth.json", ".codex/config.toml"],
            "startedAt": "2026-08-24T10:00:00Z",
            "endedAt": "2026-08-24T10:%02d:%02dZ" % divmod(seconds, 60),
            "durationSeconds": float(seconds),
            "armPromptSha256": ((self.pins.get("arms") or {}).get(entry["arm"])
                                or {}).get("promptSha256"),
            "promptKind": "registered",
            "pinsSha256": self.pins_sha256,
            "goldenSha256": self.golden_sha256,
            "reasoningEffort": (self.pins.get("codex") or {})
            .get("reasoningEffort"),
            "reasoningEffortWitnessed": True,
            "pinLabel": "PILOT",
            "citable": False,
            "durationSeconds": 1.0,
        }
        with open(os.path.join(slot, "CALL.json"), "w",
                  encoding="utf-8") as handle:
            json.dump(call, handle, indent=2, sort_keys=True)
        # The marker `stub_transcript()` reads, and the sealed verdict that
        # agrees with it.
        verdict = TRANSCRIPTS[outcome]
        with open(os.path.join(slot, ".stand-in-transcript"), "w") as handle:
            handle.write(outcome)
        with open(os.path.join(slot, batch.TRANSCRIPT_NAME), "w",
                  encoding="utf-8") as handle:
            json.dump({"slot": os.path.basename(slot), "arm": entry["arm"],
                       "globalIndex": entry["globalIndex"],
                       "admissible": verdict["admissible"],
                       "reason": verdict["reason"], "side": verdict["side"],
                       "code": verdict["code"], "message": None,
                       "goldenSha256": self.golden_sha256}, handle, indent=2)
        return 0, None

    def _stamp(self, slot: str, entry: dict) -> None:
        """`batch.stamp_slot()` checks the wrapper's stamps against the
        registry's arm prompt; the stand-in registry may not carry one, so the
        three schedule members are stamped the way the driver does."""
        call_path = os.path.join(slot, "CALL.json")
        if not os.path.isfile(call_path):
            return
        with open(call_path, encoding="utf-8") as handle:
            call = json.load(handle)
        for member in ("globalIndex", "round", "position"):
            call[member] = entry[member]
        with open(call_path, "w", encoding="utf-8") as handle:
            json.dump(call, handle, indent=2, sort_keys=True)

    def write_ledger(self, **edits) -> None:
        status = batch.pilot_status(self.records)
        body = {
            "pilotVersion": "2",
            "record": {"mode": "pilot", "label": self.label,
                       "citable": False, "runsPerArm": batch.PILOT_RUNS_PER_ARM},
            "label": self.label,
            "registeredScoredPerArm": batch.PILOT_RUNS_PER_ARM,
            "attemptCapPerArm": batch.PILOT_ATTEMPT_CAP_PER_ARM,
            "callsMade": len(self.records),
            "callsRegistered": batch.PILOT_CALL_CAP,
            "attemptCap": batch.PILOT_ATTEMPT_CAP,
            "perArm": status["perArm"],
            "short": status["short"],
            "complete": status["complete"],
            "model": STAND_IN_MODEL,
            "binarySha256": "sha256:" + "2" * 64,
            "reasoningEffort": (self.pins.get("codex") or {})
            .get("reasoningEffort"),
            "goldenSha256": self.golden_sha256,
            "pinsSha256": self.pins_sha256,
            "cliOverride": None,
            "citable": False,
            "records": self.records,
            "calls": self.calls,
        }
        body.update(edits)
        with open(os.path.join(self.root, batch.PILOT_LEDGER_NAME), "w",
                  encoding="utf-8") as handle:
            json.dump(body, handle, indent=2, sort_keys=True)
            handle.write("\n")
        with open(os.path.join(self.root, batch.PILOT_TABLE_NAME), "w",
                  encoding="utf-8") as handle:
            handle.write("# Pre-freeze calibration pilot — %s\n" % self.label)

    # -- reading back ----------------------------------------------------------

    def ledger(self) -> dict:
        with open(os.path.join(self.root, batch.PILOT_LEDGER_NAME),
                  encoding="utf-8") as handle:
            return json.load(handle)

    def slot_path(self, arm: str, run_index: int) -> str:
        return os.path.join(self.root, "arm-%s" % arm, "run-%03d" % run_index)


#: The per-outcome verdicts `stub_transcript()` returns and the seal carries.
TRANSCRIPTS = {
    "clean": {"admissible": True, "reason": None, "side": None, "code": None,
              "message": None},
    "no-completion": {"admissible": True, "reason": None, "side": None,
                      "code": None, "message": None},
    "tool": {"admissible": False, "reason": "tool-use", "side": "authoring",
             "code": "author-protocol-violation",
             "message": "the author used a tool"},
}


def stub_transcript():
    """Patch `batch.transcript_verdict()` to read the slot's stand-in marker.
    Returns the patcher; the caller starts and stops it."""
    def verdict(slot, arm, pins, golden_path):
        marker = os.path.join(slot, ".stand-in-transcript")
        with open(marker) as handle:
            outcome = handle.read().strip()
        return dict(TRANSCRIPTS[outcome])
    return mock.patch.object(batch, "transcript_verdict", verdict)


def build(study: str, label: str, pins: dict, **kwargs) -> PilotTree:
    return PilotTree(study, label, pins, **kwargs).build()


#: The five calibration members the PILOT CEREMONY fills (freeze pins since
#: round 2). A stand-in registry that fills every freeze pin with a digest
#: string would otherwise read as "a pilot that has run"; a pilot fixture
#: resets them to the pre-pilot state it is about to leave.
CEREMONY_MEMBERS = ("label", "outputSha256", "derivedFloor",
                    "c4ReferenceSha256", "dispersionSha256")


def reset_calibration_pins(pins: dict) -> dict:
    calibration = pins.setdefault("calibration", {})
    for member in CEREMONY_MEMBERS:
        calibration[member] = None
    return pins


def write_analysis_artifacts(study: str, label: str) -> dict:
    """The two post-pilot artifacts a freeze-gate fixture needs, built the
    way `harness/pilot_analysis.py` builds them where that is cheap (the C4
    reference from the sealed slots' own CALL.json bytes) and MINIMALLY where
    it is not (an eighteen-row dispersion table with no forbidden member, no
    scoring). Returns {name: sha256:...}."""
    import hashlib
    from e4lib import family, transfer
    root = os.path.join(study, "calibration", label)
    by_arm = {arm: [] for arm in ARMS}
    for arm in ARMS:
        arm_dir = os.path.join(root, "arm-%s" % arm)
        if not os.path.isdir(arm_dir):
            continue
        for name in sorted(os.listdir(arm_dir)):
            slot = os.path.join(arm_dir, name)
            call_path = os.path.join(slot, "CALL.json")
            if not os.path.isfile(call_path):
                continue
            with open(call_path, encoding="utf-8") as handle:
                call = json.load(handle)
            completion = os.path.join(slot, "completion.txt")
            by_arm[arm].append({
                "call": transfer.call_members(call),
                "completionBytes": (os.path.getsize(completion)
                                    if os.path.isfile(completion) else None),
                "reasoningOutputTokens": 400 + len(name)})
    reference = transfer.reference_document(label, transfer.observables(by_arm))
    table = {"label": label, "citable": False, "goNoGo": "GO",
             "registeredN": 60,
             "perMember": [{"id": member.id, "level": member.level,
                            "engine": member.column,
                            "population": member.population,
                            "adjustment": "ANCOVA" if member.adjusted else None,
                            "sigmaBasis": ("residual" if member.adjusted
                                           else "pooledWithinArm"),
                            "sigma": 0.1, "n": {"A": 12, "B": 12, "C": 12},
                            "df": 33, "sigmaCI95": [0.08, 0.13],
                            "mdeAtPilotN": 0.11, "mdeAtRegisteredN": 0.05}
                           for member in family.MEMBERS]}
    digests = {}
    for name, body in (("C4-REFERENCE.json", reference),
                       ("PILOT-DISPERSION.json", table)):
        target = os.path.join(root, name)
        with open(target, "w", encoding="utf-8") as handle:
            json.dump(body, handle, indent=2, sort_keys=True)
            handle.write("\n")
        with open(target, "rb") as handle:
            digests[name] = "sha256:" + hashlib.sha256(handle.read()).hexdigest()
    return digests
