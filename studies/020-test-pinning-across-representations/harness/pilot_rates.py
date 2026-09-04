#!/usr/bin/env python3
"""Section 2a's pilot counts publisher (round-1 finding R1-17).

`batch.py pilot` spends the calls and registers that it computes no rate; this
module computes the per-arm PERFECT and IDENTITY counts over the pilot's 36
slots and publishes them as `calibration/<label>/PILOT-RATES.json` — the exact
record `calibration/derive_floor.py` consumes, validated through the sealed
deriver's OWN `validate_record()` at publication time, so the producer and the
go/no-go's consumer cannot drift apart the way `score_run()` and
`reviewer.execute()` did (round-1 finding R1-13).

ONE MIRROR, NOT TWO. Every slot is scored by `sweep_rates.score_slot()` — the
same extract → admit → gold → identity order `score.score_run()` holds — so
this module adds NO second reading of the scoring rule; what it adds is the
pilot's aggregation and the derive_floor handoff. The registered scope
travels too: **no kill quantity is computed**, because a kill figure computed
before the freeze would be the informal peek §2a keeps out of the go/no-go.

VOCABULARY: the published record carries `identityPass`, the rates-ledger
publication vocabulary `SWEEP-RATES.json` established (and the shape
`derive_floor.py`'s registered contract names); `referenceIdentityPass` is the
run-record vocabulary of `score.py` and does not occur here.

The go/no-go itself is IN the published record: derived floors for every arm
on both bases, and the DECLARED minimum's verdict. §2a.4(3): the threshold's
seat is a pre-freeze go/no-go, and only that — no post-batch row reads it.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import batch                           # noqa: E402
import integrity                       # noqa: E402
import sweep_rates                     # noqa: E402
from sweep_rates import RatesError     # noqa: E402
from e4lib import admit as admit_lib   # noqa: E402

HARNESS = HERE
STUDY = os.path.dirname(HARNESS)
CALIBRATION_ROOT = os.path.join(STUDY, "calibration")
DERIVE_FLOOR_PATH = os.path.join(CALIBRATION_ROOT, "derive_floor.py")
RATES_LEDGER_NAME = "PILOT-RATES.json"
RATES_HEADING = "## Per-arm perfect and identity counts, and the go/no-go"
ARMS = ("A", "B", "C")
#: §2a.2 as amended (R2-10): the SCORED, apparatus-clean count.
PILOT_CALLS_PER_ARM = 12


def derive_floor_module():
    """The SEALED deriver, imported from its committed seat — §2a.4(1)'s
    `calibration/derive_floor.py` and never a copy of its arithmetic here: a
    second Clopper-Pearson implementation in this file would be a human
    number's way back in."""
    if not os.path.isfile(DERIVE_FLOOR_PATH):
        raise RatesError("RATES-NO-DERIVER calibration/derive_floor.py is "
                         "absent and §2a.4(1) seals it before the pilot runs")
    spec = importlib.util.spec_from_file_location("derive_floor",
                                                  DERIVE_FLOOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _bare(digest) -> str:
    return digest.split(":")[-1] if isinstance(digest, str) else digest


def slot_pre_step(record: dict, ledger: dict, pins: dict, label: str) -> tuple:
    """ROUND-2 FINDING R2-8: `score.read_slot()`'s pre-scoring ORDER, applied
    to one sealed pilot slot — `(slot_dir, prior_code, prior_side,
    transcript)`. The primary path's reads, not a new reading of them.

    1. The SEAL recomputes and equals the ledger's `manifestSha256` — a slot
       whose bytes moved after sealing refuses the whole publication.
    2. The WRAPPER outcome (`REFUSAL.json` / `CALL.json`): a refusal code is
       the slot's code, apparatus side.
    3. `CALL.json.pinsSha256` equals the LEDGER HEADER's `pinsSha256` — the
       registry every call ran under. Not the current registry: §2a.6's own
       ceremony edits it after the pilot (label, N, output digest go in), so
       the reconciliation is to what the ledger names, exactly as the batch
       reconciles to ATTEMPT.json. A mismatch is `registry-mismatch`.
    4. `CALL.json.goldenSha256` equals the header's — `golden-context-mismatch`.
    5. The TRANSCRIPT BINDING, RECOMPUTED from the sealed bytes through
       `batch.transcript_verdict()` (one binding, two callers): an AUTHORING
       side outranks a missing completion, because the wrapper writes no
       completion for a tool-using author by design and the missing file must
       not turn that authoring outcome into `slot-shape` apparatus.
    6. Only then: no completion is `slot-shape`."""
    slot_dir = os.path.join(STUDY, record["path"])
    if os.path.islink(slot_dir) or not os.path.isdir(slot_dir):
        raise RatesError("RATES-NO-SLOT the ledger names %s and it is not a "
                         "directory on disk" % record["path"])
    entry = {key: record[key] for key in batch.SCHEDULE_KEYS}
    try:
        sealed = batch.verify_seal_of(slot_dir, entry)
    except batch.BatchError as error:
        raise RatesError("RATES-SEAL %s" % error)
    if sealed != record.get("manifestSha256"):
        raise RatesError(
            "RATES-SEAL %s: the slot's recomputed seal %s is not the ledger's "
            "%s — the tree on disk is not the one the chain sealed"
            % (record["path"], sealed, record.get("manifestSha256")))
    try:
        status, code = batch.slot_outcome(slot_dir)
    except batch.BatchError as error:
        raise RatesError("RATES-OUTCOME %s" % error)
    if code != record.get("code") or status != record.get("wrapperExit"):
        raise RatesError(
            "RATES-OUTCOME %s: the slot's own bytes say exit %r / %r and the "
            "ledger records %r / %r" % (record["path"], status, code,
                                        record.get("wrapperExit"),
                                        record.get("code")))
    if code is not None:
        return slot_dir, code, "apparatus", None
    call = batch._load_json(os.path.join(slot_dir, "CALL.json"))
    stamped = call.get("pinsSha256")
    if not isinstance(stamped, str) or \
            _bare(stamped) != _bare(ledger.get("pinsSha256")):
        return slot_dir, "registry-mismatch", "apparatus", None
    if _bare(call.get("goldenSha256")) != _bare(ledger.get("goldenSha256")):
        return slot_dir, "golden-context-mismatch", "apparatus", None
    try:
        verdict = batch.transcript_verdict(slot_dir, record["arm"], pins,
                                           batch.golden_path_for(pins))
    except batch.transcript_check.UnclassifiedRefusal as error:
        raise RatesError(
            "RATES-TRANSCRIPT %s: the binding refused with a cause §1a does "
            "not name (%s)" % (record["path"], error))
    transcript = {"admissible": verdict["admissible"],
                  "reason": verdict["reason"], "side": verdict["side"],
                  "code": verdict["code"]}
    if verdict["side"] == "authoring":
        return slot_dir, verdict["code"], "authoring", transcript
    if not os.path.isfile(os.path.join(slot_dir, "completion.txt")):
        return slot_dir, "slot-shape", "apparatus", transcript
    if verdict["code"] is not None:
        return slot_dir, verdict["code"], verdict["side"], transcript
    return slot_dir, None, None, transcript


def pilot_rates(tools, label: str, gold: list, scratch: str,
                pins: dict) -> dict:
    ledger_path = os.path.join(CALIBRATION_ROOT, label, "PILOT.json")
    if not os.path.isfile(ledger_path):
        raise RatesError("RATES-NO-PILOT no ledger at calibration/%s/PILOT.json"
                         % label)
    with open(ledger_path, "rb") as handle:
        ledger = json.loads(handle.read().decode("utf-8"),
                            **integrity.LOAD_KWARGS)
    records = ledger.get("records")
    if not isinstance(records, list) or not records:
        raise RatesError(
            "RATES-NO-LEDGER calibration/%s/PILOT.json carries no chained "
            "records: a pilot the driver did not seal and chain (R2-8) is not "
            "a pilot this module scores" % label)
    if ledger.get("label") != label:
        raise RatesError("RATES-LABEL the ledger names %r and this run asked "
                         "for %r" % (ledger.get("label"), label))
    try:
        batch.pilot_replay(records, label)
    except batch.BatchError as error:
        raise RatesError("RATES-REPLAY %s" % error)
    if not ledger.get("complete") or ledger.get("short"):
        raise RatesError(
            "PILOT-INCOMPLETE the ledger records an unfinished or short pilot "
            "(%d attempts made, per arm %s, short %s): §2a.1's table prices "
            "the derived floor at n = %d apparatus-clean per arm, so a partial "
            "pilot publishes no rates — it is a DEVIATIONS.md event"
            % (len(records), ledger.get("perArm"), ledger.get("short"),
               PILOT_CALLS_PER_ARM))
    guard_registered = admit_lib.guard_is_registered()
    rows = []
    for record in records:
        slot_dir, prior_code, prior_side, transcript = slot_pre_step(
            record, ledger, pins, label)
        workdir = os.path.join(scratch, record["arm"],
                               "run-%03d" % record["slotIndex"])
        os.makedirs(workdir, exist_ok=True)
        row = sweep_rates.score_slot(tools, record["arm"], slot_dir, gold,
                                     guard_registered, workdir,
                                     prior_code=prior_code,
                                     prior_side=prior_side)
        row["globalIndex"] = record["globalIndex"]
        row["transcript"] = transcript
        rows.append(row)
    per_arm = {}
    for arm in ARMS:
        mine = [row for row in rows if row["arm"] == arm]
        # ROUND-2 FINDING R2-10: ONE reading of §1a's population rule, shared
        # with the sweep's publisher. The scored denominator is the
        # apparatus-clean calls; the excluded ones are published under their
        # own codes rather than counted as failing suites.
        per_arm[arm] = sweep_rates.per_arm_cell(mine)
        if per_arm[arm]["calls"] != PILOT_CALLS_PER_ARM:
            raise RatesError(
                "PILOT-SHORT arm %s reached %d apparatus-clean calls of the "
                "registered %d (attempted %d, apparatus-excluded %d: %s). "
                "§2a.1's table prices the derived floor at n = %d exactly, so "
                "a short arm publishes NO rates — it is a DEVIATIONS.md event "
                "under §2a.2's amended attempt rule, never a smaller "
                "denominator"
                % (arm, per_arm[arm]["calls"], PILOT_CALLS_PER_ARM,
                   per_arm[arm]["attempted"], per_arm[arm]["apparatusExcluded"],
                   per_arm[arm]["apparatusCodes"], PILOT_CALLS_PER_ARM))
    record = {
        "label": label,
        "obligation": "PREREGISTRATION.md section 2a — the pilot's per-arm "
                      "perfect and identity counts, computed by "
                      "harness/pilot_rates.py through the registered scoring "
                      "components over the SEALED slots the chained ledger "
                      "names (R2-8), no kill quantity computed by construction",
        "citable": False,
        "goldRows": len(gold),
        "guardRegistered": guard_registered,
        "ledgerPinsSha256": ledger.get("pinsSha256"),
        "ledgerGoldenSha256": ledger.get("goldenSha256"),
        "attemptsRecorded": len(records),
        "perArm": per_arm,
        "slots": rows,
    }
    floor = derive_floor_module()
    try:
        floor.validate_record(record)
        record["derived"] = floor.derive(record)
        calibration = pins.get("calibration") or {}
        record["goNoGo"] = floor.go_no_go(
            record["derived"], calibration.get("minimumViable"),
            calibration.get("minimumViableBasis"))
    except floor.FloorError as refusal:
        raise RatesError("RATES-FLOOR the sealed deriver refused the record "
                         "this module built: %s" % refusal)
    return record


def render_rates(body: dict) -> str:
    verdict = body["goNoGo"]
    lines = [
        "",
        RATES_HEADING,
        "",
        "Scored post-pilot by `harness/pilot_rates.py` through the registered "
        "scoring components (extract, admit with the presence-idiom guard "
        "live, the gold loop over %d rows, `referenceIdentity` with its "
        "registered pre-steps), and the record validated by the sealed "
        "`calibration/derive_floor.py` before publication. **No kill quantity "
        "is computed**, by registered scope. `citable: false`, like "
        "everything in this file." % body["goldRows"],
        "",
        "| arm | attempted | apparatus-excluded | perfect | identity | "
        "perfect floor | identity floor | codes |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for arm in ARMS:
        cell = body["perArm"][arm]
        floors = body["derived"]["perArm"][arm]
        codes = ", ".join("`%s`" % code for code in cell["codes"]) or "—"
        excluded = ", ".join("`%s`×%d" % pair
                             for pair in sorted(cell["apparatusCodes"].items()))
        lines.append("| %s | %d | %d%s | %d/%d | %d/%d | %.3f | %.3f | %s |" % (
            arm, cell["attempted"], cell["apparatusExcluded"],
            " (%s)" % excluded if excluded else "",
            cell["perfect"], cell["calls"], cell["identityPass"],
            cell["calls"], floors["perfectFloor"], floors["identityFloor"],
            codes))
    lines.append("")
    lines.append("**Go/no-go (§2a.4):** declared minimum %s on `%s` → %s." % (
        verdict["minimumViable"], verdict["basis"],
        "GO" if verdict["go"] else
        "NO-GO (failing arms: %s) — %s" % (", ".join(verdict["failingArms"]),
                                           verdict["consequence"])))
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Section 2a's pilot counts and go/no-go record.")
    parser.add_argument("--label", required=True,
                        help="the pilot's dated label under calibration/")
    parser.add_argument("--scratch", default=None)
    parser.add_argument("--write", action="store_true",
                        help="write PILOT-RATES.json and append the section "
                             "to PILOT.md")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    ledger_out = os.path.join(CALIBRATION_ROOT, args.label, RATES_LEDGER_NAME)
    table_path = os.path.join(CALIBRATION_ROOT, args.label, "PILOT.md")
    if args.write and not args.force:
        if os.path.exists(ledger_out):
            raise RatesError("RATES-EXISTS %s exists; recomputation replaces "
                             "it only under --force"
                             % os.path.relpath(ledger_out, STUDY))
        if os.path.isfile(table_path):
            with open(table_path, "r", encoding="utf-8") as handle:
                if RATES_HEADING in handle.read():
                    raise RatesError("RATES-EXISTS PILOT.md already carries a "
                                     "rates section; --force replaces nothing "
                                     "here — remove it deliberately first")

    pins = sweep_rates.load_pins()
    tools = sweep_rates.toolchain(pins)
    gold = sweep_rates.load_gold()
    if args.scratch:
        os.makedirs(args.scratch, exist_ok=True)
        body = pilot_rates(tools, args.label, gold, args.scratch, pins)
    else:
        with tempfile.TemporaryDirectory() as scratch:
            body = pilot_rates(tools, args.label, gold, scratch, pins)
    sys.stdout.write(render_rates(body))
    if args.write:
        with open(ledger_out, "w", encoding="utf-8") as handle:
            json.dump(body, handle, indent=2, sort_keys=True)
            handle.write("\n")
        with open(table_path, "a", encoding="utf-8") as handle:
            handle.write(render_rates(body))
        sys.stdout.write("\nwrote %s and appended the section to PILOT.md\n"
                         % os.path.relpath(ledger_out, STUDY))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RatesError as refusal:
        sys.stderr.write("%s\n" % refusal)
        sys.exit(1)
