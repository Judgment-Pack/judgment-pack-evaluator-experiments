#!/usr/bin/env python3
"""The batch driver.

**STUDY 020 PORT NOTE.** These are Study 019's bytes, taken by digest under
`harness/PORTS.md`'s two-sided table. The lineage sentence below is 019's own and is
kept as history; the binding that RUNS is 020's — `harness/integrity.py` verifies
Study 019's lock first (`harness/STUDY-MANIFEST.sha256`, at the digest 019's own
registry pins for it) and binds this file's source cell to 019's line for it.
`PREREGISTRATION.md` §7 lists this file under "ported with no design change" —
and THREE REGISTERED DELTAS have since landed in it, each named where it lives:

* **§7 delta 7 (the schedule).** This file holds NO round count of its own. 019
  hard-coded `ROUNDS = 50`, `RUNS_PER_ARM = 50`, `REGISTERED_SLOTS = 150`, a
  two-element `TAIL` and the pair (1, 1) as the registered balance floor; §2
  says "at any other round count that assertion is wrong by construction", and
  §2.1 makes 020's N an OUTPUT of the pre-pilot effort sweep. So the shape is
  read from `harness/PINS.json` (`_registered_batch_shape()`), the authority is
  `derive_order(rounds)` at any N, `schedule()` asserts the expansion attains
  the spreads the registry PUBLISHES, and `derive-schedule --rounds N` prints
  the block the registry takes at the swept N.
* **§7 delta 6 (`registeredLabelRule`).** `require_design_time_pins()` checks
  §2's `resolvedAtDesignTime` pins under EVERY label — the freeze rule is
  `integrity.study_label()`'s and is untouched here — with §2.1's M-25 ruling
  as its one exemption: a `--sweep` label exempts `codex.reasoningEffort` ALONE,
  because the sweep is what resolves it.
* **§7 delta 8 (the freeze gate's `calibration/` rule).**
  `calibration_freeze_problems()` permits the subtree, requires it, and still
  refuses any `results/primary-attempt-*`.

WHAT THIS FILE DELIBERATELY DOES NOT DO
---------------------------------------
It does not write `harness/PINS.json`. `derive-schedule` PRINTS the block a
person then edits in: a driver that rewrote its own pins is a driver that could
rewrite them after the freeze. It also never runs the sweep or the pilot outside
the harness — §2.1: "Running the sweep outside the harness is rejected on sight:
that is the 019 failure exactly."

PORTED from Study 012's `harness/batch.py`
(sha256 `6ee3bf3e2b217257fe38976df4610461c9ed9866db485678348b3ad8036fdcf3`, the
destination digest Study 012's own `harness/PORTS.md` records for it, at commit
`019c95be9e86c575878015954dfec17e4f84e683`). `harness/PORTS.md` in THIS study
carries the two-sided table and the enumerated change list; `harness/integrity.py`
machine-reads it and binds this file to that digest before anything runs.

**The calling half is now ported** — SCAFFOLD items D1–D8 (preflight, the slot
invocation, the seal, the chained ledger, resume by schedule index,
reconciliation, the shortfall) and G1–G2 (the golden-context capture and the
isolation negative control). What is NOT here, and is not a deferral this file
can hide, is the SCORER: `harness/score.py` owns admission, the rates and every
verdict, and this module publishes no judgment about a completion.

The enumerated changes to what is carried (PREREGISTRATION.md §2 "Batch shape",
§1a, §7):

1. **Three arms, not five.** `ARMS = ("A", "B", "C")` — Judgment Pack, raw
   Rego, Rego under the prescribed judgment convention (§3). Every derived
   number moves with it and none is transcribed: `POSITIONS` is 3, `SEQUENCES`
   is 6, `RUNS_PER_ARM` is 50 and `REGISTERED_SLOTS` is 150.
2. **The schedule is re-derived for three arms over the same 150 slots.**
   Study 012's 150 slots were 30 rounds of five; this study's are **50 rounds
   of three**, and 50 is not a multiple of the 6 Williams sequences — so the
   order cannot be whole blocks of the table, and exact balance is
   arithmetically unavailable (50 slots over 3 positions, 149 transitions over
   6 ordered pairs). What is registered instead is the **arithmetic floor of
   both spreads**, attained by a search this file performs rather than
   asserts: `derive_order()` enumerates every one of the 720 block
   permutations against every one of the 30 ordered two-sequence tails, keeps
   only orders in which no arm ever immediately follows itself, and returns
   the lexicographically-least of those that minimize
   (position spread, transition spread). `BLOCK_ORDER` and `TAIL` below are
   that answer, restated as constants so the driver does not run a search at
   import time, and `harness/tests/test_schedule.py` asserts the two are the
   same order and re-derives the balance properties from the expansion.
3. **The per-call timeout ceiling is 2700 s and is an APPARATUS bound**
   (§2 "Batch shape", §1a). Study 012 registered no ceiling and its wrapper
   ran unbounded. Here the wrapper enforces it, exits **12** when it fires,
   and this file maps that status to the apparatus code `call-timeout`.
   §1a records why the code's SIDE is registered in reviewed code rather than
   left to the driver: the design-phase pilot driver mis-filed timeouts as an
   authoring outcome, which silently moves a run from the excluded
   pipeline-invalid set into the denominator of every rate.
4. **The registered code partition is a named constant here** (`CODE_PARTITION`),
   and `harness/tests/test_partition.py` diffs it against §1a's own two lists.
   Study 012 spelled its partition inside `score_rates.py`'s scoring functions;
   this study's scorer does not exist yet, and the partition is the one part of
   it that must exist before the freeze because §1a registers it.
5. **The wrapper lives at `harness/authoring_call.sh`.** Study 012 kept it in
   `transcription/`; this study's `transcription/` tree does not exist yet and
   this gate is scoped to `harness/`. The wrapper's own anchor — `$STUDY` is
   the parent of the wrapper's directory — is unchanged and correct at either
   location, which is why the move costs no guard (`harness/PORTS.md`).

6. **The freeze gate is the REGISTERED LABEL RULE, not one pin.** Study 012's
   `require_freeze()` read a single member (`freeze.preregistrationSha256`).
   This study's registry decides REGISTERED-vs-PILOT over the WHOLE freeze set
   in one place (`integrity.study_label()`, `harness/PINS.json`'s
   `registeredLabelRule`), because Study 014's round 3 found a registered run
   reachable with only the preregistration digest filled. `require_freeze()`
   therefore refuses unless every freeze pin is non-null AND
   `PREREGISTRATION.md` hashes to the pin — strictly more than 012 checked, at
   the member names this registry actually carries.
7. **The no-new-slots marker is the ATTEMPT ROOT.** Study 012 wrote one
   `RESULTS.json`; this study's scorer takes `--attempt-root
   results/primary-attempt-001` and refuses if it exists (SCAFFOLD S1), so the
   thing whose existence means "a rate has been computed" is that directory.
   `ATTEMPT_ROOT` is the constant, and the rule it enforces is 012's unchanged:
   no slot is created, and no ledger record completed, after a rate exists.
8. **`WRAPPER_CODES` is DERIVED from `WRAPPER_EXIT_MEANINGS`**, so status 12
   cannot be mapped in one table and missing from the other. Study 012 wrote
   the two tables out separately and had no status 12 to keep in step; here
   every place 012 mapped 10/11 reads the derived table and gets the third
   branch for free (`harness/SCAFFOLD.md`'s second known-owed edit).
9. **The ledger's atomic-write temporary keeps its registered constant path**
   (`arms/BATCH.json.partial`) for 012's three reasons, and needs no exclusion
   entry here: this study's manifest is ADR 0004's EXACT SET over the
   registered documents and `harness/`, so `arms/` carries no covered byte and
   a residue moves nothing. `harness/tests/test_batch.py` asserts both halves —
   the constant is that path, and the path is outside `manifest_entries()`.
10. **The pieces Study 012 kept in `score_rates.py` are carried HERE**, because
   this study's scorer does not exist yet and four of them are preconditions of
   the CALLS: `C7_OUTCOMES`, `session_identity()`, `c7_record_shape_problems()`
   and `collect_slots()`. They are ported from Study 012's `harness/score_rates.py`
   (sha256 `f4d4463f081439f147a341bb38d8a6b709b3860f73f6f4e524234a180ec23336`,
   012's own destination digest) and `harness/PORTS.md` records that inside this
   file's row — `integrity.REQUIRED_PORTS` fixes the destination set at five
   and a second row naming this destination would refuse, so the provenance
   goes where the destination's row is. `harness/score.py` must read all four
   from here, exactly as it must read `CODE_PARTITION` from here.
11. **`require_lawful_destination()` is rewritten for ADR 0004's exact set.**
   Study 012's version reads `freeze.excluded` and asks whether a destination
   lies inside a registered exclusion TREE; this registry has no such member,
   because the manifest is an exact set rather than a whole-tree scan. The rule
   is therefore stated in this study's own terms — a destination is lawful when
   writing into it cannot add a covered entry — and it is computed from
   `make_manifest`'s own constants, so it cannot drift from the manifest it is
   about.
12. **`STUDY_CLI_STANDIN`** names a CLI when `--cli-override` does not. It
   REMOVES NO GATE: the named binary goes through `preflight()`'s digest check
   against `codex.binarySha256` and through the wrapper's own digest and
   version gates, so under the committed registry it refuses. It exists because
   every model-call path in this file must be reachable by a test that has no
   codex, and a test seam that is checked by the same gates as the production
   path is a seam and not a hole (`harness/tests/test_batch.py` asserts the
   refusal under the committed registry).

13. **THE PRE-PILOT EFFORT SWEEP IS A MODE OF THIS DRIVER** (§2.1, M-8/M-20/
   M-24/M-25) — section D9, and the one addition here that Study 012 has no
   counterpart for at all. §2.1 registers `n = 3/arm across three settings —
   27 calls`, run through this apparatus and never outside it, published in
   full, `citable: false`, with a per-setting abort rule and a call cap; the
   registration was on the record and the harness had no mode that could run
   it. `batch.py sweep` is that mode. It carries §2.1's registered constants —
   the swept SET (`SWEEP_SETTINGS`, the maintainer's dated 2026-08-24
   decision), the per-arm count, the derived 27-call cap, the 72 h budget and
   its priced N branch — and checks every one of them against the registry's
   own `sweep` block before a call, because a registration carried in two
   places is only safe if a disagreement refuses. It writes under
   `SWEEP_ROOT` and not `arms/`, which is what keeps R10-1's occupancy gate
   off it structurally; it claims `PIN_LABEL=SWEEP` and the per-call
   `SWEEP_EFFORT` at `invoke()` and nowhere else; it runs M-24's WITNESS
   RESOLUTION as step zero over the first sweep call's own transcript and
   records which branch fired; and it publishes `SWEEP.json` and `SWEEP.md`
   after every call rather than at the end. It computes no rate and chooses no
   setting: §2.1 registers the choice as made from the table by a rule named
   when the choice is made, and a driver that picked the winner out of the data
   it had just produced would be making that decision on the maintainer's
   behalf.

Deliberately unchanged: `schedule_entries()`'s derivation of `slotIndex` from
the order, `slot_path()`'s `arms/<ARM>/authoring/run-NNN` layout, and the five
`SCHEDULE_KEYS` — the members a slot carries so a drift is a per-slot check and
not a claim about bookkeeping.
"""
from __future__ import annotations
import datetime
import hashlib
import itertools
import json
import os
import shutil
import stat
import subprocess
import sys
import time
from collections import Counter

# The ceremony's commands run with bytecode writing disabled (Study 012 §2.10,
# carried): set structurally, not left to the operator's environment, and
# before any harness module is imported — which means before the imports below
# and not after them (012's round 9, finding 1).
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)


def _refuse_untracked_python_sources():
    """An untracked package can shadow a reviewed module at import time —
    including the module carrying the untracked-source scan itself, which is why
    this tripwire lives in the entry file the ceremony names by path, before any
    harness import. Import resolution cannot shadow a script invoked as a file.

    Carried from Study 012 (round 8 finding 2, round 9 finding 1). It used to
    fire on the study's own tree, correctly: `design/` held untracked Python
    sources and the batch was refused until they were committed. That is
    SCAFFOLD item T3, and T3 landed — the design generators are tracked and no
    `__pycache__` survives — so the tripwire is now a guard rather than an open
    condition (round-4 finding R4-6, which found this note still describing the
    tree as dirty)."""
    import subprocess as _subprocess
    study = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tracked = set(_subprocess.run(
        ["git", "ls-files", "-z", "--", "."],
        cwd=study, capture_output=True, check=True
    ).stdout.decode("utf-8").split("\0"))
    for base, _dirs, files in os.walk(study):
        for name in files:
            if not name.endswith(".py"):
                continue
            rel = os.path.relpath(os.path.join(base, name), study)
            if rel.replace(os.sep, "/") not in tracked:
                print("refused: untracked Python source %s sits in the study "
                      "tree; the reviewed bytes are the bytes that run "
                      "(§7, Study 012's round 8 finding 2)" % rel,
                      file=sys.stderr)
                raise SystemExit(2)


def _refuse_unsafe_import_path():
    """The scan above cannot precede the head imports of the file it lives in:
    running a script BY PATH puts that script's own directory first on
    `sys.path`, so every module the head imports — `subprocess` included, which
    is the module the tripwire asks git what is tracked with — resolves from the
    directory the scan exists to police. `-P` / `PYTHONSAFEPATH=1` is the
    closure; this refusal establishes that the operator applied it (Study 012's
    round 10, finding 1, carried with its own statement of what it is worth)."""
    if not sys.flags.safe_path:
        print("refused: run this file with -P, or with PYTHONSAFEPATH=1 in the "
              "environment; invoking a script by path puts its own directory "
              "first on sys.path, so this file's head imports resolve from the "
              "very directory the untracked-source scan exists to police",
              file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    _refuse_unsafe_import_path()
    _refuse_untracked_python_sources()

# Nothing is put on the import path until the tree has been scanned — and,
# under the safe path the refusal above requires, nothing was on it before
# either, which is what makes this comment true of the whole file.
sys.path.insert(0, HERE)
import integrity  # noqa: E402
import make_manifest  # noqa: E402  (one manifest definition, not two)
import transcript_check  # noqa: E402

# §2.10 [D-23], carried: the population root is DERIVED from this file's own
# location and there is no `--slots`. A root left as an argument lets the batch
# be written into — and the population read from — any directory of the right
# shape: a copy with a slot removed, a duplicated arm, a renamed tree, every
# per-slot check still passing.
ARMS_ROOT = os.path.join(STUDY, "arms")
# NEW IN 020 (§2a.2). The pre-freeze calibration pilot runs through THIS driver
# and leaves authored slots behind, so it needs a root of its own — Study 019's
# `DEVIATIONS.md` D-2 records a freeze gate that refused any tree containing
# prior authoring, which for 020 would make the registered pilot un-runnable at
# freeze time. Keeping the pilot OUT of `arms/` is what makes
# `make_manifest.prior_authoring_problems()` permit it structurally rather than
# by an exception list, and `make_manifest.calibration_problems()` is where the
# freeze REQUIRES it. `harness/tests/test_manifest.py` asserts the two roots are
# these two and that neither gate reaches the other's tree.
#
# §7 DELTA 8 states the other half in this file: §2a.2 enumerates the registered
# differences between the pilot and the primary batch as exactly four, "so a
# fifth cannot be discovered later", and the first of them is "output under
# `calibration/<label>/`". `calibration_freeze_problems()` below permits the
# subtree, requires it, and still refuses any `results/primary-attempt-*`.
CALIBRATION_ROOT = os.path.join(STUDY, "calibration")
# NEW IN 020 (§2.1). The PRE-PILOT EFFORT SWEEP's root, and it is a THIRD root
# for the same structural reason `CALIBRATION_ROOT` is a second one — one step
# earlier in the ceremony. The sweep runs before the pilot, which runs before
# the freeze, and it leaves 27 authored slots behind. Putting them in `arms/`
# would make R10-1's `prior_authoring_problems()` refuse the freeze over runs
# the registration requires; the gate derives every path it refuses from
# `authoring_state_paths()`, which walks `slot_path()` under `ARMS_ROOT`, so a
# tree outside `arms/` is outside that gate BY CONSTRUCTION and needs no
# exclusion list. `make_manifest.SWEEP_ROOT` is the study-relative spelling and
# `harness/tests/test_sweep.py` asserts the two are one name and drives the
# occupancy gate in both directions — a sweep tree does not refuse the freeze,
# an `arms/<ARM>/authoring` tree still does.
#
# Unlike the pilot, the sweep is NOT required at the freeze: `calibration/` is
# permitted AND required because §2a registers the pilot as a precondition;
# nothing registers the sweep's TREE as one, and inventing a freeze gate no
# section states would be this driver legislating.
SWEEP_ROOT = os.path.join(STUDY, "sweeps")
SCRIPT = os.path.join(HERE, "authoring_call.sh")
DEFAULT_PINS = os.path.join(HERE, "PINS.json")
DEFAULT_CAPTURES = os.path.join(STUDY, "controls", "recapture")
DEFAULT_NEGATIVE = os.path.join(STUDY, "controls", "isolation-negative")
DEFAULT_GOLDEN = os.path.join(STUDY, "transcription", "GOLDEN-CONTEXT.json")
PROBE_PROMPT = os.path.join(STUDY, "transcription", "PROBE-PROMPT.txt")
# ROUND-10 FINDING R10-1. The production study and its ONE registry, captured
# from this file's own location at import and never patched. The harness tests
# run every calling case against a STAND-IN study — a directory of production's
# shape with the committed harness symlinked in — by patching `STUDY` and the
# roots derived from it; `CANONICAL_STUDY` is the value `STUDY` had before any
# of that, so `require_canonical_registry()` below can tell the two surfaces
# apart without a flag, an environment variable or a test hook of its own.
CANONICAL_STUDY = STUDY
CANONICAL_PINS = DEFAULT_PINS
# Change 7: the marker whose existence means a rate has been computed. The
# scorer takes `--attempt-root results/primary-attempt-001` and refuses if it
# exists (SCAFFOLD S1), so that directory is what "after a rate" names here.
ATTEMPT_ROOT = os.path.join(STUDY, "results", "primary-attempt-001")
RESULTS_DIR = os.path.join(STUDY, "results")
CALIBRATION_LEDGER_NAME = "CALIBRATION.json"
# §2.1 and §2a.2: the two registered calibration modes and the pilot's per-arm
# count. The sweep's own three settings, its per-arm count and its DERIVED call
# cap are registered once, beside the sweep mode itself (`SWEEP_SETTINGS`,
# `SWEEP_PER_ARM`, `SWEEP_CALL_CAP`) — a registered number carried under two
# names in one file is the drift `sweep_preflight()` exists to refuse.
CALIBRATION_MODES = ("sweep", "pilot")
PILOT_RUNS_PER_ARM = 12           # §2a.2: "Pilot N: 12/arm"
# §2a.2's third registered difference, stamped into every calibration record.
CALIBRATION_CITABLE = False
LEDGER_NAME = "BATCH.json"
# Change 9: a REGISTERED CONSTANT and not a `mkstemp` name. A constant is a
# destination a static reader of this file can resolve, which is what lets
# `preflight()` refuse a residue before a call is spent and what lets a harness
# test check it against the manifest's covered set.
LEDGER_TEMP_NAME = "BATCH.json.partial"
SHORTFALL_NAME = "SHORTFALL.json"
MANIFEST_NAME = "SLOT-MANIFEST.json"
# R1-5: the full transcript binding's verdict for one slot, written INSIDE the
# seal — after the wrapper's bytes and before `seal_slot()`, so it is covered by
# the manifest and the ledger chain like every other byte of the slot. It is
# evidence and not authority: the scorer recomputes the verdict from the same
# retained bytes and does not read this file for its answer, exactly as it does
# not read `REFUSAL.json` for its answer.
TRANSCRIPT_NAME = "TRANSCRIPT.json"

# The seal records EVERY entry in the slot tree. A regular file is
# `[path, byte length, sha256]`; every other entry — a symlink, a directory, a
# FIFO, a socket, a device — is `[path, NON_FILE_LENGTH, "type:<marker>"]`, by
# path and type alone, because it is not a byte range to hash. The two row
# shapes cannot collide: no file has a negative length and no sha256 hex string
# begins with `type:`.
NON_FILE_LENGTH = -1
# The slot ROOT is an entry of its own list, at the one relative path no entry
# beneath it can take: `os.path.relpath(child, slot)` is never `.`, so the
# root's row cannot be forged by planting a file in the tree.
SLOT_ROOT_ENTRY = "."
TYPE_MARKERS = (
    (stat.S_ISLNK, "symlink"),
    (stat.S_ISDIR, "directory"),
    (stat.S_ISFIFO, "fifo"),
    (stat.S_ISSOCK, "socket"),
    (stat.S_ISCHR, "char-device"),
    (stat.S_ISBLK, "block-device"),
    (stat.S_ISDOOR if hasattr(stat, "S_ISDOOR") else (lambda mode: False), "door"),
)
STDERR_TAIL = 4000

# §3.2: a golden capture is derived from at least TWO independent captures whose
# normalized pre-prompt contexts agree. One capture cannot show that a context
# reproduces. This is the floor, not a default: a smaller --min-slots refuses.
MIN_CAPTURE_SLOTS = 2
# …and the two must be two CALLS. Each member below is a piece of RAW retained
# evidence that says WHICH call produced a capture, and two capture slots that
# share any of them are one call — the normalized digests are deliberately not
# among them, because two genuinely independent calls SHOULD agree there and
# that agreement is the point of the derivation, not a defect in it.
CAPTURE_IDENTITY = (
    ("sessionSha256", "the retained transcript bytes"),
    ("sessionId", "the session id the transcript records"),
    ("callIdentity", "a digest over the call record's own start, end, working "
                     "directory and isolated home"),
)
# §6 C7's three registered outcomes. Study 012 kept this tuple in
# `score_rates.py` and named it here; this study's scorer does not exist yet and
# the driver's preflight is one of the two gates that must read it, so it is
# DEFINED here and `harness/score.py` must read it from here (change 10).
C7_OUTCOMES = ("refused", "matched", "no-context")
# §6 C7: what a retained negative-control CALL.json may not carry. The control
# runs against the operator's real environment, so every member that names or
# enumerates it is dropped before the file is written into the study.
C7_REDACTED = ("environment", "environmentValues", "home", "codexHome", "cwd",
               "isolatedHomeInventory", "operatorHomeSkillsPresent")

# Change 12: the test seam. It names a CLI when `--cli-override` does not, and
# whatever it names goes through the same digest gate.
STANDIN_ENV = "STUDY_CLI_STANDIN"


class BatchError(Exception):
    """A refusal that stops the batch before any call is made."""


# §2's registered call order, as the facts the preregistration states about its
# own table rather than as a transcription of it. W1…W3 are the cyclic rows of
# the Williams first row for three treatments; W4…W6 are those three reversed;
# the batch is eight whole blocks of the six sequences and a two-sequence tail.
# A transcribed table is six chances to mistype a letter and no way to notice —
# a derived one either attains the registered balance floor or it does not, and
# the harness test checks the expansion's own counters and not this code.
ARMS = ("A", "B", "C")
WILLIAMS_FIRST_ROW = ("A", "B", "C")
POSITIONS = len(ARMS)
SEQUENCES = 2 * POSITIONS  # six: the three cyclic rows and those three reversed
# §7 DELTA 7: THE SCHEDULE IS RE-DERIVED AT THE REGISTERED ROUND COUNT, AND
# THIS FILE HOLDS NO ROUND COUNT OF ITS OWN.
#
# 019 hard-coded `SEQUENCES = 6`, `ROUNDS = 50`, `RUNS_PER_ARM = 50`,
# `REGISTERED_SLOTS = 150` and a two-element `TAIL`, and `derive_order()`'s
# docstring recorded the registered floor (1, 1) as the cached answer to a
# search AT 50 ROUNDS. §2 says it plainly: "at any other round count that
# assertion is wrong by construction". 020's N is an OUTPUT of §2.1's pre-pilot
# sweep and does not exist yet, so a literal here would be a number this file
# invented — which is precisely the defect the delta names.
#
# What is registered instead is the DERIVATION. The round count, the block
# order, the tail and the attained spreads are read from `harness/PINS.json`'s
# `batch` member; `derive_order(rounds)` is the authority that produced them and
# is re-run by `tests/test_schedule.py` at whatever round count the registry
# names; and `schedule()` asserts the expansion attains the spreads the registry
# PUBLISHES rather than the pair (1, 1) that happens to be the floor at 50.
#
# Re-pinning at the swept N is therefore a registry edit plus
# `batch.py derive-schedule --rounds N`, and no constant in this file moves.
def _registered_batch_shape(path: str = None) -> dict:
    """§2's `batch` member, read once, as the shape every expansion here is
    over. Refuses rather than defaulting: a driver that invents a round count
    when the registry has none is the 019 defect with a fallback in front of
    it."""
    where = path or os.path.join(HERE, "PINS.json")
    try:
        with open(where, "rb") as handle:
            registry = json.loads(handle.read().decode("utf-8"))
    except (IOError, OSError, ValueError) as error:
        raise BatchError(
            "harness/PINS.json could not be read (%s): §2 registers the call "
            "order, its round count and its slot count as REGISTRY members, "
            "and this driver holds no copy of them to fall back to" % error)
    block = registry.get("batch")
    if not isinstance(block, dict):
        raise BatchError(
            "harness/PINS.json registers no batch member: §2's call order, its "
            "N and its slot count are registry members")
    order = block.get("order")
    if not isinstance(order, dict):
        raise BatchError("harness/PINS.json registers no batch.order")
    rounds = block.get("n")
    if not isinstance(rounds, int) or rounds < 1:
        raise BatchError(
            "harness/PINS.json registers batch.n = %r: §2's round count is a "
            "positive integer and §2.1 registers it as an output of the "
            "pre-pilot effort sweep. Until the sweep has run and the registry "
            "has been re-pinned there is no order to expand" % (rounds,))
    blocks, tail_length = divmod(rounds, SEQUENCES)
    return {
        "rounds": rounds,
        "blocks": blocks,
        "tailLength": tail_length,
        "blockOrder": tuple(order.get("blockOrder") or ()),
        "tail": tuple(order.get("tail") or ()),
        # Delta 7's "with the new attained position spread published": the
        # spreads are registry members, so `schedule()` asserts against the
        # PUBLISHED pair at this N rather than against 019's (1, 1).
        "positionSpread": order.get("positionSpread"),
        "transitionSpread": order.get("transitionSpread"),
    }


REGISTERED_BATCH_SHAPE = _registered_batch_shape()
ROUNDS = REGISTERED_BATCH_SHAPE["rounds"]
BLOCKS = REGISTERED_BATCH_SHAPE["blocks"]
TAIL_LENGTH = REGISTERED_BATCH_SHAPE["tailLength"]
BLOCK_ORDER = REGISTERED_BATCH_SHAPE["blockOrder"]
TAIL = REGISTERED_BATCH_SHAPE["tail"]
REGISTERED_POSITION_SPREAD = REGISTERED_BATCH_SHAPE["positionSpread"]
REGISTERED_TRANSITION_SPREAD = REGISTERED_BATCH_SHAPE["transitionSpread"]
RUNS_PER_ARM = ROUNDS                            # one slot per arm per round
REGISTERED_SLOTS = ROUNDS * POSITIONS
# The members that make a slot a slot of the registered order. The ledger
# carries them per record and the driver compares them position by position
# against the expansion.
SCHEDULE_KEYS = ("globalIndex", "round", "position", "arm", "slotIndex")

# The wrapper takes five required positional arguments, and the golden-capture
# probes are made under no arm: they answer the registered probe prompt, which
# is arm-independent by construction and is why ONE recapture serves all three
# arms. The wrapper's registered interface spells that case `none`, refuses
# `PROMPT_KIND=probe` under any other arm id, and stamps `arm: null`.
# Capture slots are never batch slots and enter no denominator.
PROBE_ARM = "none"

# §2 "Batch shape": the per-call timeout ceiling, in seconds. It is a property
# of the APPARATUS — the bound past which a call is abandoned — and never a
# statement about what the author produced.
CALL_TIMEOUT_SECONDS = 2700
# The grace between TERM and KILL, so a terminated call still flushes its
# transcript before the wrapper seals what it has.
TIMEOUT_KILL_AFTER_SECONDS = 60

# The wrapper's exit statuses, and what each one is. Status 12 is this study's
# addition (change 3 above); 0, 1, 10 and 11 are Study 012's, unchanged. Status
# 13 is round 1's (R1-4).
#
# **1 and 13 are two statuses because they are two events** (R1-4). The wrapper
# runs under `set -euo pipefail`, and a failure in any of its three POST-CALL
# stages — the completion extraction, the CALL.json write, the context digests —
# used to kill the shell with the helper's own status 1, which this table read as
# "a pre-call refusal; nothing was called". The call HAD been made, the slot HAD
# been left behind, and the code the driver wrote onto it said the opposite. The
# wrapper now sets a phase flag before the call and traps every unexpected
# post-call failure to status 13, so the two events cannot wear one status again.
WRAPPER_EXIT_MEANINGS = {
    0: ("complete", "the call exited 0 and the slot is complete"),
    1: ("preflight-refused", "a pre-call refusal; the model was never invoked, "
                             "and any slot left behind is empty"),
    10: ("call-nonzero-exit", "the call exited non-zero; the slot is retained "
                              "without completion.txt"),
    11: ("slot-shape", "the run produced other than exactly one new session; "
                       "slot retained"),
    12: ("call-timeout", "the call reached the registered %d s ceiling and was "
                         "terminated; slot retained" % CALL_TIMEOUT_SECONDS),
    13: ("post-call-failure", "a post-call wrapper stage failed after the call "
                              "returned; slot retained, and whatever the stage "
                              "had not written is missing"),
}

# Change 8: the driver's status -> refusal-code map, DERIVED from the table
# above rather than written out beside it. Study 012 kept two tables and had no
# third branch to keep in step; this study's status 12 is exactly the case where
# two hand-written tables drift, so there is one. Status 0 is the slot's success
# and carries no code.
WRAPPER_CODES = {status: (None if code == "complete" else code)
                 for status, (code, _gloss) in WRAPPER_EXIT_MEANINGS.items()}

# §1a's population rule, as a partition rather than as prose. The left column is
# the code the harness emits; the right column is the phrase §1a registers for
# it, verbatim, so `harness/tests/test_partition.py` can diff the two lists
# against the registration rather than against another copy of themselves.
#
# The partition is EXHAUSTIVE over the failure codes §1a names and DISJOINT by
# construction: `CODE_PARTITION` is built from the two tuples below, and a code
# appearing in both is a KeyError at import rather than a silent reclassification.
APPARATUS_CODES = (
    ("slot-shape", "slot shape"),
    ("call-nonzero-exit", "call nonzero-exit"),
    ("call-timeout", "call timeout at the registered ceiling"),
    # R1-4: both wrapper statuses that used to fall OUTSIDE this partition and
    # therefore into every rate's denominator. A pre-call refusal spent nothing
    # and a post-call stage failure lost a byte the slot needed; neither is
    # anything the author emitted.
    ("preflight-refused", "pre-call refusal"),
    ("post-call-failure", "post-call wrapper failure"),
    ("golden-context-mismatch", "golden-context mismatch"),
    ("binary-digest-mismatch", "binary digest mismatch"),
    # ROUND-10 FINDING R10-1, second half. The wrapper stamps the registry every
    # call was made under into `CALL.json` (`pinsSha256`), and the sentence that
    # excused `--pins` claimed the scorer refused any slot whose stamp differed
    # — under this very name, "registry-mismatch". Nothing named it and nothing
    # checked it: `score.py` recorded the canonical registry's digest in
    # ATTEMPT.json and compared it with nothing. The code is registered here now
    # and `score.read_slot()` returns it, so a slot authored under a substitute
    # registry is pipeline-invalid rather than an ordinary authoring run. It is
    # APPARATUS because it is a fact about which bytes the apparatus ran under
    # and never a statement about what the author emitted — the same reason
    # `golden-context-mismatch` above is apparatus.
    ("registry-mismatch", "registry mismatch"),
    ("transcript-refused", "transcript refusal"),
)
# The SEVEN ADMISSION codes: what `admit()` reads off the retained artifact.
# `e4lib/admit.py`'s DROP_ORDER is this list in the order that module decides in,
# and a test diffs the two — so this tuple stays the admission surface and does
# not grow a member no `admit()` branch can return.
#
# STUDY 020, §7 DELTA 3: the seventh is `presence-idiom-unsound` (§3.2), and it
# is registered in this table WHETHER OR NOT IT EVER FIRES — §5's E2 entry says
# so in those words, so the row is published at count zero while §3.2's
# GATE(pre-freeze) power analysis is open rather than appearing only if the
# guard is activated. A table whose rows depend on the outcome is a table that
# reports a different partition in each branch.
AUTHORING_CODES = (
    ("no-marker-block", "no extractable marker block"),
    ("unparseable-artifact", "unparseable artifact"),
    ("schema-invalid-pack", "schema-invalid pack"),
    ("opa-check-failed", "opa check failure"),
    ("v0-syntax", "v0-syntax"),
    ("unreadable-output-shape", "unreadable output shape"),
    # NEW IN 020 (§1a's table, §3.2, ruling M-14). Study 019 had six admission
    # codes; this is the seventh and it is an AUTHORING outcome like the other
    # six — valid, counted, and scoring zero on every endpoint it reaches. It is
    # emitted by `e4lib/presence_idiom.py` over a policy the pinned binary has
    # already ACCEPTED, which is why it cannot be mistaken for a compile
    # failure, and it is registered here so that a code the scorer can emit is a
    # code the population rule names — R1-4's lesson, applied to a new code
    # rather than rediscovered by it.
    ("presence-idiom-unsound", "presence-idiom guard fires"),
)

# §1a's table has a THIRD column — "arms it can reach" — and Study 019's
# partition carried only two. It is registered here because 020 adds a code that
# is B/C-only (§11.11's ceiling), and a partition that cannot say so cannot be
# diffed against the registration that does.
#
# `e4lib/admit.py`'s `ARM_REACHABLE_CODES` is the ENFORCING copy (it refuses an
# arm-structural leak at the moment a code is returned); this is the copy
# `harness/tests/test_partition.py` diffs against §1a's prose, and the same test
# requires the two to agree, so neither can drift alone.
AUTHORING_CODE_ARMS = {
    "no-marker-block": ("A", "B", "C"),
    "unparseable-artifact": ("A", "B", "C"),
    "schema-invalid-pack": ("A",),
    "opa-check-failed": ("B", "C"),
    "v0-syntax": ("B", "C"),
    "unreadable-output-shape": ("A", "B", "C"),
    "presence-idiom-unsound": ("B", "C"),
}
# R1-5's authoring outcome, which is NOT an admission code: it is read off the
# retained TRANSCRIPT rather than off the artifact, by
# `transcript_check.classify()`, and it is what an author using a tool or taking
# a turn after the registered prompt scores. §1a registers it in its own
# sentence for exactly that reason, and `harness/tests/test_partition.py` diffs
# that sentence against this tuple.
AUTHORING_PROTOCOL_CODES = (
    ("author-protocol-violation", "author protocol violation"),
)
AUTHORING_CODE_ARMS["author-protocol-violation"] = ("A", "B", "C")

# Checked at import, in both directions, for the reason `_partition()` is built
# rather than written out: an authoring code with no reachability row, or a
# reachability row for a code no tuple names, is a KeyError here and not a
# column a published E2 table quietly loses.
for _code, _phrase in AUTHORING_CODES + AUTHORING_PROTOCOL_CODES:
    if _code not in AUTHORING_CODE_ARMS:
        raise BatchError(
            "the authoring code %r has no `arms it can reach` row: §1a's table "
            "has three columns and a partition that carries two cannot be "
            "diffed against it" % _code)
for _code in AUTHORING_CODE_ARMS:
    if _code not in dict(AUTHORING_CODES + AUTHORING_PROTOCOL_CODES):
        raise BatchError(
            "%r has a reachability row and is not a registered authoring code"
            % _code)
del _code, _phrase


def _partition() -> dict:
    """{code: ("apparatus"|"authoring", the phrase §1a registers)}.

    Built rather than written out, so the tuples above are the only place a code
    is named and a code that drifted into two sides refuses at import."""
    table = {}
    for side, rows in (("apparatus", APPARATUS_CODES),
                       ("authoring", AUTHORING_CODES),
                       ("authoring", AUTHORING_PROTOCOL_CODES)):
        for code, phrase in rows:
            if code in table:
                raise BatchError(
                    "the code %r is registered on both sides of §1a's "
                    "partition: pipeline-invalid and authoring outcomes are "
                    "disjoint by construction" % code)
            table[code] = (side, phrase)
    return table


CODE_PARTITION = _partition()

# EXHAUSTIVE, checked at import (R1-4). The partition used to be exhaustive over
# the codes §1a's prose names and silent about the two the driver could actually
# emit; `population()` then excluded only codes it recognised, so an unnamed code
# was not an error but a DENOMINATOR MEMBER. Every value this table can yield is
# now a key of the partition, at import, before any batch can run.
for _status, _code in WRAPPER_CODES.items():
    if _code is not None and _code not in CODE_PARTITION:
        raise BatchError(
            "wrapper exit %d maps to the code %r and §1a's partition does not "
            "name it: a code outside the partition is a run outside both sides "
            "of the population rule, which is a silent denominator change"
            % (_status, _code))
del _status, _code


def wrapper_code(status: int):
    """The refusal code for a wrapper exit status, or None for a complete slot —
    **fail-closed on anything else** (R1-4).

    `WRAPPER_CODES.get(status, "wrapper-error")` was the old reading, and
    `wrapper-error` was in no partition and in no registered table: the driver
    materialized, sealed and ledgered such a slot, and the scorer — which
    excludes only codes it recognises as apparatus — put it in the denominator as
    an ordinary authoring run. A status this wrapper does not register is
    evidence that the process at the end of `SCRIPT` is not the wrapper this
    study registered, so the batch stops rather than filing one more slot under a
    code nobody defined. Every remaining slot would carry the same defect, and
    the operator adjudicates it in DEVIATIONS.md."""
    if not isinstance(status, int) or isinstance(status, bool) \
            or status not in WRAPPER_CODES:
        raise BatchError(
            "the wrapper exited with the status %r and §2 registers %s: an "
            "unregistered status is not a refusal code, and a slot cannot be "
            "filed under a code no partition names. The batch stops here; record "
            "the cause in DEVIATIONS.md"
            % (status, ", ".join(str(known) for known in sorted(WRAPPER_CODES))))
    return WRAPPER_CODES[status]


# --- bytes in, bytes out ----------------------------------------------------

def _load_json(path: str):
    """Duplicate-key-rejecting JSON. Study 012 reached this through
    `score_rates._refuse_duplicate_keys`; the module name is the whole of the
    change, and `transcript_check`'s raises `ValueError` exactly as 012's did,
    so every `except (ValueError, OSError)` below keeps the behaviour it was
    ported with."""
    with open(path, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"),
                          object_pairs_hook=transcript_check._refuse_duplicate_keys)


def _digest_text(text: str) -> str:
    """sha256 of a small in-memory string; the capture identity digest."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _digest(path: str) -> str:
    with open(path, "rb") as handle:
        return "sha256:" + hashlib.sha256(handle.read()).hexdigest()


def _matches(actual: str, pinned) -> bool:
    """One computed digest against one registry pin. `integrity.bare()` is this
    study's single rule for reading a digest written with or without its
    `sha256:` prefix, and this file calls it rather than adding a second rule
    that could disagree with the module every other artifact is checked by."""
    return integrity.bare(actual) == integrity.bare(pinned)


def _canonical(body) -> bytes:
    """The serialization the ledger's hash chain is taken over: JSON with sorted
    keys and no insignificant whitespace. §2.9 registers a chain over ledger
    records, and a record is a structure and not a file — so the bytes being
    digested have to be defined somewhere, once, in a form the scorer can
    reproduce exactly."""
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _write_json(path: str, body: dict) -> None:
    with open(path, "wb") as handle:
        handle.write((json.dumps(body, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def _write_json_atomic(path: str, temp_path: str, body: dict) -> None:
    """The same bytes, written so that no reader ever sees half of them: a
    temporary file in the SAME directory, flushed and fsynced, then
    `os.replace`, then the directory entry fsynced too.

    `BATCH.json` is rewritten in full after every slot, and a plain write
    truncates before it writes — so a kill between those two leaves a truncated
    ledger and the batch's only record of every slot before it is gone.
    `os.replace` is atomic within a filesystem; the same-directory temporary is
    what makes that true, and the two fsyncs are what make it survive the other
    half of a crash.

    `temp_path` is the caller's REGISTERED CONSTANT (`arms/BATCH.json.partial`),
    not a random name, and `O_EXCL` turns a residue into a named refusal on the
    next run rather than an unread note. Study 012 needed the constant so the
    path could be an exclusion entry; here it is needed so `preflight()` can
    refuse the residue before a call is spent and so a harness test can check
    the path against the manifest at all (change 9)."""
    directory = os.path.dirname(path) or "."
    try:
        handle_fd = os.open(temp_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        raise BatchError(
            "%s already exists and this run did not create it: the atomic write "
            "never overwrites a temporary it did not open. `preflight()` refuses "
            "this before a call is spent; reaching it here means the residue "
            "appeared during the batch. Record it in DEVIATIONS.md and remove it"
            % os.path.relpath(temp_path, STUDY))
    try:
        with os.fdopen(handle_fd, "wb") as handle:
            handle.write((json.dumps(body, indent=2, sort_keys=True)
                          + "\n").encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except BaseException:
        if os.path.lexists(temp_path):
            os.unlink(temp_path)
        raise
    directory_fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def williams(first_row=WILLIAMS_FIRST_ROW) -> dict:
    """§2's six registered sequences W1…W6, derived.

    W1…W3 are the cyclic rows of the Williams first row `A, B, C` — each row the
    one before it with every arm advanced one step through A→B→C→A — and W4…W6
    are those three rows reversed. Over the six, each arm holds each of the
    three positions exactly twice and each of the six ordered pairs X→Y is
    adjacent exactly twice.

    `first_row` is an argument only so that the REGISTRY's own first row can be
    expanded by this same construction and compared with the expansion this file
    derives; every other caller takes the registered default and the two are the
    same table or nothing runs."""
    if sorted(first_row) != sorted(ARMS):
        raise BatchError("§2's Williams first row is a permutation of %r; %r is not"
                         % (list(ARMS), list(first_row)))
    rows = {}
    for step in range(POSITIONS):
        rows["W%d" % (step + 1)] = tuple(
            ARMS[(ARMS.index(arm) + step) % POSITIONS] for arm in first_row)
        rows["W%d" % (step + 1 + POSITIONS)] = tuple(
            reversed(rows["W%d" % (step + 1)]))
    return rows


def round_order(block=BLOCK_ORDER, tail=TAIL, blocks=None, rounds=None) -> tuple:
    """The registered round names: the block order `blocks` times, then the tail.

    A permutation check on both, for the same reason Study 012 checked its three
    blocks: every sequence holds every arm once, so a block that ran W4 twice
    and W3 never still gives the registered slots per arm and destroys the
    transition balance the registration is about.

    §7 delta 7: `blocks` and `rounds` default to the REGISTRY's shape and are
    arguments so `derive_order()` can search at a round count the registry does
    not yet name. No number in this function is this file's own."""
    blocks = BLOCKS if blocks is None else blocks
    rounds = ROUNDS if rounds is None else rounds
    rows = williams()
    if not all(isinstance(name, str) for name in block) \
            or sorted(block) != sorted(rows):
        raise BatchError("the registered block order is %r, which is not a "
                         "permutation of W1…W%d" % (list(block), SEQUENCES))
    if len(tail) != len(set(tail)) or any(name not in rows for name in tail):
        raise BatchError("the registered tail is %r, which is not a sequence of "
                         "distinct members of W1…W%d" % (list(tail), SEQUENCES))
    if len(block) * blocks + len(tail) != rounds:
        raise BatchError("%d blocks of %d and a tail of %d is %d rounds; the "
                         "registration is %d"
                         % (blocks, len(block), len(tail),
                            len(block) * blocks + len(tail), rounds))
    return tuple(list(block) * blocks + list(tail))


def expand(order) -> list:
    """[(globalIndex, round, position, arm)] for a sequence of round names."""
    rows = williams()
    slots, index = [], 0
    for round_index, name in enumerate(order, 1):
        for position, arm in enumerate(rows[name], 1):
            index += 1
            slots.append((index, round_index, position, arm))
    return slots


def balance(slots) -> dict:
    """The counters the registered order is chosen by and the harness test
    re-derives: per-arm slots, per-(arm, position) counts, and the directed
    transition counts split into within-round, round-boundary and total.

    Nothing here is a threshold. The spreads are read off these counters by
    `derive_order()` and asserted by `harness/tests/test_schedule.py`, which is
    what keeps "carryover-balanced" arithmetic rather than adjectival."""
    per_arm = Counter(arm for _, _, _, arm in slots)
    positions = Counter((arm, position) for _, _, position, arm in slots)
    within, boundary, total = Counter(), Counter(), Counter()
    for left, right in zip(slots, slots[1:]):
        pair = (left[3], right[3])
        total[pair] += 1
        (within if left[1] == right[1] else boundary)[pair] += 1
    return {"perArm": per_arm, "positions": positions, "within": within,
            "boundary": boundary, "total": total,
            "positionSpread": max(positions.values()) - min(positions.values()),
            "transitionSpread": max(total.values()) - min(total.values()),
            "selfSuccessions": sum(count for (left, right), count in total.items()
                                   if left == right)}


def derive_order(blocks=None, tail_length=None, rounds=None):
    """The registered order, DERIVED at a ROUND COUNT: the search `BLOCK_ORDER`
    and `TAIL` are the answer to, and the authority the registry answers to.

    Over every one of the 720 orderings of W1…W6 and every one of the ordered
    tails of the required length, keep the orders in which no arm ever
    immediately follows itself, and return the lexicographically-least (by
    W-index) of those that minimize the pair (position spread, transition
    spread).

    **§7 DELTA 7: THE FLOOR IS REPORTED, NOT ASSERTED.** 019's docstring
    recorded "(1, 1)" as the registered floor — true at 50 rounds and wrong by
    construction at any other N, because exact balance depends on arithmetic
    that N decides: whether the slots divide over the three positions and
    whether the transitions divide over the six ordered pairs. This function
    therefore RETURNS the minimum it found at the round count it was asked
    about, and `tests/test_schedule.py` requires the registry's published
    spreads to equal that minimum. Neither the code nor the registry states a
    floor; the search does, at whatever N is registered.

    `rounds` defaults to the registry's; `blocks`/`tail_length` are derived from
    it, so the three cannot disagree.

    Deliberately not run at import: it is a second of work per round count and
    the driver plans the same order every time. The registry is the cache; this
    is the authority."""
    rounds = ROUNDS if rounds is None else rounds
    if blocks is None:
        blocks = rounds // SEQUENCES
    if tail_length is None:
        tail_length = rounds - blocks * SEQUENCES
    if tail_length < 0 or tail_length >= SEQUENCES + 1:
        raise BatchError(
            "%d rounds is %d whole blocks of %d and a tail of %d: a tail is a "
            "PREFIX of one block, so a tail at or above %d is another whole "
            "block and the shape is not derived"
            % (rounds, blocks, SEQUENCES, tail_length, SEQUENCES))
    rows = williams()
    names = tuple(sorted(rows, key=lambda name: int(name[1:])))
    best = None
    for permutation in itertools.permutations(names):
        for tail in itertools.permutations(names, tail_length):
            slots = expand(list(permutation) * blocks + list(tail))
            profile = balance(slots)
            if profile["selfSuccessions"]:
                continue
            key = ((profile["positionSpread"], profile["transitionSpread"]),
                   permutation, tail)
            if best is None or key < best:
                best = key
    if best is None:
        raise BatchError("no order of W1…W%d over %d rounds avoids an arm "
                         "following itself" % (SEQUENCES, rounds))
    (spreads, permutation, tail) = best
    return {"rounds": rounds, "blocks": blocks, "tailLength": tail_length,
            "blockOrder": permutation, "tail": tail,
            "positionSpread": spreads[0], "transitionSpread": spreads[1],
            "slots": rounds * POSITIONS, "runsPerArm": rounds}


def schedule(block=BLOCK_ORDER, tail=TAIL) -> list:
    """The registered call order's slots, expanded deterministically from the
    REGISTRY's table: `[(globalIndex, round, position, arm)]`, global index
    1…`REGISTERED_SLOTS`, round 1…`ROUNDS`, within-round position 1…3.

    The arms are interleaved, not blocked, because blocked execution would
    confound the arm with the drift across the batch; the order is
    carryover-balanced rather than merely position-balanced, because a schedule
    that balances position alone leaves an arm following one particular
    predecessor almost always, and provider-side state carried from one call to
    the next is exactly what §8 admits this design cannot exclude.

    The harness test re-derives the same expansion and asserts this function
    equals it, so the driver cannot drift from the registration while the
    published balance properties still pass.

    `block` and `tail` default to the registered order and are arguments for one
    caller only: the registry check expands `harness/PINS.json`'s own
    `batch.order` through this same function and requires the result to equal
    the default expansion, so the registry and the driver are one order rather
    than two spellings that happen to agree."""
    slots = expand(round_order(block, tail))
    profile = balance(slots)
    # Not a formality: this is the one place the expansion's shape is asserted
    # against the registered numbers, and a mistyped block order would be caught
    # here rather than at slot 150.
    if len(slots) != REGISTERED_SLOTS \
            or sorted(profile["perArm"].values()) != [RUNS_PER_ARM] * POSITIONS:
        raise BatchError(
            "the expanded call order is %d slots with per-arm counts %r: §2 "
            "registers %d slots over %d rounds, %d per arm"
            % (len(slots), dict(profile["perArm"]), REGISTERED_SLOTS, ROUNDS,
               RUNS_PER_ARM))
    # …and this is the one place the BALANCE is asserted rather than described.
    #
    # §7 DELTA 7: AGAINST THE REGISTRY'S PUBLISHED SPREADS, NOT AGAINST (1, 1).
    # 019 asserted `> 1` here, which is the arithmetic floor for three arms over
    # FIFTY rounds and is wrong by construction at any other N — at a round
    # count that divides evenly the floor is (0, 0) and a drifted order
    # attaining (1, 1) would pass. The registry publishes the attained spreads
    # `derive_order()` found at the registered round count, the test re-runs
    # that search, and this asserts EQUALITY: a schedule that drifted would have
    # to attain exactly the published pair, and one that is better than the
    # published pair means the registry is stale and refuses too.
    if REGISTERED_POSITION_SPREAD is None \
            or REGISTERED_TRANSITION_SPREAD is None:
        raise BatchError(
            "harness/PINS.json's batch.order publishes no positionSpread or "
            "transitionSpread: §2 registers the attained spread as part of the "
            "order (§7 delta 7, 'with the new attained position spread "
            "published'), and an order whose balance is not published is an "
            "order whose balance nothing checks")
    if profile["selfSuccessions"] \
            or profile["positionSpread"] != REGISTERED_POSITION_SPREAD \
            or profile["transitionSpread"] != REGISTERED_TRANSITION_SPREAD:
        raise BatchError(
            "the expanded call order has %d self-successions, position spread "
            "%d and transition spread %d; the registry publishes none, %r and "
            "%r at %d rounds"
            % (profile["selfSuccessions"], profile["positionSpread"],
               profile["transitionSpread"], REGISTERED_POSITION_SPREAD,
               REGISTERED_TRANSITION_SPREAD, ROUNDS))
    return slots


def schedule_entries() -> list:
    """`schedule()` with each slot's per-arm slot index attached: the five
    members registered per ledger record and per `CALL.json`.

    `slotIndex` is derived from the order and not stored in it — it is the count
    of that arm's slots so far — which is what makes "exactly the contiguous
    range 1…count_X, derived from that prefix" true of any prefix, complete or
    not, without reference to a round number."""
    entries, seen = [], {arm: 0 for arm in ARMS}
    for global_index, round_index, position, arm in schedule():
        seen[arm] += 1
        entries.append({"globalIndex": global_index, "round": round_index,
                        "position": position, "arm": arm,
                        "slotIndex": seen[arm]})
    return entries


def slot_path(entry: dict) -> str:
    """`arms/<ARM>/authoring/run-NNN` — the slot root is the ARM's, and NNN is
    that arm's own slot index zero-padded to three digits, so within an arm the
    run order IS the on-disk order and a drift read is a sort, not a join."""
    return os.path.join(ARMS_ROOT, entry["arm"], "authoring",
                        "run-%03d" % entry["slotIndex"])


def plan(runs: int, start: int, slots_dir: str, stem: str = "run") -> list:
    """The slot paths a CAPTURE attempt will create, in order — `capture-NNN`
    with a three-digit index, in one flat attempt directory.

    The batch's own slots do not come from here: they come from
    `schedule_entries()` and `slot_path()`, because a slot's index is its arm's
    and its order is the registered order's (§2)."""
    return [os.path.join(slots_dir, "%s-%03d" % (stem, index))
            for index in range(start, start + runs)]


# --- carried from Study 012's harness/score_rates.py ------------------------
# (sha256 f4d4463f081439f147a341bb38d8a6b709b3860f73f6f4e524234a180ec23336 —
# 012's own destination digest for that file. Change 10: this study's scorer
# does not exist yet and these four are preconditions of the CALLS, so they live
# here and `harness/score.py` reads them from here.)

def session_identity(session_path: str):
    """The session id the transcript records for itself, or None.

    `session_meta` is metadata the transcript checker skips — no conversation
    content reaches the model through it — but it is exactly the right evidence
    here: it names the session, and two slots naming one session are one call
    however their directories are named."""
    with open(session_path, "rb") as handle:
        for raw in handle:
            raw = raw.strip()
            if not raw:
                continue
            entry = json.loads(raw.decode("utf-8"),
                               object_pairs_hook=transcript_check._refuse_duplicate_keys)
            if not isinstance(entry, dict) or entry.get("type") != "session_meta":
                continue
            payload = entry.get("payload")
            if isinstance(payload, dict):
                for key in ("id", "session_id"):
                    if isinstance(payload.get(key), str) and payload[key]:
                        return payload[key]
    return None


def collect_slots(root: str) -> tuple:
    """(slot paths in run order, unexpected entry names) for one arm's authoring
    tree. A slot is an entry named `run-<digits>` — collected WHATEVER ITS TYPE,
    a directory, a symlink, a FIFO or a regular file, because the NAME is what
    claims the index and the name is what has to answer for it. Skipping the
    ones that are not directories punches a hole in the indices and refuses the
    whole scoring, where the registration wants the entry named and scored.

    An ABSENT root is an empty population, not a refusal: the driver creates
    `arms/<X>/authoring/` with that arm's FIRST slot, so an arm the registered
    prefix has not reached yet has no root at all. `lexists`, not `exists`: a
    DANGLING symlink at the authoring root is something that was created and
    broken, not an arm never reached, and it still refuses."""
    if not os.path.isdir(root):
        if os.path.lexists(root):
            raise BatchError("%s is not a directory" % root)
        return [], []
    slots, unexpected = [], []
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        parts = name.split("-", 1)
        if len(parts) == 2 and parts[0] == "run" and parts[1].isdigit():
            slots.append(path)
        else:
            unexpected.append(name)
    return slots, unexpected


def c7_record_shape_problems(verdict: dict) -> list:
    """The members of §6 C7's verdict that the WRITER always writes, checked
    from one place by both gates.

    Three members, and only three: the ones whose SHAPE is fixed on every path
    and is checkable without a string diff over a registered paragraph.
    `registeredOutcomes`, equality against the one constant the writer, this
    preflight and the scorer all read; `deletedByCode`, present and a str->str
    object and deliberately NOT required non-empty, because the loop that fills
    it records only files that exist and the `no-context` case legitimately has
    none; `wrapperExit`, an int with bool excluded.

    It runs in ONE direction: each predicate is a necessary condition of the
    writer's output, so a record that FAILS one provably is not this driver's —
    and a record that passes all three has proved nothing about where it came
    from."""
    problems = []
    recorded = verdict.get("registeredOutcomes")
    if recorded != list(C7_OUTCOMES):
        problems.append("records registeredOutcomes %r and §6 C7 registers %r"
                        % (recorded, list(C7_OUTCOMES)))
    deleted = verdict.get("deletedByCode")
    if not isinstance(deleted, dict) or not all(
            isinstance(name, str) and isinstance(value, str)
            for name, value in deleted.items()):
        problems.append(
            "records deletedByCode %r and the driver writes a name-to-digest "
            "object there — empty when the call left nothing to digest and "
            "delete, which is the no-context case" % (deleted,))
    status = verdict.get("wrapperExit")
    if not isinstance(status, int) or isinstance(status, bool):
        problems.append("records wrapperExit %r and the wrapper's exit status "
                        "is an integer" % (status,))
    return problems


# --- lawful destinations (change 11) ----------------------------------------

def _object_id(path: str):
    try:
        info = os.stat(path)
    except OSError:
        return None
    return (info.st_dev, info.st_ino)


def _identity_chain(path: str) -> set:
    """Every (device, inode) up a resolved path's ancestor chain."""
    chain, current = set(), os.path.normpath(os.path.realpath(path))
    while True:
        identity = _object_id(current)
        if identity is not None:
            chain.add(identity)
        parent = os.path.dirname(current)
        if parent == current:
            return chain
        current = parent


def _identity_overlap(study: str, target: str) -> bool:
    """True when the two trees share a directory OBJECT even though their
    resolved names differ — a bind mount, a host re-exposure, a symlink to an
    ancestor."""
    study_id, target_id = _object_id(study), _object_id(target)
    if study_id is not None and study_id in _identity_chain(target):
        return True
    return target_id is not None and target_id in _identity_chain(study)


def covered_by_manifest(relative: str) -> bool:
    """Would writing at this study-relative path add — or move — a byte
    `harness/STUDY-MANIFEST.sha256` covers?

    Computed from `make_manifest`'s own constants and not from a second list.
    The covered set is a registered document set plus exact globs over
    `harness/` and `harness/tests/`, so the question has two halves: the path is
    itself a covered entry, or it lies inside a directory whose glob would
    swallow whatever is written beneath it."""
    normalized = relative.replace(os.sep, "/").strip("/")
    if not normalized:
        return True                      # the study root itself
    if normalized in make_manifest.REGISTERED_DOCUMENTS:
        return True
    if normalized in make_manifest.manifest_entries():
        return True
    first = normalized.split("/")[0]
    return first == "harness"


def require_lawful_destination(path: str, what: str, is_file: bool = False) -> None:
    """Any path this harness is asked to WRITE is outside the study, or inside
    it at a place the study manifest does not cover (§7, ADR 0004).

    This introduces no new rule: the manifest is what the final review round
    attests, and an act that moves a covered byte answers that attestation with
    another round. What it adds is a place where the code enforces it for a
    destination the OPERATOR names — `capture --captures DIR`, `capture-golden
    --out PATH`, `capture-isolation-negative --out DIR` — which Study 012 found
    (its rounds 17 and 18) were held by README prose and by nothing else.

    FAILS CLOSED ON WHAT IT CANNOT DECIDE. A target lexically outside the study
    that nonetheless shares a directory OBJECT with it has no computable
    study-relative path, so its coverage cannot be decided and it refuses.

    WHAT IT DOES NOT DO: it gates the ROOT a writer is handed, not what the
    writer joins onto it; and it is a rule about covered bytes and not about
    good taste — `--out controls/recapture/x.json` is accepted, because ADR
    0004's exact set covers no byte under `controls/`."""
    study = os.path.normpath(os.path.realpath(STUDY))
    target = os.path.normpath(os.path.realpath(path))
    if target != study and not target.startswith(study + os.sep):
        if _identity_overlap(study, target):
            raise BatchError(
                "%s %s (%s) is outside the study by name and shares a directory "
                "with it by filesystem identity (device and inode, up each "
                "ancestor chain): a second mount name for the study, or for a "
                "tree containing it, has no study-relative path, so whether the "
                "bytes written there are manifest-covered cannot be decided. "
                "This refuses rather than guessing (§7)" % (what, path, target))
        return                                    # genuinely outside the study
    relative = "" if target == study else os.path.relpath(target, study)
    if not covered_by_manifest(relative):
        return
    raise BatchError(
        "%s %s resolves to %s inside the study tree, which the ADR 0004 exact-set "
        "manifest covers (or would cover, for anything written beneath it): the "
        "act that writes there moves the manifest the final review round "
        "attested. Name a directory outside the study, or one inside it that the "
        "manifest does not reach — `controls/`, `transcription/`, `arms/` and "
        "`results/` are covered by no entry (§7, ADR 0004)"
        % (what, path, relative or "."))


# --- D1: the registry, and the ported bytes ---------------------------------

def arm_prompt(pins: dict, arm: str) -> tuple:
    """(path, pinned sha256) of one arm's registered `PROMPT.txt`.

    The path is structural and the digest is pinned, which is how this study
    treats every arm artifact; the wrapper's own prompt gate reads that same
    member (`pin arms "$ARM" promptSha256`). A registry that pins no digest for
    an arm refuses before anything is spent: an arm whose prompt bytes are not
    registered before the batch is not a registered arm."""
    pinned = ((pins.get("arms") or {}).get(arm) or {}).get("promptSha256")
    if not pinned:
        raise BatchError(
            "harness/PINS.json registers no arms.%s.promptSha256: every arm's "
            "PROMPT.txt is pinned before any call (§2)" % arm)
    return os.path.join(STUDY, "arms", arm, "PROMPT.txt"), pinned


def check_registry(pins: dict) -> None:
    """§2's `batch` member and the three arm prompts, against this file's own
    expansion — every registry check the preflight makes that does not depend on
    a stage-null pin, in one function so the harness can run the REAL ones
    against the COMMITTED registry.

    Study 012's round 3 finding 3 is why this is a function rather than a block
    of `preflight()`: its driver required member names the registry did not
    carry, and nothing failed, because the only preflight the suite ran was
    against stand-in registries built for the tests.

    The registry's own order is EXPANDED through `schedule()` rather than
    compared elementwise: comparing the members says the registry holds the same
    letters, expanding them says it holds the same ORDER, which is what the
    ledger, the resume and the shortfall are checked against.

    `batch.order.construction` is prose — a sentence naming the construction for
    a reader — and is deliberately not checked as data: the construction that
    governs is `williams()`, and `test_schedule.py` holds that against §2's
    published table."""
    batch_pin = pins.get("batch")
    if not isinstance(batch_pin, dict):
        raise BatchError(
            "harness/PINS.json registers no batch member: §2's call order, its N "
            "and its slot count are registry members, and a batch is not run "
            "against an order the registry does not carry")
    order = batch_pin.get("order")
    if not isinstance(order, dict):
        raise BatchError(
            "harness/PINS.json registers no batch.order: §2's call order is a "
            "registry member (its first row, its block order and its tail), and "
            "this batch will not run against an order the registry does not carry")
    first_row = order.get("firstRow")
    block_order = order.get("blockOrder")
    tail = order.get("tail")
    if not isinstance(first_row, list) or not isinstance(block_order, list) \
            or not isinstance(tail, list):
        raise BatchError(
            "harness/PINS.json's batch.order is %r: §2 registers firstRow as a "
            "list of arms, blockOrder as a list of sequence names and tail as a "
            "list of sequence names"
            % ({"firstRow": first_row, "blockOrder": block_order, "tail": tail},))
    if tuple(first_row) != WILLIAMS_FIRST_ROW:
        raise BatchError(
            "harness/PINS.json registers batch.order.firstRow = %r and §2's "
            "Williams first row is %r: the registry and the driver are one "
            "construction, not two" % (first_row, list(WILLIAMS_FIRST_ROW)))
    if order.get("blocks") != BLOCKS:
        raise BatchError(
            "harness/PINS.json registers batch.order.blocks = %r and §2's order "
            "is %d whole blocks of the %d sequences"
            % (order.get("blocks"), BLOCKS, SEQUENCES))
    # §7 delta 7. The spreads are part of the ORDER, not a description of it:
    # the registry publishes what `derive_order()` attained at the registered
    # round count, and `schedule()` asserts equality against them. A registry
    # that names an order without naming its balance is refused here, before a
    # call is spent, rather than at the expansion.
    for member, mine in (("positionSpread", REGISTERED_POSITION_SPREAD),
                         ("transitionSpread", REGISTERED_TRANSITION_SPREAD)):
        if order.get(member) != mine:
            raise BatchError(
                "harness/PINS.json registers batch.order.%s = %r and the "
                "canonical registry this driver derived its shape from "
                "publishes %r: the attained spread is a registered member "
                "(§7 delta 7) and two registries naming two balances is two "
                "orders" % (member, order.get(member), mine))
    registered = schedule(tuple(block_order), tuple(tail))
    derived = schedule()
    if registered != derived:
        first = next(offset for offset, (left, right)
                     in enumerate(zip(registered, derived)) if left != right)
        raise BatchError(
            "harness/PINS.json's batch.order expands to a different call order "
            "than §2's: at global index %d the registry's order gives %r and "
            "this file's gives %r. The registry and the driver are one order, "
            "not two spellings that happen to agree"
            % (first + 1, registered[first], derived[first]))
    if batch_pin.get("n") != RUNS_PER_ARM:
        raise BatchError(
            "harness/PINS.json registers batch.n = %r per arm and §2's order is "
            "%d rounds of %d arms — N = %d slots per arm, %d in total. The batch "
            "size and the call order are fixed together before the batch, so a "
            "registry that names another N refuses before a call is spent"
            % (batch_pin.get("n"), ROUNDS, POSITIONS, RUNS_PER_ARM,
               REGISTERED_SLOTS))
    if batch_pin.get("slots") != REGISTERED_SLOTS:
        raise BatchError(
            "harness/PINS.json registers batch.slots = %r and §2's call order "
            "expands to %d" % (batch_pin.get("slots"), REGISTERED_SLOTS))
    if batch_pin.get("arms") != list(ARMS):
        raise BatchError(
            "harness/PINS.json registers batch.arms = %r and §2's arms are %r"
            % (batch_pin.get("arms"), list(ARMS)))
    # The ceiling the WRAPPER enforces is read from the registry; the code this
    # driver classifies a ceiling hit with is its own constant. Three files
    # cannot hold three ceilings, so the two are compared before any call — the
    # harness test asserts the same pair, and this is the run-time half of it.
    if batch_pin.get("callTimeoutSeconds") != CALL_TIMEOUT_SECONDS \
            or batch_pin.get("timeoutKillAfterSeconds") != TIMEOUT_KILL_AFTER_SECONDS:
        raise BatchError(
            "harness/PINS.json registers a %r s ceiling with a %r s grace and "
            "this driver classifies against %d s and %d s: the wrapper reads the "
            "registry's numbers and the driver reads its own, so a disagreement "
            "is a batch bounded by one value and scored against another (§2 "
            "'Batch shape')"
            % (batch_pin.get("callTimeoutSeconds"),
               batch_pin.get("timeoutKillAfterSeconds"),
               CALL_TIMEOUT_SECONDS, TIMEOUT_KILL_AFTER_SECONDS))
    # Every arm's prompt, not one prompt: all three arms exist from round 1
    # under the interleaved order, so all three are checked before slot 1.
    for arm in ARMS:
        path, pinned = arm_prompt(pins, arm)
        if not os.path.isfile(path):
            raise BatchError("arm %s's %s is missing"
                             % (arm, os.path.relpath(path, STUDY)))
        actual = _digest(path)
        if not _matches(actual, pinned):
            raise BatchError("arm %s's %s is %s, not the pinned %s"
                             % (arm, os.path.relpath(path, STUDY), actual, pinned))


def verify_ported_bytes() -> dict:
    """§7's port chain as a precondition of the BATCH, not only of CI. A drifted
    port changes every count, and the digest table is checked before a call is
    spent because afterwards it is too late for the batch."""
    try:
        return integrity.verify()
    except integrity.IntegrityError as error:
        raise BatchError("the ported bytes are not the registered ones: %s" % error)


# --- D2: preflight -----------------------------------------------------------

def resolve_cli(cli_override: str) -> str:
    """`--cli-override`, or the `STUDY_CLI_STANDIN` test seam, or None (codex on
    PATH). Resolved ONCE per command, so the digest `preflight()` checks, the
    binary `invoke()` passes and the value the ledger header records are the
    same value — change 12. The seam removes no gate: whatever it names is
    hashed against `codex.binarySha256` here and again inside the wrapper."""
    if cli_override is not None:
        return cli_override
    return os.environ.get(STANDIN_ENV) or None


def require_canonical_registry(pins_path: str) -> str:
    """ROUND-10 FINDING R10-1. In the PRODUCTION tree, `harness/PINS.json` and
    nothing else.

    `--pins` existed so the harness tests could drive the whole calling half
    against a stand-in registry, and `authoring_call.sh` carried a sentence
    saying that was safe because the scorer would refuse a slot stamped with any
    other registry's digest. The scorer did no such thing when that sentence was
    written: it recorded `pinsRawSha256` in `ATTEMPT.json` and compared it to
    nothing. (`score.read_slot()` makes the comparison now, and a slot whose
    stamp differs is §1a's `registry-mismatch` — but a scoring-time code is a
    reading of runs that were already made, and the runs are what the
    preregistration says may not exist before the freeze. The two halves are
    complements: this one keeps the slot from being made, that one keeps a slot
    made another way from being scored as registered.)
    So `--pins` was a live seam on the production path, and the round-10
    reviewer walked through it — an alternate mapping with every freeze pin
    filled and the real preregistration digest passed `require_freeze()`, which
    judges the mapping it is HANDED. Slots authored that way are authored before
    the canonical freeze, survive it, and are then scored as registered, which
    is exactly what "150 post-freeze runs — no authoring run exists at freeze
    time" forbids.

    The seam is closed here rather than deleted, because deleting the flag would
    delete the stand-in surface with it. The two surfaces are distinguished by
    the thing that actually differs: the stand-in study is not this study.
    Under the production tree — `STUDY` still the directory this file lives in —
    a registry that is not `CANONICAL_PINS` is refused by name, whatever it
    contains and whatever label it would carry; under a patched `STUDY` the
    tests keep the flag they need. There is no environment variable and no
    opt-out: an operator who wants a different registry edits the registered
    one, in the open, where the manifest and the freeze see it."""
    if os.path.realpath(STUDY) != os.path.realpath(CANONICAL_STUDY):
        return pins_path
    if os.path.realpath(pins_path) != os.path.realpath(CANONICAL_PINS):
        raise BatchError(
            "--pins %s names a registry that is not harness/PINS.json, and the "
            "production tree is judged against harness/PINS.json alone (round-10 "
            "finding R10-1): a substitute registry with every freeze pin filled "
            "would carry the REGISTERED label into calls the canonical freeze "
            "never anchored" % pins_path)
    return pins_path


def load_registry(pins_path: str) -> dict:
    """The registry every command runs under: the canonical one (R10-1), read,
    and holding the registered label rule (change 6).

    One function, so that no command can acquire a registry by a path that skips
    either half — the five call sites were five copies of two lines, and a sixth
    copy is how a seam like R10-1's returns."""
    require_canonical_registry(pins_path)
    pins = _load_json(pins_path)
    require_freeze(pins)
    return pins


def require_freeze(pins: dict) -> str:
    """The registered label rule, before anything is called (change 6).

    Study 012 gated on ONE pin. This study's registry decides REGISTERED against
    the WHOLE freeze set in `integrity.study_label()`, because Study 014's round
    3 found a registered run reachable with only the preregistration digest
    filled — which left the registry the attempt adjudicated unpinned. Both
    halves are checked here: every freeze pin non-null, and `PREREGISTRATION.md`
    equal to the digest pinned for it, so a post-freeze edit is detectable.

    Registering this as a precondition of the CALLS as well as of the scoring is
    what makes it more than an intention: a registry merged with its nulls
    intact spends no quota."""
    # ROUND-1 R1-9 grew the freeze set from eleven pins to eighteen, and two of
    # the new members are values the PRE-FREEZE CEREMONY writes: `golden.sha256`
    # comes from the golden-context capture and `isolationNegative.assent` from
    # the isolation negative control, both of which reach this gate. Requiring
    # them here would make each command require the value it exists to create.
    # They are freeze pins regardless — `integrity.study_label()` reads the whole
    # set, so no REGISTERED attempt is reachable while either is null, and the
    # scorer's golden-context gate reads them again at attempt time — and
    # `integrity.CEREMONY_LIFECYCLE_PINS` exempts them at this one gate and
    # nowhere else. The specific golden and assent gates below and in
    # `record_negative_control()` are what refuse them at this stage.
    unfilled = integrity.ceremony_unfilled_pins(pins)
    if unfilled:
        raise BatchError(
            "harness/PINS.json labels this study %s: the batch runs under the "
            "registered label only, and these freeze pins are still null: %s. A "
            "PILOT supports no claim, so no PILOT spends the registered quota"
            % (integrity.study_label(pins), ", ".join(unfilled)))
    pinned = (pins.get("preregistration") or {}).get("sha256")
    path = os.path.join(STUDY, "PREREGISTRATION.md")
    if not os.path.isfile(path):
        raise BatchError("the preregistration is missing from %s" % STUDY)
    actual = _digest(path)
    if not _matches(actual, pinned):
        raise BatchError("PREREGISTRATION.md is %s, not the %s registered at the "
                         "freeze: it was edited after the freeze" % (actual, pinned))
    return actual


def golden_path_for(pins: dict, override: str = None) -> str:
    """The capture's path is structural — `transcription/GOLDEN-CONTEXT.json` —
    and the registry pins its digest, which is how this study treats every
    registered artifact. `--golden` serves the harness tests; the pin still has
    to match whatever it names."""
    return override or DEFAULT_GOLDEN


def require_golden(pins: dict, golden_path: str = None) -> str:
    """The capture is on disk and the registry's `golden.sha256` is non-null and
    equal to its digest, before any slot is created. A skipped recapture
    therefore costs nothing instead of costing a hundred and fifty calls, and
    the digest verified here is stamped into every slot's CALL.json so the
    binding is per run and not per batch. ONE capture serves all three arms: the
    pre-prompt context precedes the prompt and does not depend on it, and that
    does not become three properties because there are three prompts.

    What this does NOT check, stated so no caller reads more into it: that
    either file was COMMITTED. Nothing in this study compares a worktree file to
    a HEAD blob; committing the capture and the registry before slot 1 is ledger
    discipline the study records, not an ordering the driver enforces."""
    path = golden_path_for(pins, golden_path)
    pinned = (pins.get("golden") or {}).get("sha256")
    if not os.path.isfile(path):
        raise BatchError(
            "no golden context at %s: run the recapture (batch.py capture "
            "--scratch-parent DIR) and commit it before the first slot" % path)
    if not pinned:
        raise BatchError(
            "harness/PINS.json registers no golden.sha256: the capture's digest "
            "must replace the null and be committed before the first slot")
    actual = _digest(path)
    if not _matches(actual, pinned):
        raise BatchError("the golden capture at %s is %s, not the registered %s"
                         % (path, actual, pinned))
    return path


def require_isolation_negative(pins: dict, golden_path: str) -> dict:
    """§6's isolation negative control, before any slot is created.

    The control runs ONCE and BEFORE the batch, and Study 012's round 9 found
    that ordering was ceremony only: the registry's assent gated the control's
    own command and nothing else, so a hundred and fifty calls could be spent on
    a study whose publication list promises a control record that was never
    made. It is a precondition of the BATCH, which is what this function is.

    Checked here: the registry records the assent; the verdict is at the
    CANONICAL path and readable as duplicate-free JSON; its outcome is one of the
    THREE registered outcomes; it names the same assent the registry now records;
    it was compared against the golden capture THIS batch runs behind; and it has
    the SHAPE the writer produces (`c7_record_shape_problems()`).

    All three outcomes admit the batch — a `no-context` verdict already exits
    non-zero and is reported as undemonstrated, and refusing it here would make
    that registered sentence unreachable. What is refused is a control that never
    ran.

    What this does NOT establish: that the control's own calls were the
    registered ones, nor that the record was COMMITTED."""
    assent = (pins.get("isolationNegative") or {}).get("assent")
    if assent != "granted":
        raise BatchError(
            "harness/PINS.json records isolationNegative.assent %r: the "
            "isolation negative control runs before the batch and the registry "
            "records the assent it ran under (§6)" % (assent,))
    path = os.path.join(DEFAULT_NEGATIVE, "VERDICT.json")
    relative = os.path.relpath(path, STUDY)
    if not os.path.isfile(path):
        raise BatchError(
            "no isolation-negative record at %s: the control runs ONCE, BEFORE "
            "the batch (batch.py capture-isolation-negative --scratch-parent "
            "DIR), and no slot is created until its verdict is on disk" % relative)
    try:
        verdict = _load_json(path)
    except (ValueError, OSError) as error:
        raise BatchError("%s cannot be read as duplicate-free JSON (%s): the "
                         "control's verdict is the record the batch runs behind"
                         % (relative, error))
    if not isinstance(verdict, dict):
        raise BatchError("%s is a %s and the control's verdict is an object"
                         % (relative, type(verdict).__name__))
    if verdict.get("outcome") not in C7_OUTCOMES:
        raise BatchError("%s records outcome %r and §6 registers %r: a record "
                         "carrying none of them is not a control that ran"
                         % (relative, verdict.get("outcome"), list(C7_OUTCOMES)))
    if verdict.get("assent") != assent:
        raise BatchError("%s: the control was authorized by %r and the registry "
                         "now records %r: the record is not this batch's"
                         % (relative, verdict.get("assent"), assent))
    recorded = verdict.get("goldenSha256")
    actual = _digest(golden_path)
    if not isinstance(recorded, str) or not _matches(actual, recorded):
        raise BatchError("%s: the control was compared against golden capture %r "
                         "and this batch runs against %s: the control "
                         "demonstrates the power of the gate THIS batch runs "
                         "behind (§6)" % (relative, recorded, actual))
    shape = c7_record_shape_problems(verdict)
    if shape:
        raise BatchError("%s: %s — the record is not one this driver wrote"
                         % (relative, "; ".join(shape)))
    return verdict


def preflight(entries: list, slots: list, scratch_parent: str, pins_path: str,
              cli_override: str, prompt_kind: str,
              golden_path: str = None, calibration_mode: str = None) -> dict:
    """The pins, or BatchError. Everything checkable before the first call is
    checked before the first call: a batch that would run drifted bytes, collide
    with retained slots, publish after an attempt has been scored, run a prompt
    that is not the arm's pinned one, reach past the registered global index, or
    run without the registered golden capture must not spend a single
    invocation.

    `entries` are the schedule entries this invocation plans, empty for the probe
    calls (the recapture and the isolation control), which are not slots of the
    order."""
    verify_ported_bytes()
    if not slots:
        raise BatchError("a batch needs at least one run")
    if not os.path.isfile(SCRIPT):
        raise BatchError("no authoring wrapper at %s" % SCRIPT)
    if not os.path.isdir(scratch_parent):
        raise BatchError("scratch parent %s is not a directory" % scratch_parent)
    pins = load_registry(pins_path)
    # §7 delta 6, before any branch: the design-time-resolved pins are checked
    # under EVERY label — the primary batch, the pilot, the sweep and the probe
    # calls alike — because §2 marks them resolvedAtDesignTime and
    # registeredLabelRule checks them "whether or not the freeze has happened".
    # `calibration_mode` carries §2.1's ONE exemption and nothing else.
    require_design_time_pins(pins, calibration_mode)
    if prompt_kind == "registered":
        if not entries:
            raise BatchError("a batch of the registered order is planned from the "
                             "order: no schedule entries were given for %d slots"
                             % len(slots))
        # §2: the whole call order is registered before the batch, so the LAST
        # slot this invocation would create is bounded by its end —
        # unconditionally, whether or not --runs was given. The entries are a
        # slice of the expansion and cannot exceed it by construction; the bound
        # is checked anyway, because "cannot happen by construction" is a claim
        # about today's code and this is a claim about the study.
        if entries[-1]["globalIndex"] > REGISTERED_SLOTS:
            raise BatchError(
                "this invocation plans global indices %d…%d and §2 registers %d "
                "slots: no invocation may plan a slot past the registered order"
                % (entries[0]["globalIndex"], entries[-1]["globalIndex"],
                   REGISTERED_SLOTS))
        check_registry(pins)
    else:
        pinned = (pins.get("probePrompt") or {}).get("sha256")
        if not pinned:
            raise BatchError("harness/PINS.json registers no probePrompt.sha256")
        if not os.path.isfile(PROBE_PROMPT):
            raise BatchError("no probe prompt at %s"
                             % os.path.relpath(PROBE_PROMPT, STUDY))
        actual = _digest(PROBE_PROMPT)
        if not _matches(actual, pinned):
            raise BatchError("%s is %s, not the pinned %s"
                             % (os.path.relpath(PROBE_PROMPT, STUDY), actual, pinned))
    if cli_override is not None:
        if not os.path.isfile(cli_override):
            raise BatchError("no CLI at %s" % cli_override)
        override_digest = _digest(cli_override)
        if not _matches(override_digest, pins["codex"]["binarySha256"]):
            raise BatchError("the CLI at %s is %s, not the pinned %s"
                             % (cli_override, override_digest,
                                pins["codex"]["binarySha256"]))
    if prompt_kind == "registered":
        if os.path.exists(ATTEMPT_ROOT):
            # No slot in ANY arm after a rate has been computed. Adding runs
            # once the numbers are visible is the one thing a rate study must
            # never do, and here the operator also holds a directional
            # prediction about one of the arms.
            raise BatchError("%s exists: no slot may be created in any arm after "
                             "a rate has been computed"
                             % os.path.relpath(ATTEMPT_ROOT, STUDY))
        # `_write_json_atomic()` refuses to write over the ledger's temporary,
        # and that refusal would land AFTER a call had been spent. The state is
        # checkable before the first call, so it is checked before the first call.
        temporary = os.path.join(ARMS_ROOT, LEDGER_TEMP_NAME)
        if os.path.lexists(temporary):
            raise BatchError(
                "%s: a previous run left the ledger's temporary behind, which is "
                "the residue of a kill between writing the ledger and renaming "
                "it into place. The ledger itself is whole — the rename is "
                "atomic — so record the interrupted run in DEVIATIONS.md, remove "
                "that file, and run again" % os.path.relpath(temporary, STUDY))
        golden = require_golden(pins, golden_path)
        # LAST in the registered branch, and after the golden gate: the control's
        # record is bound to the capture, so the capture is verified before the
        # binding is compared, and every earlier refusal still fails for its own
        # reason. Probe calls take the other branch, because the recapture
        # precedes the control and the control precedes the batch.
        require_isolation_negative(pins, golden)
    # `lexists`, not `exists`: a DANGLING symlink at a planned slot path is
    # absent to `exists()` and present to `mkdir`. A link at a planned slot path
    # is a slot that already exists, whatever it points at.
    existing = [os.path.relpath(slot, STUDY) for slot in slots
                if os.path.lexists(slot)]
    if existing:
        raise BatchError("these slots already exist and are never rewritten: %s"
                         % ", ".join(existing))
    return pins


# --- D3: the call ------------------------------------------------------------

# NEW IN 020 (§2.1, M-25). The two labels a call can be made under, and the
# whole of the sweep exemption's surface on this side. `PRIMARY` is every
# registered call; `SWEEP` is the pre-pilot effort sweep, whose calls are
# `citable: false`, outside every population, and exempt from the
# `codex.reasoningEffort` null check because the sweep is what RESOLVES it.
#
# It is a driver ARGUMENT and not an inherited environment variable:
# `invoke()` sets `PIN_LABEL` unconditionally, so an operator's stray
# `PIN_LABEL=SWEEP` in a shell cannot reach the wrapper. Running the sweep
# outside the harness is the 019 failure exactly (§2a.1), and a label a shell
# could supply would be the same hole wearing a new name.
PIN_LABELS = ("PRIMARY", "SWEEP")
SWEEP_LABEL = "SWEEP"
# The environment member the sweep's per-call SETTING travels in. It is not part
# of Study 011's four-member contract and it is not a fifth general one: it is
# legal under one label, it is set unconditionally by `invoke()` exactly as
# `PIN_LABEL` is, and the wrapper refuses it under `PRIMARY`. A setting an
# operator's shell could supply would be the sweep run outside the harness
# wearing the harness's own name.
SWEEP_EFFORT_ENV = "SWEEP_EFFORT"

# --- §2.1's registered sweep, as constants -----------------------------------
#
# THE SWEPT SET, registered 2026-08-24, BEFORE THE SWEEP, as the maintainer's
# decision (PREREGISTRATION.md §2.1, "The three swept settings"). The registered
# shape — 3 settings × 3/arm — names a cardinality and no members, and a set
# whose members are chosen after the durations are seen is a picked set and not
# a swept one. These three are the pinned CLI's own named reasoning-effort
# tiers, in cost order.
#
# It is a CONSTANT here and a member there: `harness/PINS.json`'s
# `sweep.settings` carries the same three, and `harness/tests/test_sweep.py`
# binds this tuple to that member AND to §2.1's own paragraph, currency-style —
# a set edited in one place and not the others fails the suite rather than
# running.
#
# `xhigh`, `max` and `ultra` are reachable only by a `DEVIATIONS.md` entry
# naming the reason and republishing the price. That is enforced and not merely
# stated: `invoke()` refuses a setting outside this tuple and the wrapper
# refuses one outside `sweep.settings`, so the deviation has to be WRITTEN
# before either will run it.
SWEEP_SETTINGS = ("low", "medium", "high")
SWEEP_PER_ARM = 3
# The same registered number under the name §2a.2's calibration record reads it
# by. An ALIAS and not a second literal: §2.1 states "n = 3/arm" once, so the
# two readers share one binding and a drift between them is not expressible.
SWEEP_RUNS_PER_ARM = SWEEP_PER_ARM
# 3 settings × 3 arms × 3 runs. Derived, so a fourth setting cannot silently
# leave the registered cap behind — and checked against the registry's own
# `sweep.callCap`, so a cap raised in one place and not the other refuses.
SWEEP_CALL_CAP = len(SWEEP_SETTINGS) * POSITIONS * SWEEP_PER_ARM
# The abort rule's second clause (§2.1). `SWEEP_BUDGET_PROJECTION_N` is the ONE
# branch §2.1's dual-pricing table prices — N = 60/arm — which that table calls
# a priced illustration and not a registered N. When `batch.n` is filled the
# projection is made at THAT value instead and the ledger records which of the
# two it used; the driver never silently takes the cheaper one.
SWEEP_BUDGET_HOURS = 72
SWEEP_BUDGET_PROJECTION_N = 60
# The sweep's dated label and the directory a call at the CLI's own default
# lands under. The label's SHAPE is checked by the wrapper too, from the slot
# path, because that is the one anchor component the wrapper cannot compute.
SWEEP_LABEL_SUFFIX = "-effort-sweep"
SWEEP_DEFAULT_SETTING_DIR = "default"
SWEEP_LEDGER_NAME = "SWEEP.json"
SWEEP_TABLE_NAME = "SWEEP.md"
# M-24's witness resolution. The member names a `turn_context` payload could use
# for the effort, searched at any depth: 019's transcripts carry
# `collaboration_mode.settings.reasoning_effort` and hold NULL there, which is
# the state M-24 describes and the reason the resolution is a step and not an
# assumption. A name matched here with a NON-NULL value is a witness; the same
# name holding null is not.
EFFORT_WITNESS_MEMBERS = ("reasoning_effort", "reasoningEffort",
                          "model_reasoning_effort", "reasoning_level",
                          "default_reasoning_level", "effort")
# The two branches M-24 registers, named so the ledger records a registered word
# and not a sentence somebody wrote at the keyboard.
WITNESS_BRANCH_GATE5 = "gate-5-extension"
WITNESS_BRANCH_SELF_REPORT = "call-json-self-report"


def invoke(slot: str, scratch_parent: str, pins_path: str, cli_override: str,
           prompt_kind: str, arm: str, arm_prompt_path: str,
           isolation: str = "isolated", golden_sha256: str = None,
           pin_label: str = "PRIMARY", sweep_effort: str = None) -> tuple:
    """(wrapper exit status, refusal code or None, stderr) for one call.

    `arm` and `arm_prompt_path` are the wrapper's two arm arguments, inserted
    before the optional binary: the wrapper writes into the arm's slot tree — and
    refuses a slot path that is not `arms/<ARM>/authoring/` — and stamps `arm`
    and `armPromptSha256` into CALL.json, so an arm mismatch is a per-slot check
    against retained bytes rather than a claim about this driver's bookkeeping.
    The probe calls pass the wrapper's registered no-arm literal and the probe
    prompt's own path.

    `golden_sha256` is the digest `require_golden()` verified at preflight; the
    wrapper stamps it into the slot's CALL.json, so the scorer can check the
    golden-before-slots ordering per slot instead of taking it on trust. The
    probe calls precede the golden and pass none.

    The environment contract is Study 011's, unchanged and not extended:
    PYTHON_BIN, PROMPT_KIND, ISOLATION, GOLDEN_SHA256. The schedule stamps do
    NOT travel this way, because the wrapper's permitted differences are
    registered as exactly five and reading a round index from the environment is
    not among them; `stamp_slot()` writes them after this returns.

    `STUDY_CLI_STANDIN` reaches this function as `cli_override` and by no other
    route: `resolve_cli()` has already collapsed the two, so there is one value
    and the digest gate has already seen it."""
    argv = ["bash", SCRIPT, scratch_parent, slot, pins_path, arm, arm_prompt_path]
    if cli_override is not None:
        argv.append(cli_override)
    environment = dict(os.environ)
    environment["PYTHON_BIN"] = sys.executable
    environment["PROMPT_KIND"] = prompt_kind
    environment["ISOLATION"] = isolation
    environment["GOLDEN_SHA256"] = golden_sha256 or ""
    if pin_label not in PIN_LABELS:
        raise BatchError(
            "%r is not a registered pin label; the registered labels are %s, "
            "and an unrecognised one is refused rather than treated as PRIMARY"
            % (pin_label, ", ".join(PIN_LABELS)))
    if sweep_effort is not None and pin_label != SWEEP_LABEL:
        raise BatchError(
            "a sweep setting (%r) was passed with the pin label %r: §2.1's "
            "per-call setting travels under %s alone, and a primary call runs "
            "the registry's codex.reasoningEffort or it does not run"
            % (sweep_effort, pin_label, SWEEP_LABEL))
    if sweep_effort is not None and sweep_effort not in SWEEP_SETTINGS:
        raise BatchError(
            "%r is not one of the registered sweep settings %s: §2.1 registers "
            "the swept SET on 2026-08-24, before the sweep, and a tier outside "
            "it needs a DEVIATIONS.md entry naming the reason and republishing "
            "the price" % (sweep_effort, ", ".join(SWEEP_SETTINGS)))
    # Set UNCONDITIONALLY, never defaulted from the inherited environment: the
    # sweep exemption is claimed by the driver or not at all. Both members, for
    # the same reason and by the same rule — an operator's stray `PIN_LABEL` or
    # `SWEEP_EFFORT` is overwritten here whether or not this call is a sweep's.
    environment["PIN_LABEL"] = pin_label
    environment[SWEEP_EFFORT_ENV] = sweep_effort or ""
    # The helper interpreters the wrapper runs must not write bytecode beside
    # the reviewed sources: an existing cache loads even under -B, and the
    # verification gate refuses on one.
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(argv, env=environment, capture_output=True, text=True)
    try:
        code = wrapper_code(completed.returncode)
    except BatchError as error:
        # The stderr tail travels with the refusal: an unregistered status is
        # the one case where the wrapper's own message is the only evidence of
        # what happened, and it would otherwise be discarded with the process.
        raise BatchError("%s\nwrapper stderr tail: %s"
                         % (error, (completed.stderr or "")[-STDERR_TAIL:]))
    return completed.returncode, code, completed.stderr


def stamp_slot(slot: str, entry: dict, pins: dict) -> None:
    """The schedule stamps into `CALL.json`, after checking the wrapper's own.

    Two things happen here, in this order, and both before the slot is sealed.

    First the wrapper's own stamps are checked against the schedule this driver
    planned: the `arm` must be the slot's SCHEDULED arm, the `armPromptSha256`
    must be that arm's pinned prompt, and the `slotIndex` the wrapper read out of
    the slot name must be the arm's own index. The scorer re-derives all of it
    from the retained bytes and assigns the mismatch codes itself — nothing here
    is that judgment. What this catches is a driver/wrapper disagreement, at a
    cost of one call rather than a hundred and fifty, and it refuses the batch
    because every remaining slot would carry the same defect.

    Then the three members the registration puts in `CALL.json` and the wrapper
    does not write — `round`, `position`, `globalIndex` — are added. They are
    written here and not by the wrapper because the wrapper's permitted
    differences are registered and reading a schedule from its environment is
    not among them. The stamps go in before `seal_slot()` runs, so they are
    inside the seal and an edit to them afterwards is exactly what the manifest
    and the chain refuse.

    A slot with no CALL.json — the wrapper refused before it wrote one — has
    nothing to stamp and nothing to check, and is left to the scorer, which reads
    the absence itself.

    A refusal here leaves the slot on disk, unsealed and unrecorded, which the
    scorer refuses as a slot with no ledger record: the disagreement is
    adjudicated in `DEVIATIONS.md` and not by this driver, whose alternative
    would be to seal bookkeeping it has just found to be wrong."""
    call_path = os.path.join(slot, "CALL.json")
    if not os.path.isfile(call_path):
        return
    call = _load_json(call_path)
    _, pinned = arm_prompt(pins, entry["arm"])
    if call.get("arm") != entry["arm"]:
        raise BatchError(
            "%s is scheduled as arm %s at global index %d and its CALL.json "
            "records arm %r: the batch stops here rather than spending the "
            "remaining slots under a wrapper that names the wrong arm"
            % (os.path.relpath(slot, STUDY), entry["arm"], entry["globalIndex"],
               call.get("arm")))
    stamped = call.get("armPromptSha256")
    if not isinstance(stamped, str) or not _matches(stamped, pinned):
        raise BatchError(
            "%s records armPromptSha256 %r and arm %s's registered prompt is %s: "
            "the run was made with bytes that are not the arm's"
            % (os.path.relpath(slot, STUDY), stamped, entry["arm"], pinned))
    if call.get("slotIndex") != entry["slotIndex"]:
        raise BatchError(
            "%s records slotIndex %r and the registered order assigns arm %s's "
            "slot %d at global index %d: the slot's name and its place in the "
            "order disagree"
            % (os.path.relpath(slot, STUDY), call.get("slotIndex"), entry["arm"],
               entry["slotIndex"], entry["globalIndex"]))
    for member in ("globalIndex", "round", "position"):
        if member in call:
            raise BatchError(
                "%s already carries a %s stamp (%r): the schedule stamps are "
                "written once, by the driver, into the slot it just made"
                % (os.path.relpath(slot, STUDY), member, call[member]))
        call[member] = entry[member]
    _write_json(call_path, call)


def refuse_slot(slot: str, code: str, status: int, stderr: str) -> None:
    """Terminate one slot with its refusal record. A pre-flight refusal may leave
    no slot at all; the record still gets one, so every attempted run is on disk
    and the population has no invisible members.

    `exist_ok=True` covers the ordinary case of a slot the wrapper created. It
    does not cover a path that exists and is not a directory — a link, a file, a
    FIFO — where `makedirs` raises `FileExistsError` and the batch would end in a
    bare traceback. Preflight already refuses those, so reaching this is a bug;
    it refuses as a BatchError rather than as a traceback so that the driver's
    failure is one of its own registered refusals either way."""
    if code not in CODE_PARTITION:
        raise BatchError(
            "no refusal record is written under the code %r: §1a's partition "
            "does not name it, and a slot on disk wearing an unnamed code is a "
            "run that no rule counts and no rule excludes (R1-4)" % code)
    if os.path.lexists(slot) and not os.path.isdir(slot):
        raise BatchError(
            "%s exists and is not a directory, so no refusal record can be "
            "written into it: remove it by hand and record the cause in "
            "DEVIATIONS.md" % slot)
    os.makedirs(slot, exist_ok=True)
    _write_json(os.path.join(slot, "REFUSAL.json"), {
        "run": os.path.basename(slot),
        "code": code,
        "wrapperExit": status,
        "wrapperStderrTail": stderr[-STDERR_TAIL:],
        "note": "Recorded by batch.py. harness/score.py recomputes admission "
                "from the retained bytes and does not trust this record.",
    })


# --- D3b: the transcript binding (R1-5) --------------------------------------

def transcript_verdict(slot: str, arm: str, pins: dict,
                       golden_path: str) -> dict:
    """The FULL transcript binding for one slot, as a structured verdict.

    **The one entry point.** Round 1's R1-5: the wrapper called only
    `extract_completion()` and `context_digests()`, and the only non-test caller
    of `check_golden()` was the golden capture itself — so no scored slot ever
    went through the gate that binds the transcript to the arm's prompt bytes, to
    the golden pre-prompt context, and to the retained completion. A transcript
    carrying the wrong prompt, an extra pre-prompt turn, or a completion that is
    not its last assistant message stayed in the population. This function is
    what both the driver (below, at the seal) and the scorer (per scored slot)
    call, so there is one binding and not two readings of one.

    The verdict is `transcript_check.classify()`'s: `admissible`, and when it is
    not, the `reason` tag, the §1a `side` that reason is attributed to, and the
    `code` the run is filed under. Attribution is the whole point of the
    structure — an author who used a tool or took a turn after the registered
    prompt is an AUTHORING outcome, retained in the denominator and scoring zero,
    while a mismatched prompt, a drifted golden context, a mangled log or a
    mis-extracted completion is APPARATUS and leaves it. `classify()` refuses
    outright on a reason nobody registered, and that refusal propagates: a
    transcript this study cannot attribute does not get a denominator by
    default."""
    prompt_path, _pinned = arm_prompt(pins, arm)
    return transcript_check.classify(
        os.path.join(slot, "session.jsonl"),
        prompt_path,
        os.path.join(slot, "completion.txt"),
        os.path.join(slot, "CALL.json"),
        golden_path,
        model=(pins.get("codex") or {}).get("model"),
        arm=arm)


def bind_transcript(slot: str, entry: dict, pins: dict,
                    golden_path: str) -> dict:
    """Run the binding and retain its verdict in the slot, before the seal.

    The driver runs it as well as the scorer for one reason worth the bytes: a
    systematic apparatus break — a golden capture that drifted, a prompt file
    swapped under the batch — is visible at slot 2 instead of after a hundred and
    fifty calls have been spent on a batch that will score none of them. It does
    NOT refuse: a per-slot verdict is a per-slot outcome, the population rule
    owns what happens to it, and a driver that stopped the batch on one refused
    transcript would be adjudicating §1a from inside D3.

    An `UnclassifiedRefusal` is the exception, and it propagates: a refusal this
    study has no cause for is a defect in the gate, every remaining slot would
    meet it, and the fail-closed answer is to stop rather than to seal a verdict
    that says nothing."""
    verdict = transcript_verdict(slot, entry["arm"], pins, golden_path)
    _write_json(os.path.join(slot, TRANSCRIPT_NAME), {
        "slot": os.path.basename(slot),
        "arm": entry["arm"],
        "globalIndex": entry["globalIndex"],
        "admissible": verdict["admissible"],
        "reason": verdict["reason"],
        "side": verdict["side"],
        "code": verdict["code"],
        "message": verdict["message"],
        "goldenSha256": (pins.get("golden") or {}).get("sha256"),
        "armPromptSha256": arm_prompt(pins, entry["arm"])[1],
        "note": "The full transcript binding for this slot: the arm's prompt "
                "bytes, the golden pre-prompt context, the retained completion, "
                "the turn-context model and cwd, and the recorded exit status. "
                "Written by batch.py before the seal, so it is inside the "
                "manifest and the ledger chain. Recorded by batch.py; "
                "harness/score.py recomputes this verdict from the same retained "
                "bytes and does not trust this record. `side` is what §1a does "
                "with the run: an author protocol violation (a tool call, a turn "
                "after the registered prompt) is an AUTHORING outcome, retained "
                "in the denominator and scoring zero; every other refusal is "
                "APPARATUS and leaves it.",
    })
    return verdict


# --- D4: the seal ------------------------------------------------------------

def _entry_type(mode: int) -> str:
    """The type marker a non-regular entry is sealed by. Every marker is a fixed
    string, so the seal a driver writes and the list a scorer recomputes name a
    FIFO the same way on both sides."""
    for predicate, marker in TYPE_MARKERS:
        if predicate(mode):
            return marker
    return "other"


def slot_files(slot: str) -> list:
    """The sorted list, over the slot ROOT and EVERY entry beneath it, in path
    order — the shape the scorer recomputes and compares entry for entry.

    A regular file is `[relative path, byte length, bare sha256 hex]`. Every
    other entry is `[relative path, NON_FILE_LENGTH, "type:<marker>"]`: named and
    typed, since it is not a byte range to hash.

    **The root is an entry too, at path `.`** (Study 012's round 8, finding 4).
    Walking only what lies BENEATH the slot can be evaded one level up: rename
    the sealed directory and plant a symlink at its old path, and every entry the
    list covers is byte-identical through the link, while the scorer's lstat-first
    rule moves the slot out of the valid set and into the invalid one — the same
    denominator change the seal exists to prevent.

    **Every entry, not every regular file** (round 7, finding 3). An entry ADDED
    after the seal — a symlink, most of all — leaves a regular-files-only
    manifest recomputing exactly as written, and buys that slot a
    pipeline-invalid code and the denominator change it carries.

    `SLOT-MANIFEST.json` is excluded from its own list — a file cannot carry its
    own digest — and is sealed instead by the ledger, which records the digest of
    the manifest file itself. `os.walk` does not descend into symlinked
    directories, so a link cannot smuggle a subtree into the seal. Every type is
    decided by `lstat`, and only regular files are opened, so a FIFO in a slot
    tree is sealed rather than read (an `open()` on one blocks forever)."""
    rows = [[SLOT_ROOT_ENTRY, NON_FILE_LENGTH,
             "type:%s" % _entry_type(os.lstat(slot).st_mode)]]
    for base, directories, names in os.walk(slot):
        directories.sort()
        for name in sorted(directories + names):
            path = os.path.join(base, name)
            relative = os.path.relpath(path, slot)
            if relative == MANIFEST_NAME:
                continue
            mode = os.lstat(path).st_mode
            if stat.S_ISREG(mode):
                with open(path, "rb") as handle:
                    body = handle.read()
                rows.append([relative, len(body), hashlib.sha256(body).hexdigest()])
            else:
                rows.append([relative, NON_FILE_LENGTH, "type:%s" % _entry_type(mode)])
    return sorted(rows)


def files_digest(files: list) -> str:
    """"The sha256 of that sorted list", made byte-exact: one
    `<path> <bytes> <sha256>` line per file, sorted, newline-terminated.

    The registration fixes the CONTENT of the list and not its serialization, so
    the serialization has to be fixed somewhere, once, in a form the scorer can
    reproduce exactly. A non-regular entry's row encodes in the same three
    fields: `<path> -1 type:<marker>`."""
    listing = "\n".join("%s %d %s" % tuple(row) for row in sorted(files)) + "\n"
    return "sha256:" + hashlib.sha256(listing.encode("utf-8")).hexdigest()


def seal_slot(slot: str, entry: dict) -> str:
    """The terminal manifest, and the digest of the FILE it writes — the value
    the ledger record carries, which binds the list and its digest into the chain
    and is what the scorer recomputes.

    **The sealer is the DRIVER.** The seal must cover *the slot*, and the wrapper
    is not the last writer into it: `REFUSAL.json` is this driver's, so a manifest
    written inside the wrapper would seal every slot except the refused ones —
    leaving exactly the slots whose retained bytes explain a failure unsealed,
    and the pipeline-invalid rate is an endpoint. The seal is therefore taken
    after the refusal record and the schedule stamps are written and before the
    ledger record is appended, for every outcome including refusals; the
    wrapper's own header states the same division, so the two artifacts agree
    rather than each assuming the other did it.

    What the seal establishes and what it does not: the operator can recompute
    the whole chain. It shows that a slot was not altered in isolation or after
    the ledger was published; it does not show that the ledger was written
    honestly, and this study has no transparency log (§8)."""
    if not os.path.isdir(slot):
        raise BatchError(
            "%s is not a directory after the wrapper returned, so it cannot be "
            "sealed: record the cause in DEVIATIONS.md" % slot)
    path = os.path.join(slot, MANIFEST_NAME)
    if os.path.lexists(path):
        raise BatchError("%s already exists: a slot is sealed once, and a slot "
                         "that carries a seal was not created by this invocation"
                         % path)
    files = slot_files(slot)
    _write_json(path, {
        "slot": os.path.basename(slot),
        "arm": entry["arm"],
        "globalIndex": entry["globalIndex"],
        "files": files,
        "filesSha256": files_digest(files),
        "note": "The terminal seal of this slot: the slot ROOT itself, at the "
                "relative path `.`, and EVERY entry beneath it by relative path "
                "— regular files by byte length and sha256, everything else "
                "(symlinks, directories, FIFOs, sockets, devices) by a -1 length "
                "and a type: marker — sorted by path, and the sha256 of that "
                "sorted list. Every entry, so that an entry ADDED after the seal "
                "breaks it rather than passing it and then buying that slot a "
                "pipeline-invalid code and the denominator change it carries; "
                "and the root, so that renaming this directory and planting a "
                "symlink at its old path breaks it for the same reason. This "
                "file is not a member of its own list — a file cannot carry its "
                "own digest — and is sealed instead by the ledger, whose record "
                "for this slot carries the digest of THIS FILE and the previous "
                "record's digest, so BATCH.json is a hash chain in schedule "
                "order. A slot whose recomputed manifest differs from the "
                "ledger's, or a chain that does not verify, invalidates "
                "confirmatory scoring for the WHOLE batch rather than moving "
                "this slot out of a denominator.",
    })
    return _digest(path)


# --- D5: the chained ledger --------------------------------------------------

def record_digest(record: dict) -> str:
    """One ledger record's digest, over the same canonical serialization the
    manifest's list uses. The record being digested carries its own
    `previousSha256`, which is what makes the sequence a chain rather than a list
    of independently digested lines."""
    return "sha256:" + hashlib.sha256(_canonical(record)).hexdigest()


def ledger_record(entry: dict, slot: str, status: int, code: str,
                  manifest_sha256: str, previous: str) -> dict:
    """The per-slot record: where the slot sits in the registered order, where it
    sits on disk, what the wrapper's exit status was, its seal, and the digest of
    the record before it.

    The code is checked against §1a's partition on the way in (R1-4). The ledger
    is the population's index, and a record carrying a code the partition does
    not name puts a run into the study that neither the excluded set nor the
    denominator has a rule for — which is how `preflight-refused` and the
    `wrapper-error` sentinel used to reach every per-arm rate."""
    if code is not None and code not in CODE_PARTITION:
        raise BatchError(
            "no ledger record is written for global index %s under the code %r: "
            "§1a's partition does not name it" % (entry.get("globalIndex"), code))
    if wrapper_code(status) != code:
        raise BatchError(
            "no ledger record is written for global index %s: the wrapper exited "
            "%r, which this driver files as %r, and the record would carry %r"
            % (entry.get("globalIndex"), status, wrapper_code(status), code))
    record = {key: entry[key] for key in SCHEDULE_KEYS}
    record.update({
        "slot": os.path.basename(slot),
        # The ledger and the slot set are in bijection "at the path the record
        # names", so the record names one — study-relative, so the ledger is
        # portable and the population is not addressed by an absolute path this
        # machine happens to have.
        "path": os.path.relpath(slot, STUDY),
        "wrapperExit": status,
        "code": code,
        "manifestSha256": manifest_sha256,
        "previousSha256": previous,
    })
    return record


def load_ledger() -> list:
    """The per-slot records BATCH.json already holds, IN FILE ORDER. A resumed
    batch MERGES into these rather than replacing them: the wrapper's exit status
    is retained per slot, and a slot that exited 0 carries it nowhere else, so
    overwriting the ledger would delete the only record of runs the resume did
    not make.

    File order is schedule order, and that is verified here before the records
    are used for anything. Sorting them first silently normalizes a ledger whose
    records have been physically reordered — the prefix check then passes over
    the sorted list and the file is rewritten in the order the driver preferred,
    while the scorer reads the same file in file order and refuses it. A
    reordered ledger is a ledger someone edited; the chain is over the file, and
    the driver refuses rather than repairing it.

    The decoded top level and the `records` member are both TYPE-CHECKED here:
    `[]` decodes fine and then reaches `.get` on a list, which is a traceback
    where the resume rule promises a refusal naming the file."""
    path = os.path.join(ARMS_ROOT, LEDGER_NAME)
    if not os.path.isfile(path):
        return []
    ledger = _load_json(path)
    if not isinstance(ledger, dict):
        raise BatchError(
            "%s decodes to a JSON %s and a ledger is an object carrying a records "
            "list: a file that is not one is not this batch's ledger, whatever it "
            "holds. Move it aside and record why in DEVIATIONS.md"
            % (path, type(ledger).__name__))
    records = ledger.get("records")
    if records is None:
        raise BatchError(
            "%s carries no records member (batchVersion %r) and cannot be "
            "resumed into: move it aside and record why in DEVIATIONS.md"
            % (path, ledger.get("batchVersion")))
    if not isinstance(records, list):
        raise BatchError(
            "%s's records member is a JSON %s and the registration registers it "
            "as the list of per-slot records in schedule order: a ledger whose "
            "records are not a list has no prefix to check and no chain to "
            "verify. Move it aside and record why in DEVIATIONS.md"
            % (path, type(records).__name__))
    previous = None
    for offset, record in enumerate(records):
        index = record.get("globalIndex") if isinstance(record, dict) else None
        if not isinstance(index, int) or isinstance(index, bool):
            raise BatchError(
                "%s's record %d carries globalIndex %r: every ledger record names "
                "its place in §2's registered order, and a record that does not "
                "cannot be checked against it" % (path, offset + 1, index))
        if previous is not None and index <= previous:
            raise BatchError(
                "%s records global index %d after %d: the ledger is append-only "
                "in §2's registered order and its FILE order is that order. A "
                "file whose records have been moved is refused, not re-sorted — "
                "the driver would otherwise rewrite it in an order the scorer "
                "never saw. Record the cause in DEVIATIONS.md"
                % (path, index, previous))
        previous = index
    return records


def verify_ledger_chain(records: list) -> None:
    """The hash chain, verified over the ledger in schedule order.

    Verified by the DRIVER and not only by the scorer, because a batch whose
    chain does not verify can never be scored confirmatorily — that consequence
    is registered in advance — and continuing to spend calls into it would be
    spending them on a batch that already has no verdict to give.

    Named `verify_ledger_chain` and not `verify_chain`: `integrity.verify_chain()`
    is the PORT chain, this study imports that module, and two functions called
    `verify_chain` over two different chains in one namespace is a name a reader
    has to disambiguate every time."""
    previous = None
    for record in records:
        if record.get("previousSha256") != previous:
            raise BatchError(
                "the ledger's hash chain breaks at global index %r: the record "
                "names %r as its predecessor's digest and the record before it "
                "digests to %r. A batch whose chain does not verify is not scored "
                "confirmatorily at all; record the cause in DEVIATIONS.md"
                % (record.get("globalIndex"), record.get("previousSha256"), previous))
        previous = record_digest(record)


def verify_prefix(records: list, entries: list) -> None:
    """The ledger IS the registered order's prefix of its own length, position by
    position, or BatchError naming the first divergence.

    This is what makes resumption by global index safe where `--start-round` was
    not: a round number cannot say whether the rest of its round ran, and an
    overlap or an omission inside a round is undetectable after the fact from
    one. A prefix of the registered order is checkable against the order itself,
    at every position, before a call is spent.

    The record's `path` is one of the compared members, and it is DERIVED
    (Study 012's round 8, finding 5): a first record carrying the schedule keys
    for global index 1 and the path `README.md` otherwise verifies as the
    registered prefix, reconciles against a tree in which `run-001` is absent,
    and lets `--resume` continue at index 2 over a slot that was never made. The
    path a record names has to be the path the order assigns its (arm, slot
    index), recomputed here from `slot_path()`."""
    if len(records) > len(entries):
        raise BatchError(
            "%s records %d slots and §2 registers %d: a ledger longer than the "
            "registered order is not a prefix of it"
            % (os.path.join(ARMS_ROOT, LEDGER_NAME), len(records), len(entries)))
    for offset, record in enumerate(records):
        expected = {key: entries[offset][key] for key in SCHEDULE_KEYS}
        expected["path"] = os.path.relpath(slot_path(entries[offset]), STUDY)
        actual = {key: record.get(key) for key in SCHEDULE_KEYS}
        actual["path"] = record.get("path")
        if actual != expected:
            raise BatchError(
                "the ledger diverges from §2's registered call order at position "
                "%d: it records %r and the order assigns %r. No slot is re-run "
                "and no batch continues from a ledger that is not a prefix of the "
                "registered order" % (offset + 1, actual, expected))
    verify_ledger_chain(records)


def ledger_header(member: str, default=None):
    """One member of the ledger FILE's own header, or `default` when there is no
    ledger yet. `declare_shortfall()` reads `cliOverride` through this when it
    completes a crash-interrupted record: the header describes the batch that
    ran, and the declaration is not the place to restate it from a fresh command
    line."""
    path = os.path.join(ARMS_ROOT, LEDGER_NAME)
    if not os.path.isfile(path):
        return default
    ledger = _load_json(path)
    return ledger.get(member, default) if isinstance(ledger, dict) else default


def write_ledger(records: list, pins: dict, cli_override: str) -> None:
    # Atomically: this file is rewritten in full after every slot, and a kill
    # during the rewrite can otherwise leave a truncated one — losing the only
    # record of every slot that ran before it.
    _write_json_atomic(os.path.join(ARMS_ROOT, LEDGER_NAME),
                       os.path.join(ARMS_ROOT, LEDGER_TEMP_NAME), {
        "batchVersion": "1",
        "registeredRunsPerArm": RUNS_PER_ARM,
        "registeredSlots": REGISTERED_SLOTS,
        "model": pins["codex"]["model"],
        "binarySha256": pins["codex"]["binarySha256"],
        "armPromptSha256": {arm: arm_prompt(pins, arm)[1] for arm in ARMS},
        "goldenSha256": (pins.get("golden") or {}).get("sha256"),
        "callTimeoutSeconds": CALL_TIMEOUT_SECONDS,
        "cliOverride": cli_override,
        # Schedule order IS chain order: each record's previousSha256 is the
        # digest of the record before it in this list, so sorting by global index
        # is the same list the chain was built in.
        "records": sorted(records, key=lambda row: row["globalIndex"]),
        "note": "One append-only record per slot in §2's registered order, "
                "written after every run and MERGED by a resumed invocation "
                "(batch.py run --resume), which continues at the next global "
                "index, refuses to overlap a recorded one, and refuses if the "
                "recorded prefix diverges from the registered order at any "
                "position. Each record carries its slot's SLOT-MANIFEST.json "
                "digest and the previous record's digest, so this file is a hash "
                "chain over the batch — which the operator can recompute in full, "
                "and which therefore shows that no slot was altered in isolation, "
                "not that this ledger was written honestly (§8). No clock is "
                "recorded here; each slot's CALL.json carries its own start and "
                "end.",
    })


# --- D6: reconciliation ------------------------------------------------------

def verify_seal_of(slot: str, entry: dict) -> str:
    """The digest of a slot's `SLOT-MANIFEST.json` when that manifest is this
    slot's — the slot root and every entry beneath it at the length, digest or
    type marker it records, the sorted-list digest over them, and the slot, arm
    and global index it names — or BatchError saying which of those failed.

    This is `seal_slot()` read backwards, over a slot the driver did not just
    make. It exists for the one case that needs it (`reconcile_ledger()`) and it
    recomputes rather than trusts: a manifest that does not verify is exactly the
    evidence that a slot was interrupted mid-write or edited, and neither may be
    admitted to the ledger on the strength of the file that claims to seal it.

    A manifest that is not readable JSON, or whose keys are duplicated, is that
    same evidence and refuses through this registered path rather than escaping
    as a bare `ValueError`."""
    path = os.path.join(slot, MANIFEST_NAME)
    if os.path.islink(path) or not os.path.isfile(path):
        raise BatchError(
            "%s is not sealed: %s is missing or is not a regular file. The driver "
            "seals a slot BEFORE it records it, so an unsealed slot is one whose "
            "wrapper never returned — it did not run to a terminal outcome, and "
            "no ledger record can be completed for it. Remove it by hand and "
            "record the cause in DEVIATIONS.md"
            % (os.path.relpath(slot, STUDY), MANIFEST_NAME))
    try:
        manifest = _load_json(path)
    except (ValueError, OSError) as error:
        raise BatchError(
            "%s cannot be read as duplicate-free JSON (%s): a seal that cannot be "
            "read is not a seal that verifies, and no ledger record is completed "
            "from one. Remove the slot by hand and record the cause in "
            "DEVIATIONS.md" % (os.path.relpath(path, STUDY), error))
    if not isinstance(manifest, dict):
        raise BatchError("%s is not a JSON object" % os.path.relpath(path, STUDY))
    named = (manifest.get("slot"), manifest.get("arm"), manifest.get("globalIndex"))
    expected = (os.path.basename(slot), entry["arm"], entry["globalIndex"])
    if named != expected:
        raise BatchError(
            "%s seals %r and §2's registered order puts %r at that path: the "
            "manifest is not this slot's"
            % (os.path.relpath(path, STUDY), named, expected))
    files = slot_files(slot)
    if manifest.get("files") != files \
            or manifest.get("filesSha256") != files_digest(files):
        raise BatchError(
            "%s does not verify against the slot it seals: the tree on disk is "
            "not the one the manifest lists. A slot whose seal does not recompute "
            "is not admitted to the ledger — that discrepancy is the whole "
            "batch's, and completing a record from a broken seal would put it "
            "inside the chain instead" % os.path.relpath(path, STUDY))
    return _digest(path)


def slot_outcome(slot: str) -> tuple:
    """(wrapper exit status, refusal code) as the SLOT's own retained bytes
    record them: `REFUSAL.json` when the driver terminated it, and exit 0 with no
    code when the wrapper wrote a `CALL.json` and no refusal.

    Those are the only two shapes `run_batch()` produces, and the pair is checked
    against `WRAPPER_CODES` rather than taken from the file: a refusal record
    naming a code no exit status of this wrapper yields is not this driver's, and
    a slot carrying neither artifact never reached a terminal outcome at all."""
    refusal_path = os.path.join(slot, "REFUSAL.json")
    call_path = os.path.join(slot, "CALL.json")
    relative = os.path.relpath(slot, STUDY)
    if not os.path.islink(refusal_path) and os.path.isfile(refusal_path):
        refusal = _load_json(refusal_path)
        if not isinstance(refusal, dict):
            raise BatchError("%s/REFUSAL.json is not a JSON object" % relative)
        status, code = refusal.get("wrapperExit"), refusal.get("code")
        if not isinstance(status, int) or isinstance(status, bool):
            raise BatchError("%s/REFUSAL.json records wrapperExit %r, and the "
                             "registration registers an integer exit status"
                             % (relative, status))
        # `wrapper_code()` and not `WRAPPER_CODES.get(..., "wrapper-error")`:
        # a record naming a status this wrapper never returns refuses the whole
        # scoring (R1-4), instead of being compared against a sentinel that is in
        # no partition and would then travel into a denominator.
        expected = wrapper_code(status)
        if code != expected:
            raise BatchError(
                "%s/REFUSAL.json records code %r for wrapper exit %d, and this "
                "driver writes %r for that status: the refusal record is not one "
                "this batch produced" % (relative, code, status, expected))
        if code is not None and code not in CODE_PARTITION:
            raise BatchError(
                "%s/REFUSAL.json records the code %r, which is on neither side "
                "of §1a's partition: a slot wearing a code no partition names is "
                "counted by no rule and excluded by none" % (relative, code))
        return status, code
    if not os.path.islink(call_path) and os.path.isfile(call_path):
        return 0, None
    raise BatchError(
        "%s carries neither CALL.json nor REFUSAL.json: it is not a terminal "
        "slot, and no ledger record describes it honestly. Record the cause in "
        "DEVIATIONS.md" % relative)


def slots_on_disk() -> list:
    """Every slot present under every arm's `authoring/`, as sorted
    study-relative paths, counted by the SCORER's own rule.

    `collect_slots()` names an entry `run-NNN` a slot whatever it holds, because
    the NAME is what claims the index. The driver counts the population the same
    way the scoring will, so a reconciliation cannot pass over a slot the scorer
    will then refuse to score."""
    present = []
    for arm in ARMS:
        root = os.path.join(ARMS_ROOT, arm, "authoring")
        if not os.path.isdir(root):
            continue
        slots, _unexpected = collect_slots(root)
        present.extend(os.path.relpath(path, STUDY) for path in slots)
    return sorted(present)


def reconcile_ledger(records: list, entries: list) -> dict:
    """The ONE ledger record a crash between the seal and the ledger write can
    leave unwritten, completed from that slot's own seal — or None when the
    ledger and the slots on disk already agree. Any other disagreement is a
    BatchError naming it exactly.

    The driver seals a slot and then appends its ledger record, so there is a
    window in which a slot is sealed and the ledger does not name it. A kill
    inside that window otherwise leaves a batch that can neither be resumed
    (`--resume` plans the orphan's index again and refuses its existing path) nor
    declared short (the declaration's two counts disagree and the scorer refuses
    it). The batch is stuck with no registered way forward.

    **The slot RAN.** That is the whole of the reasoning, and it is why completing
    the record is not the same as inventing one: the wrapper returned, the driver
    wrote the refusal record and the schedule stamps, and the driver sealed the
    tree — every one of those precedes the ledger append, and the seal is the
    evidence that all of them happened. Only the bookkeeping was interrupted.
    Nothing is re-run, no call is spent, and every member of the completed record
    is READ from the slot.

    The conditions are narrow on purpose, and each refuses rather than guesses:
    the orphan is the NEXT scheduled slot and nothing further ahead; there is
    exactly ONE; its manifest VERIFIES; and every recorded slot is still on disk.
    The reconciliation is over every slot PRESENT, not over the canonical paths
    the order would name next, so a slot at an index the registered order never
    assigns refuses here rather than being discovered after the calls."""
    for offset, record in enumerate(records):
        path = record.get("path")
        if not isinstance(path, str) or not path:
            raise BatchError(
                "ledger record %d names no slot path (%r): the ledger and the "
                "slot set are in bijection at the path the record names, and a "
                "record that names none cannot be reconciled with anything. "
                "Record the cause in DEVIATIONS.md" % (offset + 1, path))
    recorded = [os.path.normpath(record["path"]) for record in records]
    missing = [path for path in recorded
               if not os.path.lexists(os.path.join(STUDY, path))]
    if missing:
        raise BatchError(
            "the ledger records %d slot(s) that are not on disk (%s): a ledger "
            "record with no slot is not a crash this driver can have caused, and "
            "the scorer refuses the whole scoring over it. Record the cause in "
            "DEVIATIONS.md" % (len(missing), ", ".join(missing)))
    orphans = [entry for entry in entries[len(records):]
               if os.path.lexists(slot_path(entry))]
    if len(orphans) > 1:
        raise BatchError(
            "%d slots past the ledger's last record exist on disk (global indices "
            "%s) and the ledger records none of them. The seal-then-record window "
            "can leave at most ONE, so this is not an interrupted append: no slot "
            "is admitted to the ledger from it, and the cause goes in "
            "DEVIATIONS.md"
            % (len(orphans), ", ".join(str(entry["globalIndex"]) for entry in orphans)))
    permitted = set(recorded)
    if orphans:
        permitted.add(os.path.relpath(slot_path(orphans[0]), STUDY))
    unaccounted = [path for path in slots_on_disk() if path not in permitted]
    if unaccounted:
        raise BatchError(
            "%d slot(s) are on disk that the ledger does not record and §2's "
            "registered order does not put next (%s): the seal-then-record window "
            "leaves exactly ONE slot, at the next registered index, so this is "
            "not that window. No call is made and no record is completed from it "
            "— the slots go, or the cause goes in DEVIATIONS.md"
            % (len(unaccounted), ", ".join(unaccounted)))
    if not orphans:
        return None
    entry = orphans[0]
    if entry["globalIndex"] != entries[len(records)]["globalIndex"]:
        raise BatchError(
            "a slot exists at global index %d and the ledger ends at %d: the "
            "driver runs the registered order one slot at a time, so a slot past "
            "the next index was not left by an interrupted append. Record the "
            "cause in DEVIATIONS.md"
            % (entry["globalIndex"], records[-1]["globalIndex"] if records else 0))
    slot = slot_path(entry)
    if os.path.islink(slot) or not os.path.isdir(slot):
        raise BatchError(
            "%s exists and is not a directory, so it is not a sealed slot this "
            "driver left: slots already on disk are never rewritten, and this one "
            "must be removed by hand with the cause recorded in DEVIATIONS.md"
            % os.path.relpath(slot, STUDY))
    manifest = verify_seal_of(slot, entry)
    status, code = slot_outcome(slot)
    previous = record_digest(records[-1]) if records else None
    return ledger_record(entry, slot, status, code, manifest, previous)


# --- D7: the batch -----------------------------------------------------------

def run_batch(runs: int, resume: bool, scratch_parent: str, pins_path: str,
              cli_override: str, dry_run: bool,
              golden_override: str = None) -> int:
    cli_override = resolve_cli(cli_override)
    entries = schedule_entries()
    records = load_ledger()
    verify_prefix(records, entries)
    done = len(records)
    if records and not resume:
        raise BatchError(
            "%s already records %d slots: a batch is continued with `run "
            "--resume`, which resumes at global index %d, and never restarted"
            % (os.path.join(ARMS_ROOT, LEDGER_NAME), done, done + 1))
    # The crash window the seal-then-record order leaves open, closed on the
    # resume that follows it: a slot sealed and not yet recorded is completed
    # from its seal, and any other disagreement between the ledger and the slots
    # on disk refuses here rather than being planned over. `--resume` only: a
    # plain `run` over retained slots is a restart, and no slot is ever rewritten.
    recovered = reconcile_ledger(records, entries) if resume else None
    if recovered is not None:
        records.append(recovered)
        verify_prefix(records, entries)
        done = len(records)
        if not dry_run:
            # The completed record enters the ledger under the same preconditions
            # a call does: the ported bytes, the freeze, and the
            # no-slots-after-a-rate rule. It is written BEFORE anything else so
            # that a resume with nothing left to run still leaves the ledger whole.
            if os.path.exists(ATTEMPT_ROOT):
                raise BatchError(
                    "%s exists: no ledger record may be completed after a rate "
                    "has been computed, any more than a slot may be created"
                    % os.path.relpath(ATTEMPT_ROOT, STUDY))
            verify_ported_bytes()
            recovery_pins = load_registry(pins_path)
            write_ledger(records, recovery_pins, cli_override)
        print("%s the ledger record for global index %d from its seal: the slot "
              "ran and only the append was interrupted"
              % ("dry run: would complete" if dry_run else "completed",
                 recovered["globalIndex"]))
    if resume and not records:
        raise BatchError(
            "--resume was given and the ledger records no slot: there is nothing "
            "to resume at, and the first invocation of a batch is `run` without it")
    remaining = entries[done:]
    if not remaining:
        raise BatchError(
            "the registered order is complete: all %d slots are in the ledger, "
            "and no batch may be extended (§2)" % REGISTERED_SLOTS)
    if runs is not None:
        if runs < 1:
            raise BatchError("a batch needs at least one run")
        if runs > len(remaining):
            raise BatchError(
                "--runs %d asks for more slots than the registered order has "
                "left: %d of %d are in the ledger and %d remain. The order is "
                "fixed before the batch, so an invocation that would reach past "
                "global index %d is refused before a call is spent"
                % (runs, done, REGISTERED_SLOTS, len(remaining), REGISTERED_SLOTS))
        remaining = remaining[:runs]
    slots = [slot_path(entry) for entry in remaining]
    pins = preflight(remaining, slots, scratch_parent, pins_path, cli_override,
                     "registered", golden_override)
    if dry_run:
        print("dry run: %d slots, none created" % len(slots))
        print("  model      %s" % pins["codex"]["model"])
        print("  binary     %s" % pins["codex"]["binarySha256"])
        for arm in ARMS:
            print("  prompt %s   %s" % (arm, arm_prompt(pins, arm)[1]))
        print("  golden     %s" % (pins.get("golden") or {}).get("sha256"))
        print("  ceiling    %d s (grace %d s)"
              % (CALL_TIMEOUT_SECONDS, TIMEOUT_KILL_AFTER_SECONDS))
        print("  wrapper    %s" % SCRIPT)
        print("  cli        %s" % (cli_override or "codex on PATH"))
        for entry, slot in zip(remaining, slots):
            print("  would create %s (global %d, round %d, position %d, arm %s)"
                  % (os.path.relpath(slot, STUDY), entry["globalIndex"],
                     entry["round"], entry["position"], entry["arm"]))
        return 0
    os.makedirs(ARMS_ROOT, exist_ok=True)
    # The digest preflight verified, stamped into every slot this invocation
    # makes: a golden swapped after the batch changes the pin, and every slot
    # then names a digest that is not the pin it is being scored under.
    golden_pin = (pins.get("golden") or {}).get("sha256")
    # …and the capture itself, which `preflight()` has already verified against
    # that pin. The per-slot transcript binding needs the BYTES, not the digest.
    golden_file = golden_path_for(pins, golden_override)
    previous = record_digest(records[-1]) if records else None
    for entry, slot in zip(remaining, slots):
        status, code, stderr = invoke(slot, scratch_parent, pins_path, cli_override,
                                      "registered", entry["arm"],
                                      arm_prompt(pins, entry["arm"])[0],
                                      golden_sha256=golden_pin)
        # Refusal record, then the schedule stamps, then the transcript binding,
        # then the seal, then the ledger. The order is the registered one and
        # each step is a reason for the next: the refusal record is part of the
        # slot and the schedule stamps are part of CALL.json, so both must be
        # written before the manifest that seals them; the binding reads the
        # stamped CALL.json and writes its verdict into the slot, so it comes
        # after the stamps and before the seal; and the ledger record carries the
        # manifest's digest, so it is appended after the seal exists.
        if code is not None:
            refuse_slot(slot, code, status, stderr)
        stamp_slot(slot, entry, pins)
        # R1-5: only a slot the wrapper completed. A refused slot already carries
        # an apparatus code that says why, and half its bytes are missing by
        # construction — binding it would say "unreadable" over a fact the
        # refusal record already states more precisely.
        bound = None
        if code is None:
            bound = bind_transcript(slot, entry, pins, golden_file)
        manifest = seal_slot(slot, entry)
        records.append(ledger_record(entry, slot, status, code, manifest, previous))
        previous = record_digest(records[-1])
        write_ledger(records, pins, cli_override)
        print("%03d %s %s: exit %d%s%s"
              % (entry["globalIndex"], entry["arm"], os.path.basename(slot), status,
                 "" if code is None else " (%s)" % code,
                 "" if bound is None or bound["admissible"]
                 else " [transcript %s: %s]" % (bound["side"], bound["reason"])))
    made = records[done:]
    refused = [row for row in made if row["code"] is not None]
    print("batch: %d slots this invocation (%d refused), %d of %d in the ledger"
          % (len(made), len(refused), len(records), REGISTERED_SLOTS))
    return 0


# --- G1: the golden context --------------------------------------------------

def capture_slots(directory: str) -> list:
    """Every retained slot beneath a directory that has a session and a call
    record, in name order. Capture slots are not batch slots, are not named
    `run-NNN`, and never enter any denominator — a directory named `run-<digits>`
    refuses outright, so a golden capture can never be derived from the batch's
    own runs."""
    if not os.path.isdir(directory):
        raise BatchError("%s is not a directory" % directory)
    found = []
    for name in sorted(os.listdir(directory)):
        path = os.path.join(directory, name)
        parts = name.split("-", 1)
        if os.path.isdir(path) and len(parts) == 2 and parts[0] == "run" \
                and parts[1].isdigit():
            raise BatchError(
                "%s holds the batch slot %s: a golden capture is derived from "
                "probe captures taken before the batch, never from the batch's "
                "own runs" % (directory, name))
        if os.path.isdir(path) and not os.path.islink(path) \
                and os.path.isfile(os.path.join(path, "session.jsonl")) \
                and os.path.isfile(os.path.join(path, "CALL.json")):
            found.append(path)
    return found


def capture_identity(slot: str) -> dict:
    """The raw retained evidence of WHICH call produced this capture.

    Raw, deliberately: the session file's bytes, the session id, and the call
    record's own wall clock, working directory and isolated home. Not the
    normalized context digests — those are what two independent calls are
    SUPPOSED to share."""
    call = _load_json(os.path.join(slot, "CALL.json"))
    return {
        "slot": os.path.basename(slot),
        "sessionSha256": _digest(os.path.join(slot, "session.jsonl")),
        "sessionId": session_identity(os.path.join(slot, "session.jsonl")),
        # A DIGEST, not the values. The four members distinguish two calls as
        # well as their raw forms do -- equality of digests is equality of
        # tuples -- but cwd and home are the operator's absolute paths, and this
        # record is written into transcription/GOLDEN-CONTEXT.json, a committed
        # artifact with a freeze pin. C7_REDACTED already states the study's
        # rule for retained artifacts: every member that names the machine is
        # dropped before the file is written into the study. An earlier form of
        # this line retained the raw tuple, and the independent mutation audit
        # (G10) demonstrated a test positively requiring the operator's paths in
        # a committed file. Distinctness survives; the paths do not.
        "callIdentity": _digest_text("\x1f".join(
            str(call.get(member)) for member in
            ("startedAt", "endedAt", "cwd", "home"))),
    }


def require_distinct_sessions(identities: list) -> None:
    """Every capture slot is a different call, or BatchError naming the pair.

    The hole this closes: counting slots and comparing normalized contexts lets
    two slots holding ONE call's evidence — a copied directory, or one transcript
    retained twice — agree perfectly and derive an allowlist from a context that
    had never been shown to reproduce. The floor of two is a floor of two
    INDEPENDENT calls."""
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
                    "agree by construction rather than by reproduction"
                    % (first["slot"], second["slot"], prose, first[member]))


def _identity_value(record: dict, member: str):
    """One `CAPTURE_IDENTITY` member off a RETAINED identity record, in a form
    two records can be compared on. Every member is a string today —
    `callIdentity` became a digest when the raw start/end/cwd/home tuple was
    found retained in a committed artifact (mutation audit G10) — but a record
    written by the earlier form round-trips its tuple through JSON as a list,
    so a list is still read as a tuple rather than misread as unequal to
    itself."""
    value = record.get(member)
    return tuple(value) if isinstance(value, list) else value


def golden_provenance_problems(document: dict) -> list:
    """The retained golden capture's own provenance, re-checked from its bytes.
    Returns a list of problem strings; empty means the document CARRIES the
    evidence for the derivation it claims.

    The gap this closes is a gap in the RECORD, not in the derivation.
    `capture_golden()` already enforces the floor of two and
    `require_distinct_sessions()` already checks it on raw retained evidence —
    that half is sound, and stronger than the `sessionId`-only rule the archived
    apparatus line proposed. What the committed artifact used to record was
    `capturedFrom` (slot BASENAMES) and `capturedIn` (a directory basename), and
    the source captures live outside the study tree at an operator-named path.
    So "two agreeing captures from distinct sessions" was true of the run and
    uncheckable from any retained byte — exactly the diagnosis the archived line
    made of Study 012, which retained only the derived file and whose
    `capturedFrom` names two captures that are not in its tree. This study was
    about to publish the same shape. `capture_golden()` now writes the
    `identities` list it already computes, and this function is what reads it.

    Two departures from `require_distinct_sessions()`, both deliberate:

    * A NULL identity member is a problem here, where there it is skipped. There
      the check is live and the other members still discriminate; here the
      question is whether the retained bytes SHOW the claim, and a member that is
      absent shows nothing. The archived line's `derive_golden` refused a capture
      with no `sessionId` for this reason — "a check that silently skips is worse
      than one that stops" — and that is the half of it worth carrying.
    * `capturedFrom` and the identity list must name the same slots in the same
      order. They are two claims by one document about one derivation, and a
      document that disagrees with itself is not evidence for either.

    Pure: it reads a parsed document and touches no disk. **It is not wired into
    `score.golden_context_gate()` yet** — see PREREG-REVIEW.md's salvage-audit
    section for why that wiring is the round-4 response's and not this one's."""
    problems = []
    if not isinstance(document, dict):
        return ["the golden capture is not a JSON object"]
    identities = document.get("capturedIdentities")
    if not isinstance(identities, list):
        return ["the golden capture records no capturedIdentities list: its "
                "derivation from %d independent calls is asserted rather than "
                "checkable from any retained byte" % MIN_CAPTURE_SLOTS]
    if len(identities) < MIN_CAPTURE_SLOTS:
        problems.append(
            "the golden capture records %d capture identit%s; a derivation needs "
            "at least %d, because one capture cannot show that a pre-prompt "
            "context reproduces"
            % (len(identities), "y" if len(identities) == 1 else "ies",
               MIN_CAPTURE_SLOTS))
    for index, record in enumerate(identities):
        if not isinstance(record, dict):
            problems.append("capture identity %d is not an object" % index)
            continue
        if not record.get("slot"):
            problems.append("capture identity %d names no slot" % index)
        for member, prose in CAPTURE_IDENTITY:
            if _identity_value(record, member) is None:
                problems.append(
                    "capture identity %d (%s) carries no value for %s: the derivation's "
                    "independence cannot be checked on a member the record does "
                    "not carry"
                    % (index, record.get("slot"), prose))
    usable = [record for record in identities if isinstance(record, dict)]
    for index, first in enumerate(usable):
        for second in usable[index + 1:]:
            for member, prose in CAPTURE_IDENTITY:
                value = _identity_value(first, member)
                if value is None or value != _identity_value(second, member):
                    continue
                problems.append(
                    "captures %s and %s share %s (%r): they are one call's "
                    "evidence recorded twice, and two copies of one call agree "
                    "by construction rather than by reproduction"
                    % (first.get("slot"), second.get("slot"), prose, value))
    captured_from = document.get("capturedFrom")
    if isinstance(captured_from, list):
        named = [record.get("slot") for record in usable]
        if named != list(captured_from):
            problems.append(
                "the golden capture's capturedFrom (%r) and its recorded capture "
                "identities (%r) name different slots: one document making two "
                "claims about one derivation is evidence for neither"
                % (captured_from, named))
    return problems


def capture_golden(slots_dir: str, out_path: str, min_slots: int,
                   pins_path: str = DEFAULT_PINS) -> int:
    """Derive this study's golden pre-prompt context from retained capture slots.

    Study 010 locked a capture taken from two independent real runs that
    reproduced identically, and 011 and 012 repeated that procedure in their own
    environments; this repeats it again here, because a golden capture pins one
    machine's codex boilerplate and an inherited one would refuse every honest
    run. The captures must AGREE — a context that varies run to run cannot be an
    allowlist — and none of them may carry a leak token before the prompt, or the
    capture would bless a planted turn. ONE capture serves all three arms: the
    pre-prompt context precedes the prompt and does not depend on it, which is the
    property that made the probe-prompt capture legitimate in the first place and
    does not become three properties because there are three prompts.

    **A capture-after-the-batch scores GOLDEN-MISMATCH; it does not redefine the
    golden.** That is enforced structurally rather than by instruction: this
    command refuses to rewrite an existing capture, `require_golden()` compares
    every batch against the registry pin, and the pin is stamped into each slot's
    own `CALL.json` at call time — so a second capture written after slots exist
    is a new file at a new path that the registry does not pin, and every slot
    made under the old one still names the old one. The gate a re-capture can
    only ever move is a slot's own comparison, which is the apparatus code
    `golden-context-mismatch`.

    The two-capture rule is enforced HERE, where the derivation happens, and not
    only in the command that makes the calls: `MIN_CAPTURE_SLOTS` is a floor, so
    `--min-slots 1` refuses rather than deriving an allowlist from a single
    unreproduced context — and the two must be two independent CALLS, which
    `require_distinct_sessions()` checks on the raw retained evidence rather than
    on the normalized digests two honest calls are supposed to share.

    It runs the same preflight the command that makes the calls runs — the ported
    bytes, the registered interpreter, and the freeze — because this half derives
    the artifact every later admission is checked against. And it requires every
    capture slot to be a PROBE call at the pinned probe-prompt digest: a name is
    not evidence of which prompt was answered, and a golden derived from an arm's
    own runs would pin a context the operator had already seen coverage profiles
    from."""
    if not out_path:
        raise BatchError("--out is required: a golden capture is written where "
                         "the operator names it, never into the study tree by "
                         "default")
    if os.path.exists(out_path):
        raise BatchError("%s already exists; a registered capture is never "
                         "rewritten" % out_path)
    require_lawful_destination(out_path, "--out", is_file=True)
    if min_slots < MIN_CAPTURE_SLOTS:
        raise BatchError(
            "a golden capture is derived from at least %d agreeing captures and "
            "--min-slots %d asks for fewer: one capture cannot show that a "
            "pre-prompt context reproduces, and a context that might vary is not "
            "an allowlist" % (MIN_CAPTURE_SLOTS, min_slots))
    verify_ported_bytes()
    pins = load_registry(pins_path)
    probe_pin = (pins.get("probePrompt") or {}).get("sha256")
    if not probe_pin:
        raise BatchError("%s pins no probePrompt.sha256: a capture is derived "
                         "only from runs of the registered probe prompt" % pins_path)
    usable, contexts, identities = [], [], []
    for slot in capture_slots(slots_dir):
        session = os.path.join(slot, "session.jsonl")
        call = _load_json(os.path.join(slot, "CALL.json"))
        if call.get("promptKind") != "probe" or call.get("promptSha256") != probe_pin:
            raise BatchError(
                "capture %s records promptKind %r and prompt %r: a golden capture "
                "is derived only from calls that answered the registered PROBE "
                "prompt (%s). Running an arm's prompt before the batch would show "
                "the operator coverage profiles first"
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
        raise BatchError("a capture needs at least %d capture slots with a "
                         "session; found %d" % (required, len(usable)))
    # …and they are that many CALLS: agreement between two copies of one
    # transcript is not reproduction. Checked before the contexts are compared,
    # because a duplicate agrees by construction and the comparison below would
    # report success.
    require_distinct_sessions(identities)
    first = contexts[0]
    for name, context in zip(usable[1:], contexts[1:]):
        if context != first:
            raise BatchError("capture %s does not reproduce %s's pre-prompt "
                             "context; a varying context cannot be an allowlist"
                             % (name, usable[0]))
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    _write_json(out_path, {
        "contextVersion": first["contextVersion"],
        "entries": first["entries"],
        "capturedFrom": usable,
        # The evidence for the sentence above, retained rather than asserted.
        # `require_distinct_sessions()` has just checked these; writing them is
        # what lets a reader — and `golden_provenance_problems()` — check the
        # same thing later, from the committed file alone. The source capture
        # slots live outside the study tree at an operator-named path, so
        # without this the derivation was a claim no retained byte supported.
        "capturedIdentities": identities,
        "capturedIn": os.path.basename(os.path.abspath(slots_dir)),
        "note": "The pre-prompt context of this study's registered invocations, "
                "captured from independent probe-prompt runs that reproduced "
                "identically after normalization. One capture serves all three "
                "arms. Any deviation in a batch run's context scores that run "
                "golden-context-mismatch — an APPARATUS code (§1a) — and a "
                "capture taken after the batch cannot redefine this one: it is a "
                "new file the registry does not pin, and every slot names the "
                "digest it was made under. Its digest goes into harness/PINS.json "
                "golden.sha256 and both are committed before round 1.",
    })
    print("captured: %d entries from %d agreeing captures"
          % (len(first["entries"]), len(usable)))
    print("next: put %s into harness/PINS.json golden.sha256 and commit both "
          "before the first slot" % _digest(out_path))
    return 0


def next_attempt(captures_dir: str) -> str:
    """`controls/recapture/attempt-N/`, the next unused N.

    A disagreeing recapture may be repeated after the environmental cause is
    fixed. A repeat needs somewhere to go: slots are never rewritten, so attempt
    2 is its own directory and every attempt stays published."""
    used = []
    if os.path.isdir(captures_dir):
        for name in os.listdir(captures_dir):
            parts = name.split("-", 1)
            if len(parts) == 2 and parts[0] == "attempt" and parts[1].isdigit():
                used.append(int(parts[1]))
    return os.path.join(captures_dir, "attempt-%d" % ((max(used) + 1) if used else 1))


def run_capture(runs: int, captures_dir: str, out_path: str, scratch_parent: str,
                pins_path: str, cli_override: str) -> int:
    """The recapture, end to end: N probe calls into a numbered attempt
    directory, then the derivation.

    The probe prompt — not any arm's — is deliberate. The pre-prompt context
    precedes the prompt and does not depend on it, and running an arm's prompt
    here would show the operator coverage profiles before the batch. It is also
    what makes ONE recapture serve three arms: the probe's bytes are
    arm-independent by construction."""
    cli_override = resolve_cli(cli_override)
    if os.path.exists(out_path):
        raise BatchError("%s already exists; a registered capture is never "
                         "rewritten" % out_path)
    if runs < MIN_CAPTURE_SLOTS:
        # Before a single call is spent: a recapture that could only produce one
        # context could never derive a capture from it.
        raise BatchError(
            "the recapture makes at least %d probe calls and --runs %d asks for "
            "fewer: the capture is derived only from contexts that agree, so one "
            "call could never produce one" % (MIN_CAPTURE_SLOTS, runs))
    # `--captures DIR` is an operator-named destination like the two `--out`s,
    # and the attempts retained beneath it are bytes a manifest could cover. The
    # check is made before the attempt directory is planned, so nothing is
    # created by a refused capture.
    require_lawful_destination(captures_dir, "--captures")
    attempt = next_attempt(captures_dir)
    slots = plan(runs, 1, attempt, stem="capture")
    preflight([], slots, scratch_parent, pins_path, cli_override, "probe")
    os.makedirs(attempt, exist_ok=True)
    print("capture attempt: %s" % attempt)
    for slot in slots:
        status, code, stderr = invoke(slot, scratch_parent, pins_path, cli_override,
                                      "probe", PROBE_ARM, PROBE_PROMPT)
        if code is not None:
            refuse_slot(slot, code, status, stderr)
            raise BatchError("capture %s failed (%s); the batch does not start "
                             "until two captures agree. Fix the cause and run "
                             "capture again: the next attempt gets its own "
                             "directory." % (os.path.basename(slot), code))
        print("%s: exit %d" % (os.path.basename(slot), status))
    return capture_golden(attempt, out_path, runs, pins_path)


# --- G2: the isolation negative control --------------------------------------

def capture_isolation_negative(out_dir: str, scratch_parent: str, pins_path: str,
                               cli_override: str, golden_override: str) -> int:
    """§6's negative control: the isolation gate's power, demonstrated rather
    than assumed.

    ONE probe call with the operator's REAL home — everything else exactly as
    registered — whose registered expectation is that it FAILS the golden match.
    If it matches instead, the gate has no demonstrated power against home
    leakage in this environment; that is recorded and the batch proceeds
    unchanged. Registering both outcomes before the batch is what keeps this a
    control rather than a decision. It runs ONCE for the whole batch, not per
    arm: it uses the probe prompt and tests home leakage, neither of which
    depends on which representation an arm carries.

    **It runs only under RECORDED OPERATOR ASSENT and refuses otherwise.** The
    member is `isolationNegative.assent`, spelled exactly as the registry spells
    it — Study 012's round 3 found the driver reading `operatorAssent` while the
    registry recorded `assent`, so granting assent where the registry records it
    left the control refusing and granting it where the code looked would have
    run the control with the registry recording nothing.

    THREE outcomes are registered, not two: `refused` (the expectation),
    `matched` (the limitation), and `no-context` — the call produced nothing
    comparable, so neither comparison happened. `no-context` returns NON-ZERO: it
    is a control that did not run, and returning 0 for it would report a step as
    done that reached neither registered comparison. Its verdict is still
    retained, so the failure is on disk rather than only in a shell's exit status.

    Retention is done by code, not by the operator's care: the call is made into a
    scratch slot, and the only bytes that reach the study are the comparison
    verdict, a CALL.json stripped of every member that names or enumerates the
    operator's environment, and — when the call produced one — the context
    digests. session.jsonl, stdout.raw and stderr.raw are digested and deleted
    here; publishing the transcript of a non-isolated run would publish an
    inventory of the operator's own machine, which is the thing the control exists
    to detect. The deletion is VERIFIED, not attempted.

    The control's slot is not a slot of the registered order, so it carries no
    schedule stamps and is not sealed into the ledger: it is a control, it enters
    no denominator, and the chain is over the batch."""
    cli_override = resolve_cli(cli_override)
    verify_ported_bytes()
    pins = load_registry(pins_path)
    assent = (pins.get("isolationNegative") or {}).get("assent")
    if assent != "granted":
        raise BatchError(
            "harness/PINS.json records isolationNegative.assent %r: this is the "
            "one registered step that exposes the operator's real environment to "
            "the pinned CLI and it runs only with recorded assent (§6)" % (assent,))
    if not os.path.isdir(scratch_parent):
        raise BatchError("scratch parent %s is not a directory" % scratch_parent)
    golden = require_golden(pins, golden_override)
    if os.path.exists(out_dir):
        raise BatchError("%s already exists; a registered control is never "
                         "rewritten" % out_dir)
    # A TREE here, not a file: the record is a directory, so every path beneath
    # it has to be somewhere the manifest does not reach.
    require_lawful_destination(out_dir, "--out")
    raw = os.path.join(scratch_parent, "s020-c7-raw-%d" % os.getpid())
    if os.path.exists(raw):
        raise BatchError("%s already exists" % raw)
    status, code, stderr = invoke(raw, scratch_parent, pins_path, cli_override,
                                  "probe", PROBE_ARM, PROBE_PROMPT,
                                  isolation="operator-home")
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
                    "the non-isolated call reproduced the golden pre-prompt "
                    "context: the golden gate has no demonstrated power against "
                    "home leakage in this environment (§6, recorded as a "
                    "limitation)")
            except transcript_check.TranscriptError as error:
                outcome, message = "refused", str(error)
        else:
            outcome, message = "no-context", (
                "the control produced no comparable context (wrapper exit %d, "
                "code %r): neither registered comparison happened and the gate's "
                "power is undemonstrated" % (status, code))
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
        stripped["note"] = ("The control's CALL.json, stripped by batch.py of "
                            "every member that names or enumerates the operator's "
                            "real environment. The transcript was digested and "
                            "deleted, not retained.")
        _write_json(os.path.join(out_dir, "CALL.json"), stripped)
        _write_json(os.path.join(out_dir, "VERDICT.json"), {
            "control": "the isolation gate's power",
            "registeredExpectation": "the golden match FAILS",
            "registeredOutcomes": list(C7_OUTCOMES),
            "outcome": outcome,
            "message": message,
            "wrapperExit": status,
            "wrapperCode": code,
            "goldenSha256": _digest(golden),
            "deletedByCode": digests,
            # The registry member this call was authorized by, under the
            # registry's own name for it: one member name in the registry, in
            # the driver and in the retained verdict.
            "assent": assent,
            "retention": "This file and a stripped CALL.json are always retained, "
                         "and context.json whenever the call produced a "
                         "comparable context (outcome 'no-context' is the case "
                         "where it did not). session.jsonl, stdout.raw, "
                         "stderr.raw and any completion were digested above and "
                         "deleted by batch.py, and the deletion is verified: "
                         "publishing the transcript of a deliberately "
                         "non-isolated run would publish an inventory of the "
                         "operator's environment.",
        })
    finally:
        # Every exit from the block above passes here, including the ones already
        # carrying an exception — so the warning is printed on all of them and
        # the refusal is raised on the one that would otherwise report success.
        shutil.rmtree(raw, ignore_errors=True)
        if os.path.exists(raw):
            print("WARNING: the control's scratch slot %s survived removal" % raw,
                  file=sys.stderr)
    if os.path.exists(raw):
        raise BatchError(
            "the control's scratch slot %s survived removal: its transcript is an "
            "inventory of the operator's environment and is still on disk. Remove "
            "it by hand and record the cause in DEVIATIONS.md before publishing "
            "anything from %s" % (raw, out_dir))
    print("isolation negative: %s — %s" % (outcome, message))
    print("retained under %s: %s" % (out_dir, ", ".join(sorted(os.listdir(out_dir)))))
    if outcome == "no-context":
        print("refused: the control reached neither registered comparison; its "
              "verdict is retained and the gate's power is undemonstrated",
              file=sys.stderr)
        return 1
    return 0


# --- D8: the shortfall -------------------------------------------------------

# R1-7. The declaration used to be a bag of counts, and the scorer accepted ANY
# JSON object — `{}` included — as the thing that makes an incomplete batch
# terminal. Nothing tied the file to the ledger, to the seals, or to the
# registered order, so an operator could delete slots by outcome, declare the
# remainder short, and be scored on it.
#
# The declaration is a SCHEMA now, and the schema carries evidence rather than
# summary: the ledger's file digest and chain head, the full slot/seal inventory,
# and the declared prefix, each of which the scorer recomputes against the bytes
# on disk. `validate_shortfall()` is the schema and the internal consistency;
# `verify_shortfall()` is the comparison against the ledger. The driver runs both
# ON WRITE — a declaration it could not validate is not written — and the scorer
# runs both on read. One definition, two callers.
SHORTFALL_VERSION = "1"

# member -> the type(s) it must have. `None` in a tuple means the member may be
# null, and only where a null is a fact (an empty prefix has no last slot).
SHORTFALL_SCHEMA = {
    "declarationVersion": (str,),
    "registeredRounds": (int,),
    "registeredRunsPerArm": (int,),
    "registeredSlots": (int,),
    "completedRounds": (int,),
    "completedThroughGlobalIndex": (int,),
    "completedSlots": (int,),
    "ledgerSha256": (str, type(None)),
    "ledgerHeadSha256": (str, type(None)),
    "slots": (list,),
    "lastSlot": (str, type(None)),
    "lastSlotEndedAt": (str, type(None)),
    "lastSlotEndedAtFrom": (str, type(None)),
    "reason": (str,),
    "note": (str,),
}

# …and the members of one row of the inventory. Every one of them is READ from
# the slot's own ledger record, and every one is checkable against the retained
# bytes: the schedule keys against §2's expansion, the path against `slot_path()`,
# the seal against a recomputed `SLOT-MANIFEST.json`, the code against §1a.
SHORTFALL_SLOT_SCHEMA = {
    "globalIndex": (int,),
    "round": (int,),
    "position": (int,),
    "arm": (str,),
    "slotIndex": (int,),
    "path": (str,),
    "manifestSha256": (str,),
    "wrapperExit": (int,),
    "code": (str, type(None)),
}


def _typed(where: str, body: dict, schema: dict) -> None:
    """Every member of `schema` present in `body` at one of its types, and no
    member of `body` the schema does not name. Both directions: a missing member
    is a declaration that says less than the registration requires, and an extra
    one is a declaration carrying something nobody checks."""
    if not isinstance(body, dict):
        raise BatchError("%s is a JSON %s and the declaration schema registers "
                         "an object" % (where, type(body).__name__))
    for member, types in sorted(schema.items()):
        if member not in body:
            raise BatchError(
                "%s carries no %s member: the declaration is what makes an "
                "incomplete batch terminal, and one that omits a registered "
                "member declares less than the registration requires (R1-7)"
                % (where, member))
        if isinstance(body[member], bool) or not isinstance(body[member], types):
            raise BatchError(
                "%s records %s as a JSON %s and the schema registers %s"
                % (where, member, type(body[member]).__name__,
                   " or ".join(kind.__name__ for kind in types)))
    extra = sorted(set(body) - set(schema))
    if extra:
        raise BatchError(
            "%s carries members the declaration schema does not name (%s): a "
            "member nobody checks is a member nobody can rely on"
            % (where, ", ".join(extra)))


def validate_shortfall(declaration, entries: list = None) -> None:
    """The declaration's SCHEMA and its internal consistency — no ledger needed.

    What it establishes, and why each one is here rather than left to a reader:

    * every registered member is present, at its registered type, and no
      unregistered member is;
    * the registered constants in it are §2's, so a declaration written by
      another study's driver or another batch shape refuses;
    * `slots` is a PREFIX of §2's registered order: global indexes 1..n with no
      gap and no repeat, each row's schedule keys equal to the order's at that
      position, and each row's path the one `slot_path()` assigns it. This is
      what makes outcome-selective deletion visible — a set of slots chosen by
      what they contained is not a prefix;
    * every row's code is on one side of §1a's partition (R1-4);
    * the counts are DERIVED from `slots` rather than asserted beside it:
      `completedSlots`, `completedThroughGlobalIndex`, `completedRounds` and
      `lastSlot` all have to equal what the inventory says, so no count can
      disagree with the evidence under it."""
    _typed(SHORTFALL_NAME, declaration, SHORTFALL_SCHEMA)
    if declaration["declarationVersion"] != SHORTFALL_VERSION:
        raise BatchError(
            "%s declares version %r and this driver writes version %r: a "
            "declaration of another shape is not read as this one"
            % (SHORTFALL_NAME, declaration["declarationVersion"],
               SHORTFALL_VERSION))
    for member, registered in (("registeredRounds", ROUNDS),
                               ("registeredRunsPerArm", RUNS_PER_ARM),
                               ("registeredSlots", REGISTERED_SLOTS)):
        if declaration[member] != registered:
            raise BatchError(
                "%s records %s %r and §2 registers %d: the declaration is about "
                "THIS registered order"
                % (SHORTFALL_NAME, member, declaration[member], registered))
    if not declaration["reason"].strip():
        raise BatchError("%s declares an empty reason: a shortfall without a "
                         "reason is a gap" % SHORTFALL_NAME)
    slots = declaration["slots"]
    if len(slots) >= REGISTERED_SLOTS:
        raise BatchError(
            "%s inventories %d slots and §2 registers %d: a shortfall declares a "
            "SHORT batch" % (SHORTFALL_NAME, len(slots), REGISTERED_SLOTS))
    entries = schedule_entries() if entries is None else entries
    for offset, row in enumerate(slots):
        where = "%s slot %d" % (SHORTFALL_NAME, offset + 1)
        _typed(where, row, SHORTFALL_SLOT_SCHEMA)
        expected = {key: entries[offset][key] for key in SCHEDULE_KEYS}
        expected["path"] = os.path.relpath(slot_path(entries[offset]), STUDY)
        actual = {key: row[key] for key in SCHEDULE_KEYS}
        actual["path"] = row["path"]
        if actual != expected:
            raise BatchError(
                "%s diverges from §2's registered call order at position %d: it "
                "declares %r and the order assigns %r. A declaration is a PREFIX "
                "of the registered order — a set of slots chosen by what they "
                "contained is not one, and that is the deletion this refuses"
                % (SHORTFALL_NAME, offset + 1, actual, expected))
        if row["code"] is not None and row["code"] not in CODE_PARTITION:
            raise BatchError(
                "%s declares the code %r, which is on neither side of §1a's "
                "partition" % (where, row["code"]))
        if wrapper_code(row["wrapperExit"]) != row["code"]:
            raise BatchError(
                "%s declares wrapper exit %r with the code %r, and this driver "
                "files that status as %r"
                % (where, row["wrapperExit"], row["code"],
                   wrapper_code(row["wrapperExit"])))
    last = slots[-1] if slots else None
    for member, derived in (
            ("completedSlots", len(slots)),
            ("completedThroughGlobalIndex", last["globalIndex"] if last else 0),
            ("completedRounds", completed_rounds(slots)),
            ("lastSlot", last["path"] if last else None)):
        if declaration[member] != derived:
            raise BatchError(
                "%s declares %s %r and its own slot inventory says %r: every "
                "count in a declaration is derived from the inventory under it, "
                "so no count can outlive the evidence"
                % (SHORTFALL_NAME, member, declaration[member], derived))
    if (declaration["ledgerHeadSha256"] is None) != (not slots):
        raise BatchError(
            "%s declares the ledger head %r over %d slots: a non-empty prefix "
            "has a chain head and an empty one has none"
            % (SHORTFALL_NAME, declaration["ledgerHeadSha256"], len(slots)))


def verify_shortfall(declaration, records: list, ledger_sha256: str) -> None:
    """The declaration against the LEDGER it claims to describe.

    `validate_shortfall()` establishes that the declaration is internally
    honest; this establishes that it is honest about something else. The ledger's
    file digest and its chain head are both compared, because they fail in
    different ways: the head moves if any record's content changed, and the file
    digest moves if the file was rewritten around the same records."""
    slots = declaration["slots"]
    if len(records) != len(slots):
        raise BatchError(
            "%s inventories %d slots and the ledger records %d: the declaration "
            "and the ledger are compared slot for slot"
            % (SHORTFALL_NAME, len(slots), len(records)))
    for offset, (row, record) in enumerate(zip(slots, records)):
        declared = {member: row[member] for member in SHORTFALL_SLOT_SCHEMA}
        actual = {member: record.get(member) for member in SHORTFALL_SLOT_SCHEMA}
        if declared != actual:
            raise BatchError(
                "%s's slot %d is not the ledger's record %d: it declares %r and "
                "the ledger holds %r"
                % (SHORTFALL_NAME, offset + 1, offset + 1, declared, actual))
    head = record_digest(records[-1]) if records else None
    if declaration["ledgerHeadSha256"] != head:
        raise BatchError(
            "%s declares the ledger head %r and the chain's last record digests "
            "to %r: the declaration names a ledger this one is not"
            % (SHORTFALL_NAME, declaration["ledgerHeadSha256"], head))
    if declaration["ledgerSha256"] != ledger_sha256:
        raise BatchError(
            "%s declares the ledger file digest %r and %s is %r"
            % (SHORTFALL_NAME, declaration["ledgerSha256"], LEDGER_NAME,
               ledger_sha256))


def completed_rounds(records: list) -> int:
    """The last round every one of whose THREE slots the ledger holds, and
    **zero** when no round is whole.

    Study 012's round 3 finding 15: a declaration that used the LAST SLOT's round
    reported a round that never finished — a batch that died two slots into round
    1 declared one round completed. The count is derived from the prefix here,
    which `verify_prefix()` has already checked against the registered order, so
    "completed" means every slot of that round is on disk and in the chain."""
    counted = {}
    for record in records:
        counted[record.get("round")] = counted.get(record.get("round"), 0) + 1
    whole = 0
    while counted.get(whole + 1) == POSITIONS:
        whole += 1
    return whole


def last_slot_clock(records: list) -> tuple:
    """(the UTC wall clock of the last completed slot, the record it was read
    from) — falling back through the prefix to the last slot that HAS a
    `CALL.json`.

    The wrapper writes `CALL.json` after the call returns, so a tail whose
    wrapper refused at preflight has no clock at all. The driver reads no clock
    of its own, so the honest fallback is the last slot that carries one — named
    in the declaration beside the value, so a reader can see the timestamp is that
    slot's and not the tail's."""
    for record in reversed(records):
        call_path = os.path.join(STUDY, record.get("path") or "", "CALL.json")
        if not os.path.isfile(call_path):
            continue
        ended = _load_json(call_path).get("endedAt")
        if ended:
            return ended, record
    return None, None


def declare_shortfall(reason: str, pins_path: str) -> int:
    """A batch that cannot finish declares the shortfall BEFORE anything is
    scored. The scorer refuses an incomplete batch without this file, so the
    declaration cannot be written after the rates are seen — and it refuses a
    declaration over a batch that is not short, so this file cannot be used to
    unblock scoring of a full or over-full one. **A terminal batch is therefore
    exactly 150 slots or a SHORTFALL.json, never both and never neither.**

    What it declares (R1-7's schema, `SHORTFALL_SCHEMA`): the reason, the last
    completed round R, the exact completed prefix of the registered order — the
    global index of the last completed slot — the UTC wall clock of that slot,
    **the ledger's file digest and chain head**, and **the full slot/seal
    inventory**: one row per slot carrying its place in §2's order, its path, its
    `SLOT-MANIFEST.json` digest, its wrapper exit and its §1a code. The prefix is
    the ledger's, verified against the registered order first, because the scorer
    requires the declared prefix to equal the ledger's slot for slot, and per-arm
    counts follow from a prefix where they do not follow from a round number.

    **The inventory is the point, and the counts are the summary.** Round 1
    (R1-7) found the scorer accepting any JSON object — `{}` included — as the
    thing that makes an incomplete batch terminal: nothing bound the file to the
    ledger, the seals, or the registered order, so an arbitrary set of slots
    could be declared short and scored. A set chosen by what its slots CONTAINED
    is not a prefix of the registered order and does not carry the ledger's
    chain head, and both are checked — by this function before it writes, and by
    the scorer before it reads.

    The clock is READ, not taken: the driver holds no clock, and the timestamp is
    the one the wrapper stamped into that slot's CALL.json when it ran.

    Declaring one costs the study its whole confirmatory surface: under the
    stopping rule an incomplete batch, at any round and for any reason, yields
    `UNRESOLVED-BY-DESIGN` on every level verdict and no contrast at all. That
    price is registered in advance and is not this file's to reduce."""
    verify_ported_bytes()
    if os.path.exists(ATTEMPT_ROOT):
        raise BatchError("%s exists: a shortfall may not be declared after a rate "
                         "has been computed" % os.path.relpath(ATTEMPT_ROOT, STUDY))
    out_path = os.path.join(ARMS_ROOT, SHORTFALL_NAME)
    if os.path.exists(out_path):
        raise BatchError("%s already exists" % out_path)
    if not reason:
        raise BatchError("--reason is required: a shortfall without a reason is a gap")
    pins = load_registry(pins_path)
    entries = schedule_entries()
    records = load_ledger()
    verify_prefix(records, entries)
    # The slots actually on disk, counted by the SCORER's own rule, so the
    # driver's count is not a second definition of the population — and by the
    # same function the reconciliation below enumerates them with, so the
    # declaration and the reconciliation cannot be looking at two different
    # populations.
    present = len(slots_on_disk())
    if present >= REGISTERED_SLOTS:
        raise BatchError(
            "%d slots are present and %d were registered: a shortfall declares a "
            "SHORT batch, and this one is not short" % (present, REGISTERED_SLOTS))
    # The declaration is a statement about the ledger AND about the slots on
    # disk, so the two are reconciled before either is written down. A batch
    # killed in the seal-then-record window is exactly the batch that then needs a
    # shortfall, and it used to be the one batch that could not have one.
    recovered = reconcile_ledger(records, entries)
    if recovered is not None:
        records.append(recovered)
        verify_prefix(records, entries)
        write_ledger(records, pins, ledger_header("cliOverride"))
        print("completed the ledger record for global index %d from its seal: the "
              "slot ran and only the append was interrupted"
              % recovered["globalIndex"])
    if present != len(records):
        raise BatchError(
            "%d slots are on disk and the ledger records %d: a declaration is a "
            "statement about the ledger AND about the slots present, and the "
            "scorer requires the two to agree slot for slot. The disagreement is "
            "not the seal-then-record window — that leaves exactly one slot, and "
            "it is completed above — so it goes in DEVIATIONS.md rather than into "
            "a declaration the scoring will refuse" % (present, len(records)))
    last = records[-1] if records else None
    whole_rounds = completed_rounds(records)
    stopped_at, clock_record = last_slot_clock(records)
    ledger_file = os.path.join(ARMS_ROOT, LEDGER_NAME)
    declaration = {
        "declarationVersion": SHORTFALL_VERSION,
        "registeredRounds": ROUNDS,
        "registeredRunsPerArm": RUNS_PER_ARM,
        "registeredSlots": REGISTERED_SLOTS,
        "completedRounds": whole_rounds,
        "completedThroughGlobalIndex": last["globalIndex"] if last else 0,
        "completedSlots": present,
        # The ledger's identity, both ways (R1-7): the digest of the FILE, and
        # the chain head the records themselves compute to. A declaration that
        # names neither can be written over any ledger at all.
        "ledgerSha256": _digest(ledger_file) if os.path.isfile(ledger_file)
                        else None,
        "ledgerHeadSha256": record_digest(records[-1]) if records else None,
        # The inventory: one row per slot of the declared prefix, each carrying
        # its place in the registered order, its path, its SEAL and its outcome.
        # This is the member that makes outcome-selective deletion visible —
        # counts alone never could.
        "slots": [{member: record.get(member)
                   for member in SHORTFALL_SLOT_SCHEMA} for record in records],
        "lastSlot": last["path"] if last else None,
        "lastSlotEndedAt": stopped_at,
        # Which slot that clock is the clock OF. It is the last slot of the
        # prefix whenever that slot has a CALL.json, and an earlier one when the
        # tail's wrapper refused before writing one; a reader can tell the two
        # apart by comparing it with lastSlot instead of guessing.
        "lastSlotEndedAtFrom": clock_record["path"] if clock_record else None,
        "reason": reason,
        "note": "Declared before scoring. A terminal batch is exactly %d slots or "
                "carries this file, never both. The completed prefix is the "
                "ledger's, verified against §2's registered call order position "
                "by position; the scorer requires it to equal the ledger's prefix "
                "slot for slot and the slots actually present to be exactly that "
                "prefix. completedRounds counts WHOLE rounds — a prefix ending "
                "inside a round declares the round before it, and 0 when none is "
                "whole. lastSlotEndedAt is read from a slot's own CALL.json — the "
                "driver reads no clock — and falls back through the prefix to the "
                "last slot that HAS one, because a wrapper that refused at "
                "preflight wrote no CALL.json; lastSlotEndedAtFrom names the slot "
                "it was read from, and both are null when no slot of the prefix "
                "carries a timestamp at all. The headline reports 'R of %d rounds "
                "completed', and an incomplete batch returns no verdict of any "
                "kind: every level verdict is UNRESOLVED-BY-DESIGN and no "
                "contrast is computed. The slots member is the INVENTORY: one "
                "row per slot of the declared prefix, carrying its place in the "
                "registered order, its path, its SLOT-MANIFEST.json digest and "
                "its outcome, beside the ledger's own file digest and chain "
                "head. Counts summarize; the inventory is what a reader "
                "recomputes, and what makes a prefix distinguishable from a set "
                "of slots chosen by what they contained."
                % (REGISTERED_SLOTS, ROUNDS),
    }
    # R1-7: the driver validates its OWN declaration before writing it, through
    # the same two functions the scorer runs on read. A declaration this driver
    # cannot validate is a declaration this driver does not write — the
    # alternative is a file that unblocks scoring and describes nothing.
    validate_shortfall(declaration, entries)
    verify_shortfall(declaration, records, declaration["ledgerSha256"])
    _write_json(out_path, declaration)
    print("shortfall declared: %d of %d rounds, %d of %d slots completed"
          % (whole_rounds, ROUNDS, present, REGISTERED_SLOTS))
    return 0


# --- D9: the pre-pilot effort sweep (§2.1) -----------------------------------
#
# THE THING THE REGISTRATION REGISTERS AND THE HARNESS LACKED. §2.1 registers
# `n = 3/arm across three settings — 27 calls`, run through this apparatus,
# published in full, `citable: false`, outside every population, with a
# per-setting abort rule and a call cap. Every one of those words is a behaviour
# here rather than a promise somewhere else:
#
#   *sequential, arm-interleaved, A first* — `sweep_schedule()`. A first because
#     the abort rule reads the setting's FIRST ARM-A CALL, and a schedule that
#     opened on B would make the registered sentence unreadable.
#   *27 calls, capped* — `SWEEP_CALL_CAP`, derived from the settings and the
#     per-arm count and checked against the registry's `sweep.callCap`.
#   *the sweep's own root* — `SWEEP_ROOT`, outside `arms/` so R10-1's occupancy
#     gate cannot see it (the constant carries the argument).
#   *`PIN_LABEL=SWEEP`, claimed by the driver* — `invoke()`, unconditionally.
#   *the effort threaded per call* — `SWEEP_EFFORT`, likewise unconditionally,
#     legal under one label and refused outside the registered set at BOTH ends.
#   *published in full* — `SWEEP.json` and `SWEEP.md`, written after every call
#     rather than at the end, so a sweep killed mid-run has published what it
#     spent.
#   *`citable: false`* — stamped by the wrapper into every `CALL.json`, by this
#     driver into every ledger row, into the ledger's header and into the
#     rendered table's own first line.
#
# WHAT THIS MODE DOES NOT DO. It computes no rate, chooses no setting and fills
# no pin. §2.1 registers the compute condition as chosen from the sweep's result
# by a rule that is named when the choice is made; a driver that picked the
# winner would be making the registered decision on the maintainer's behalf out
# of the data it had just produced. It publishes the table and stops.


def sweep_label(when=None) -> str:
    """`<UTC date>-effort-sweep`, the sweep's dated directory name.

    A DATE and not a timestamp: §2.1's sweep is one procedure run once, and two
    sweeps on one day are a second sweep, which the cap clause governs — the
    label collides, the slots collide, and the driver refuses rather than
    interleaving two sweeps in one tree. `when` is the injection seam the tests
    use; production takes today's UTC date."""
    day = when or datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    return "%s%s" % (day, SWEEP_LABEL_SUFFIX)


def sweep_setting_dir(setting) -> str:
    """The directory a setting's slots live in. `None` — a sweep call at the
    CLI's own default — lands under the registered literal rather than under an
    empty component, because a path with an empty component is a path with one
    fewer component."""
    return setting if setting else SWEEP_DEFAULT_SETTING_DIR


def sweep_slot_path(label: str, setting, arm: str, run_index: int) -> str:
    """`sweeps/<label>/<setting>/arm-<ARM>/run-NNN`, absolute.

    The wrapper recomputes this from the registry, the threaded setting and the
    arm, and refuses a slot that is not it — so this function is the driver's
    half of an agreement and not the authority for it."""
    if arm not in ARMS:
        raise BatchError("%r is not one of this study's arms %s"
                         % (arm, ", ".join(ARMS)))
    return os.path.join(SWEEP_ROOT, label, sweep_setting_dir(setting),
                        "arm-%s" % arm, "run-%03d" % run_index)


def sweep_schedule(setting: str, per_arm: int = SWEEP_PER_ARM) -> list:
    """One setting's calls: ARM-INTERLEAVED, A FIRST, sequential.

    A B C A B C A B C at `per_arm = 3`. Two registered properties live in that
    order and neither is decorative:

    * **A is first.** The abort rule's first clause reads "a setting whose FIRST
      arm-A call exceeds 2700 s", and under an interleaved order opening on A
      the setting's first call and its first arm-A call are the same call. A
      block order (AAA BBB CCC) would satisfy that sentence too, and would spend
      three arm-A calls before ever seeing B — which is precisely the state the
      SECOND clause's per-arm projection cannot be computed from.
    * **Interleaved, not blocked.** The projection needs a mean for every arm,
      and interleaving reaches one call per arm after three calls instead of
      after seven. A setting that is out of budget is then detectable at a third
      of the price.

    This is NOT the primary batch's carryover-balanced Williams order and does
    not pretend to be: three runs per arm cannot balance first-order carryover,
    the sweep is `citable: false` and outside every population, and a sweep
    dressed as a balanced design would invite exactly the reading §2.1 forbids.
    """
    if per_arm < 1:
        raise BatchError("a sweep setting runs at least one call per arm")
    entries, index = [], 0
    for run_index in range(1, per_arm + 1):
        for arm in ARMS:                      # ("A", "B", "C") — A first
            index += 1
            entries.append({
                "setting": setting,
                "arm": arm,
                "runIndex": run_index,
                "indexWithinSetting": index,
            })
    return entries


# --- D9a: M-24's witness resolution, as the sweep's step zero ----------------

def _witness_occurrences(payload, prefix: str = "") -> list:
    """Every `EFFORT_WITNESS_MEMBERS` name reachable in one payload, at any
    depth, as `[(dotted path, value)]`.

    Recursive because the occurrence M-24 actually found in 019's transcripts is
    three levels down — `collaboration_mode.settings.reasoning_effort` — and a
    scan of the payload's top-level keys would have reported "no member names
    the effort" about a transcript that names it twice."""
    found = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            here = "%s.%s" % (prefix, key) if prefix else str(key)
            if key in EFFORT_WITNESS_MEMBERS:
                found.append((here, value))
            found.extend(_witness_occurrences(value, here))
    elif isinstance(payload, list):
        for position, value in enumerate(payload):
            found.extend(
                _witness_occurrences(value, "%s[%d]" % (prefix, position)))
    return found


def effort_witness(session_path: str) -> dict:
    """M-24's WITNESS RESOLUTION over one retained transcript.

    §2.1 registers a step that "sets the flag and inspects the resulting
    `session.jsonl` for a non-null member naming the effort", with two branches:

    * a non-null member exists — transcript gate 5 is extended to it with the
      same `turn-context-mismatch` reason tag and the same apparatus-side
      classification (`WITNESS_BRANCH_GATE5`);
    * none exists — the effort pin is a `CALL.json` SELF-REPORT where no
      transcript witness exists, with `reasoning_output_tokens` entering C4 as a
      band (`WITNESS_BRANCH_SELF_REPORT`).

    THE BRANCH IS DECIDED ON `turn_context` AND ONLY ON `turn_context`, because
    gate 5 is a `turn_context` gate: extending it to a member that lives in some
    other record type would be extending a different gate. A non-null occurrence
    elsewhere in the transcript is real evidence and is REPORTED — under
    `otherOccurrences`, with the note that says why it did not decide the branch
    — rather than being dropped or quietly promoted.

    NULL occurrences are counted separately and on purpose. 019's transcripts
    carry exactly one, `collaboration_mode.settings.reasoning_effort: null`, and
    reporting "no occurrences" about a transcript that has one would make the
    next reader re-do this work to find out whether the member was absent or
    present-and-empty. `transcript_check.py:603-608` would refuse every call
    against that null, which is the fact M-24 is a ruling about.

    THIS FUNCTION AMENDS NOTHING. It reports which branch fired; extending gate
    5 is a change to `harness/transcript_check.py` that lands with the branch,
    under the preregistration's own sentence, and not on this driver's
    authority."""
    if not os.path.isfile(session_path):
        raise BatchError(
            "M-24's witness resolution has no transcript to read at %s: the "
            "step is registered as run over the FIRST sweep call's own "
            "session.jsonl, and a first call that retained none resolves "
            "nothing" % session_path)
    turn_context, other, nulls = [], [], []
    with open(session_path, "rb") as handle:
        for number, line in enumerate(handle, start=1):
            text = line.decode("utf-8", "replace").strip()
            if not text:
                continue
            try:
                record = json.loads(text)
            except ValueError:
                # A transcript line that is not JSON is the transcript's
                # problem and `transcript_check` is where it is adjudicated;
                # this step reports what it could read rather than refusing a
                # resolution over a line it does not own.
                continue
            if not isinstance(record, dict):
                continue
            kind = record.get("type")
            payload = record.get("payload")
            for where, value in _witness_occurrences(payload):
                row = {"line": number, "recordType": kind, "member": where,
                       "value": value}
                if value is None:
                    nulls.append(row)
                elif kind == "turn_context":
                    turn_context.append(row)
                else:
                    other.append(row)
    branch = WITNESS_BRANCH_GATE5 if turn_context else WITNESS_BRANCH_SELF_REPORT
    return {
        "branch": branch,
        "sessionSha256": _digest(session_path),
        "turnContextOccurrences": turn_context,
        "otherOccurrences": other,
        "nullOccurrences": nulls,
        "searchedMembers": list(EFFORT_WITNESS_MEMBERS),
        "note": (
            "M-24, resolved as the sweep's step zero over the FIRST sweep "
            "call's retained transcript. The branch is decided on turn_context "
            "alone, because transcript gate 5 is a turn_context gate; a "
            "non-null occurrence in another record type is reported under "
            "otherOccurrences and does not decide it. A null occurrence is "
            "reported under nullOccurrences and is NOT a witness: 019's "
            "transcripts carry exactly one such member and "
            "transcript_check.py:603-608 would refuse every call against it."),
        "obligation": (
            "transcript gate 5 is EXTENDED to this member, with the same "
            "turn-context-mismatch reason tag and the same apparatus-side "
            "classification, before the primary batch. The sweep publishes the "
            "branch; it does not amend the gate."
            if branch == WITNESS_BRANCH_GATE5 else
            "the effort pin is registered as a CALL.json SELF-REPORT where no "
            "transcript witness exists, with reasoning_output_tokens entering "
            "C4 as a band. The condition is asserted by the wrapper and not "
            "independently witnessed, and that sentence travels with every "
            "published record of the condition."),
    }


def reasoning_output_tokens(session_path: str):
    """The transcript's LAST `reasoning_output_tokens`, or None.

    §2.1's publication obligation names this column, and the pinned CLI carries
    it in `event_msg`/`token_count` under `info.total_token_usage` — a running
    total, so the last one is the call's. It is read WHERE THE TRANSCRIPT
    CARRIES IT and is None where it does not: a sweep row with no token count is
    published as a row with no token count, not as a zero."""
    if not os.path.isfile(session_path):
        return None
    value = None
    with open(session_path, "rb") as handle:
        for line in handle:
            text = line.decode("utf-8", "replace").strip()
            if not text or "reasoning_output_tokens" not in text:
                continue
            try:
                record = json.loads(text)
            except ValueError:
                continue
            found = _token_total(record)
            if found is not None:
                value = found
    return value


def _token_total(record):
    """`info.total_token_usage.reasoning_output_tokens` from one record, or
    None. Read by PATH and not by a recursive name search: `last_token_usage`
    carries the same member name for a different quantity, and a search that
    took whichever came first would publish one or the other by dict order."""
    if not isinstance(record, dict):
        return None
    payload = record.get("payload")
    if not isinstance(payload, dict):
        return None
    info = payload.get("info")
    if not isinstance(info, dict):
        return None
    usage = info.get("total_token_usage")
    if not isinstance(usage, dict):
        return None
    value = usage.get("reasoning_output_tokens")
    return value if isinstance(value, int) and not isinstance(value, bool) else None


# --- D9b: the abort rule, as two functions that decide nothing else ----------

def sweep_budget_n(pins: dict) -> tuple:
    """`(N, which branch it came from)` for the abort rule's projection.

    `batch.n` is NULL by construction until this sweep produces it, so the
    projection is made at the ONE branch §2.1's dual-pricing table prices —
    `N = 60/arm` — and the ledger records that it was the priced branch and not
    a registered N. A registry that has since filled `batch.n` is projected at
    THAT value, and the ledger records that instead. The driver never picks the
    cheaper of the two."""
    registered = (pins.get("batch") or {}).get("n")
    if isinstance(registered, int) and not isinstance(registered, bool) \
            and registered > 0:
        return registered, "batch.n"
    return SWEEP_BUDGET_PROJECTION_N, "the §2.1 priced branch (N = 60/arm)"


def projected_batch_hours(per_arm_means: dict, n: int) -> float:
    """The primary batch's wall clock at these per-arm means, in hours.

    `n × Σ_arm mean_arm ÷ 3600` — the SLOT-TRIPLE arithmetic §2.1's own table
    uses: the pilot-like triple 1660.184 + 803.042 + 624.114 s = 3087.34 s at
    N = 60 gives 51.46 h, which is the figure that table prints. Computing the
    projection the same way the registration priced it is what makes "beyond
    72 h" mean the same number to the driver and to the reader.

    Refuses on a partial mean set rather than projecting from two arms: a
    projection over an incomplete triple understates the batch, and understating
    it is the direction that spends money."""
    missing = [arm for arm in ARMS if arm not in per_arm_means]
    if missing:
        raise BatchError(
            "no budget projection is made from %d of %d arms (missing %s): a "
            "triple short an arm understates the batch, and understating it is "
            "the direction that spends"
            % (len(per_arm_means), len(ARMS), ", ".join(missing)))
    return n * sum(per_arm_means[arm] for arm in ARMS) / 3600.0


def sweep_abort_verdict(calls: list, n: int, n_source: str) -> dict:
    """§2.1's PER-SETTING ABORT RULE over one setting's calls so far, exactly as
    registered and not one clause wider.

    > A setting whose **first** arm-A call exceeds **2700 s** (the registered
    > per-call ceiling) is aborted after that call; a setting whose per-arm mean
    > duration projects a primary batch beyond **72 h** at the registered N
    > branch is recorded as **out of budget** and is not swept further. Aborted
    > settings are published with the call that aborted them.

    Two clauses, two verdicts, and they are different words on purpose:
    `aborted` is a setting whose first call ran past the apparatus ceiling, and
    `out-of-budget` is a setting the arithmetic priced out. Returning one word
    for both would make the published table unable to say which happened.

    CLAUSE ONE reads the setting's first arm-A call — which, under
    `sweep_schedule()`'s A-first interleave, is the setting's first call. The
    duration compared is the DRIVER-MEASURED wall clock, which includes the
    wrapper's own setup and its kill grace; a call the wrapper terminated at the
    ceiling therefore satisfies "exceeds 2700 s" without the rule needing a
    second sentence about timeouts, and the ledger records `timedOut` beside the
    duration so a reader can see which it was.

    CLAUSE TWO is evaluated as soon as EVERY arm has a completed call — after
    three calls under the interleaved order — because "is not swept further" is
    only a rule if it can still stop something. A refused call contributes no
    duration to any mean: a call that never reached the model is not evidence
    about what the model costs.

    Returns `{"verdict", "reason", "abortingCall", …}` with verdict `None` when
    the setting continues. It DECIDES NOTHING ELSE — it does not choose a
    setting, does not stop other settings, and does not touch the cap."""
    completed = [call for call in calls if call.get("code") is None]
    first_arm_a = next((call for call in calls if call["arm"] == "A"), None)
    if first_arm_a is not None and first_arm_a["indexWithinSetting"] == 1 \
            and first_arm_a["durationSeconds"] > CALL_TIMEOUT_SECONDS:
        return {
            "verdict": "aborted",
            "clause": "first-arm-A-call-over-ceiling",
            "reason": (
                "the setting's first arm-A call ran %.1f s, past the registered "
                "%d s per-call ceiling; §2.1 aborts the setting AFTER that call, "
                "and the call is published with it"
                % (first_arm_a["durationSeconds"], CALL_TIMEOUT_SECONDS)),
            "abortingCall": first_arm_a,
            "projectedBatchHours": None,
        }
    means = {}
    for arm in ARMS:
        durations = [call["durationSeconds"] for call in completed
                     if call["arm"] == arm]
        if durations:
            means[arm] = sum(durations) / len(durations)
    if len(means) == len(ARMS):
        hours = projected_batch_hours(means, n)
        if hours > SWEEP_BUDGET_HOURS:
            return {
                "verdict": "out-of-budget",
                "clause": "projected-batch-over-budget",
                "reason": (
                    "the per-arm means (%s) project a primary batch of %.2f h at "
                    "%s, past the registered %d h; §2.1 records the setting out "
                    "of budget and sweeps it no further"
                    % (", ".join("%s %.1f s" % (arm, means[arm]) for arm in ARMS),
                       hours, n_source, SWEEP_BUDGET_HOURS)),
                "abortingCall": calls[-1],
                "projectedBatchHours": hours,
                "perArmMeanSeconds": means,
            }
        return {"verdict": None, "clause": None, "reason": None,
                "abortingCall": None, "projectedBatchHours": hours,
                "perArmMeanSeconds": means}
    return {"verdict": None, "clause": None, "reason": None,
            "abortingCall": None, "projectedBatchHours": None,
            "perArmMeanSeconds": means}


# --- D9c: the sweep's own preflight ------------------------------------------

def sweep_preflight(label: str, slots: list, scratch_parent: str,
                    pins_path: str, cli_override: str) -> dict:
    """Everything checkable before the sweep's first call, and NOT the primary
    batch's preflight.

    The two differ because the sweep runs at a different point in the ceremony,
    and pretending otherwise would make it un-runnable:

    * `require_freeze()` refuses while any freeze pin is null. The sweep runs
      BEFORE the freeze — every freeze pin is null by construction — so this
      gate reads the DESIGN-TIME pins under the registered sweep label instead
      (`integrity.design_time_pin_state()` minus `SWEEP_EXEMPT_PINS`), which
      leaves exactly one requirement: `codex.model` is filled. That is M-25's
      own sentence — one exemption, one value and one label wide, and
      `codex.model` never exempt — enforced rather than restated.
    * `check_registry()` refuses while `batch.n` is null. `batch.n` is this
      sweep's OUTPUT; requiring it would be requiring the answer before the
      question.
    * `require_golden()` and `require_isolation_negative()` are preconditions of
      the BATCH. §3.2's golden capture is a fact about the environment at
      capture time and the sweep precedes it; gating the sweep on it would
      reorder the registered ceremony.

    What it does NOT relax: the ported bytes, the canonical registry (R10-1),
    the CLI digest, the arm prompt digests, the attempt root, the lawful
    destination and the never-rewrite-a-slot rule are all checked here, and the
    wrapper re-checks the binary digest, the CLI version, the interpreter and
    the per-arm prompt digest per call."""
    verify_ported_bytes()
    if not slots:
        raise BatchError("a sweep needs at least one call")
    if len(slots) > SWEEP_CALL_CAP:
        raise BatchError(
            "this sweep plans %d calls and §2.1 caps the sweep at %d: the cap is "
            "not raised without a DEVIATIONS.md entry naming the reason and "
            "republishing the price" % (len(slots), SWEEP_CALL_CAP))
    if not os.path.isfile(SCRIPT):
        raise BatchError("no authoring wrapper at %s" % SCRIPT)
    if not os.path.isdir(scratch_parent):
        raise BatchError("scratch parent %s is not a directory" % scratch_parent)
    require_canonical_registry(pins_path)
    pins = _load_json(pins_path)
    # The registered constants and the registry's own members are the same
    # numbers, or the sweep does not run. §2.1's set, cap, per-arm count, root
    # and budget are carried in both places so a reader of either can see them;
    # carrying them in both places is only safe if a drift refuses.
    sweep = pins.get("sweep") or {}
    for member, expected, what in (
            ("settings", list(SWEEP_SETTINGS), "the swept set (§2.1, 2026-08-24)"),
            ("perArm", SWEEP_PER_ARM, "the per-arm call count"),
            ("callCap", SWEEP_CALL_CAP, "the registered call cap"),
            ("root", os.path.basename(SWEEP_ROOT), "the sweep's slot root"),
            ("budgetHours", SWEEP_BUDGET_HOURS, "the abort rule's budget"),
            ("budgetProjectionN", SWEEP_BUDGET_PROJECTION_N,
             "the abort rule's priced N branch")):
        if sweep.get(member) != expected:
            raise BatchError(
                "harness/PINS.json's sweep.%s is %r and this driver's constant "
                "for %s is %r: the two are one registration in two places, and a "
                "sweep is not run under a disagreement about what it is"
                % (member, sweep.get(member), what, expected))
    if sweep.get("citable") is not False:
        raise BatchError(
            "harness/PINS.json's sweep.citable is %r: §2.1 registers the sweep's "
            "outputs as citable: false and outside every population, and a "
            "registry that does not say so is not the registry this mode runs "
            "under" % sweep.get("citable"))
    # M-25's gate, at the width M-25 registers it. `integrity` owns the tuples
    # and the exemption; this reads them rather than restating them.
    state = integrity.design_time_pin_state(pins)
    unfilled = [name for name, filled in state.items()
                if not filled and name not in integrity.SWEEP_EXEMPT_PINS]
    if unfilled:
        raise BatchError(
            "harness/PINS.json leaves these design-time pins null: %s. §2.1's "
            "exemption is one value and one label wide — codex.reasoningEffort "
            "alone, because the sweep is what resolves it — and codex.model is "
            "never exempt: a sweep is still a call to a named model, and 019's "
            "pilot's defining defect was a call whose model nothing recorded"
            % ", ".join(sorted(unfilled)))
    for arm in ARMS:
        path, pinned = arm_prompt(pins, arm)
        if not os.path.isfile(path):
            raise BatchError("arm %s's prompt is missing from %s"
                             % (arm, os.path.relpath(path, STUDY)))
        actual = _digest(path)
        if not _matches(actual, pinned):
            raise BatchError(
                "arm %s's prompt is %s, not the pinned %s: no sweep call is made "
                "with bytes that are not the arm's" % (arm, actual, pinned))
    if cli_override is not None:
        if not os.path.isfile(cli_override):
            raise BatchError("no CLI at %s" % cli_override)
        override_digest = _digest(cli_override)
        if not _matches(override_digest, pins["codex"]["binarySha256"]):
            raise BatchError("the CLI at %s is %s, not the pinned %s"
                             % (cli_override, override_digest,
                                pins["codex"]["binarySha256"]))
    if os.path.exists(ATTEMPT_ROOT):
        raise BatchError(
            "%s exists: a sweep is a call, and no call is made after a rate has "
            "been computed" % os.path.relpath(ATTEMPT_ROOT, STUDY))
    # The sweep root must be a place this harness may write. It is, and it is
    # asserted rather than assumed: ADR 0004's exact set reaches no byte under
    # `sweeps/`, exactly as it reaches none under `arms/` or `calibration/`.
    require_lawful_destination(os.path.join(SWEEP_ROOT, label),
                               "the sweep root")
    here = os.path.join(SWEEP_ROOT, label)
    if os.path.lexists(here):
        raise BatchError(
            "%s already exists: §2.1's sweep is one procedure run once, and a "
            "second sweep under the same dated label would interleave two sweeps "
            "in one tree. Move the first out of the way and record the second in "
            "DEVIATIONS.md" % os.path.relpath(here, STUDY))
    existing = [os.path.relpath(slot, STUDY) for slot in slots
                if os.path.lexists(slot)]
    if existing:
        raise BatchError("these sweep slots already exist and are never "
                         "rewritten: %s" % ", ".join(existing))
    return pins


# --- D9d: the ledger and the rendered table ----------------------------------

def sweep_ledger_body(label: str, pins_path: str, pins: dict, n: int,
                      n_source: str, settings: list, witness) -> dict:
    """`SWEEP.json`'s whole content. Written after every call, so a sweep killed
    part way through has published what it spent — the prereg's
    published-in-full obligation is about the calls that were MADE, and a ledger
    written only at the end publishes nothing about a sweep that did not
    finish."""
    return {
        "sweepVersion": "1",
        "citable": False,
        "label": label,
        "study": os.path.basename(STUDY),
        "registration": "PREREGISTRATION.md §2.1 — the pre-pilot effort sweep. "
                        "Outputs are citable: false and outside every "
                        "population. The compute condition is chosen from this "
                        "table by a rule named when the choice is made; this "
                        "file chooses nothing.",
        "registeredSettings": list(SWEEP_SETTINGS),
        "perArm": SWEEP_PER_ARM,
        "callCap": SWEEP_CALL_CAP,
        "callTimeoutSeconds": CALL_TIMEOUT_SECONDS,
        "budgetHours": SWEEP_BUDGET_HOURS,
        "budgetProjectionN": n,
        "budgetProjectionNSource": n_source,
        "pinsSha256": _digest(pins_path),
        "model": (pins.get("codex") or {}).get("model"),
        "cli": (pins.get("codex") or {}).get("version"),
        "reasoningEffortFlag": (pins.get("codex") or {}).get(
            "reasoningEffortFlag"),
        "reasoningEffortConfigKey": (pins.get("codex") or {}).get(
            "reasoningEffortConfigKey"),
        "witnessResolution": witness,
        "settings": settings,
    }


def render_sweep_table(body: dict) -> str:
    """`SWEEP.md` — §2.1's "full per-setting table", rendered from the ledger
    this driver just wrote and from nothing else.

    One row per (setting, arm, run), because the registration names per-arm
    DURATIONS, completion BYTES and `reasoning_output_tokens` and a table that
    published only the means would have discarded the dispersion the compute
    decision is about. The per-setting summary sits under its own rows rather
    than in a second table, so a reader cannot read a mean without seeing what
    it is a mean of."""
    lines = [
        "# Pre-pilot effort sweep — %s" % body["label"],
        "",
        "**`citable: false`. Outside every population.** PREREGISTRATION.md "
        "§2.1 registers this sweep as `n = 3/arm across three settings — 27 "
        "calls`, published in full. Nothing here is evidence for or against R1, "
        "and no setting is chosen by this file.",
        "",
        "| what | value |",
        "|---|---|",
        "| registered settings | %s |" % ", ".join(body["registeredSettings"]),
        "| per arm | %d |" % body["perArm"],
        "| call cap | %d |" % body["callCap"],
        "| per-call ceiling | %d s |" % body["callTimeoutSeconds"],
        "| budget | %d h at N = %d/arm (%s) |"
        % (body["budgetHours"], body["budgetProjectionN"],
           body["budgetProjectionNSource"]),
        "| model | `%s` |" % body["model"],
        "| CLI | `%s` |" % body["cli"],
        "| effort argument | `%s %s=<tier>` |"
        % (body["reasoningEffortFlag"], body["reasoningEffortConfigKey"]),
        "| registry | `%s` |" % body["pinsSha256"],
        "",
    ]
    witness = body.get("witnessResolution")
    lines.extend([
        "## M-24's witness resolution — the sweep's step zero",
        "",
    ])
    if not witness:
        lines.extend([
            "Not resolved: no sweep call retained a transcript to read it from.",
            "",
        ])
    else:
        lines.extend([
            "**Branch: `%s`.**" % witness["branch"],
            "",
            witness["obligation"],
            "",
            "| occurrences | count |",
            "|---|---|",
            "| non-null, in `turn_context` (the gate-5 surface) | %d |"
            % len(witness["turnContextOccurrences"]),
            "| non-null, in another record type | %d |"
            % len(witness["otherOccurrences"]),
            "| present and NULL | %d |" % len(witness["nullOccurrences"]),
            "",
        ])
        for row in witness["nullOccurrences"][:5]:
            lines.append("- null at `%s` (`%s`, line %d)"
                         % (row["member"], row["recordType"], row["line"]))
        for row in witness["otherOccurrences"][:5]:
            lines.append("- non-null at `%s` = `%r` (`%s`, line %d) — NOT a "
                         "gate-5 witness: gate 5 reads `turn_context`"
                         % (row["member"], row["value"], row["recordType"],
                            row["line"]))
        lines.append("")
    for setting in body["settings"]:
        lines.extend([
            "## Setting `%s` — %s" % (setting["setting"], setting["outcome"]),
            "",
        ])
        if setting.get("reason"):
            lines.extend([setting["reason"], ""])
        lines.extend([
            "| arm | run | duration s | completion bytes | reasoning tokens | "
            "exit | code | timed out |",
            "|---|---|---|---|---|---|---|---|",
        ])
        for call in setting["calls"]:
            lines.append(
                "| %s | %d | %.1f | %s | %s | %d | %s | %s |"
                % (call["arm"], call["runIndex"], call["durationSeconds"],
                   "—" if call["completionBytes"] is None
                   else call["completionBytes"],
                   "—" if call["reasoningOutputTokens"] is None
                   else call["reasoningOutputTokens"],
                   call["wrapperExit"], call["code"] or "complete",
                   "yes" if call["timedOut"] else "no"))
        lines.append("")
        means = setting.get("perArmMeanSeconds") or {}
        if means:
            lines.extend([
                "| arm | mean duration s | completed calls |",
                "|---|---|---|",
            ])
            for arm in ARMS:
                if arm in means:
                    completed = len([call for call in setting["calls"]
                                     if call["arm"] == arm
                                     and call["code"] is None])
                    lines.append("| %s | %.1f | %d |"
                                 % (arm, means[arm], completed))
            lines.append("")
        if setting.get("projectedBatchHours") is not None:
            lines.extend([
                "Projected primary batch at N = %d/arm: **%.2f h** "
                "(budget %d h)."
                % (body["budgetProjectionN"], setting["projectedBatchHours"],
                   body["budgetHours"]),
                "",
            ])
    return "\n".join(lines) + "\n"


# --- D9e: the sweep itself ----------------------------------------------------

def _completion_bytes(slot: str):
    path = os.path.join(slot, "completion.txt")
    return os.path.getsize(path) if os.path.isfile(path) else None


def run_sweep(scratch_parent: str, pins_path: str, cli_override: str,
              label: str = None, settings: list = None,
              dry_run: bool = False) -> int:
    """§2.1's pre-pilot effort sweep, end to end.

    Sequential — never parallel, like the batch, and for the batch's reason: the
    sweep is measuring durations, and two calls sharing a machine measure the
    machine's contention. Arm-interleaved with A first. `PIN_LABEL=SWEEP` and
    the per-call setting claimed by this driver at `invoke()` and by nothing
    else. Published after every call.

    A refused call does not stop the sweep: the sweep exists to price settings,
    and a wrapper refusal is priced information about the apparatus, recorded
    with its code. What stops a setting is the abort rule and nothing else; what
    stops the sweep is the cap."""
    label = label or sweep_label()
    settings = list(settings or SWEEP_SETTINGS)
    unregistered = [name for name in settings if name not in SWEEP_SETTINGS]
    if unregistered:
        raise BatchError(
            "these settings are not in §2.1's registered set %s: %s. The swept "
            "SET was registered on 2026-08-24, before the sweep; a tier outside "
            "it needs a DEVIATIONS.md entry naming the reason and republishing "
            "the price" % (", ".join(SWEEP_SETTINGS), ", ".join(unregistered)))
    planned = []
    for setting in settings:
        for entry in sweep_schedule(setting):
            planned.append((entry, sweep_slot_path(label, setting, entry["arm"],
                                                   entry["runIndex"])))
    pins = sweep_preflight(label, [slot for _entry, slot in planned],
                           scratch_parent, pins_path, cli_override)
    n, n_source = sweep_budget_n(pins)
    if dry_run:
        print("sweep %s: %d calls over %d settings (%s), %d/arm, cap %d"
              % (label, len(planned), len(settings), ", ".join(settings),
                 SWEEP_PER_ARM, SWEEP_CALL_CAP))
        for entry, slot in planned:
            print("  %-8s %s run-%03d  %s"
                  % (entry["setting"], entry["arm"], entry["runIndex"],
                     os.path.relpath(slot, STUDY)))
        return 0
    root = os.path.join(SWEEP_ROOT, label)
    published = []
    witness = None
    spent = 0
    for setting in settings:
        calls, verdict = [], {"verdict": None, "reason": None,
                              "projectedBatchHours": None,
                              "perArmMeanSeconds": {}}
        for entry in sweep_schedule(setting):
            if spent >= SWEEP_CALL_CAP:
                raise BatchError(
                    "the sweep has spent its registered cap of %d calls and the "
                    "next call would be number %d: §2.1's cap is not raised "
                    "without a DEVIATIONS.md entry naming the reason and "
                    "republishing the price" % (SWEEP_CALL_CAP, spent + 1))
            slot = sweep_slot_path(label, setting, entry["arm"],
                                   entry["runIndex"])
            path, _pinned = arm_prompt(pins, entry["arm"])
            started = time.monotonic()
            status, code, stderr = invoke(
                slot, scratch_parent, pins_path, cli_override, "registered",
                entry["arm"], path, pin_label=SWEEP_LABEL, sweep_effort=setting)
            duration = time.monotonic() - started
            spent += 1
            session = os.path.join(slot, "session.jsonl")
            call = dict(entry)
            call.update({
                "slot": os.path.relpath(slot, STUDY),
                "globalIndex": spent,
                "durationSeconds": round(duration, 3),
                "wrapperExit": status,
                "code": code,
                "timedOut": code == WRAPPER_CODES.get(12),
                "completionBytes": _completion_bytes(slot),
                "reasoningOutputTokens": reasoning_output_tokens(session),
                "sessionRetained": os.path.isfile(session),
                "citable": False,
                "stderrTail": (stderr or "")[-STDERR_TAIL:] if code else None,
            })
            calls.append(call)
            # STEP ZERO, on the first sweep call that retained a transcript.
            # M-24 registers the resolution over "the resulting session.jsonl",
            # and the first call that produced one is the first call the step
            # can read; a refused first call resolves nothing and the step waits
            # for the next transcript rather than reporting an absence as a
            # branch.
            if witness is None and os.path.isfile(session):
                witness = effort_witness(session)
                witness["resolvedFrom"] = call["slot"]
            verdict = sweep_abort_verdict(calls, n, n_source)
            published = _publish_sweep(
                root, label, pins_path, pins, n, n_source, published, setting,
                calls, verdict, witness)
            if verdict["verdict"] is not None:
                print("setting %s: %s — %s"
                      % (setting, verdict["verdict"], verdict["reason"]))
                break
    print("sweep %s: %d calls under %s, published under %s (citable: false)"
          % (label, spent, SWEEP_LABEL, os.path.relpath(root, STUDY)))
    return 0


def _publish_sweep(root: str, label: str, pins_path: str, pins: dict, n: int,
                   n_source: str, published: list, setting: str, calls: list,
                   verdict: dict, witness) -> list:
    """Rewrite `SWEEP.json` and `SWEEP.md` with this setting's state folded in.

    Called after EVERY call. The published set is rebuilt rather than appended
    to, so the file on disk is always the whole sweep so far and never a
    fragment plus an assumption about what came before it."""
    current = {
        "setting": setting,
        "outcome": verdict["verdict"] or "swept",
        "reason": verdict.get("reason"),
        "clause": verdict.get("clause"),
        "abortingCall": verdict.get("abortingCall"),
        "projectedBatchHours": verdict.get("projectedBatchHours"),
        "perArmMeanSeconds": verdict.get("perArmMeanSeconds") or {},
        "callsMade": len(calls),
        "callsRegistered": POSITIONS * SWEEP_PER_ARM,
        "citable": False,
        "calls": calls,
    }
    rest = [row for row in published if row["setting"] != setting]
    published = rest + [current]
    body = sweep_ledger_body(label, pins_path, pins, n, n_source, published,
                             witness)
    os.makedirs(root, exist_ok=True)
    _write_json(os.path.join(root, SWEEP_LEDGER_NAME), body)
    with open(os.path.join(root, SWEEP_TABLE_NAME), "w") as handle:
        handle.write(render_sweep_table(body))
    return published



# --- §7 delta 6: the registered label rule's design-time half ---------------
#
# §2.1, M-25, ruled as drafted. `authoring_call.sh` refuses while `codex.model`
# is null, and `registeredLabelRule` names design-time-resolved pins as checked
# *whether or not the freeze has happened* — so a sweep that must run BEFORE the
# effort value exists is either refused or unenforced. Registered: a distinct
# `--sweep` label that exempts `codex.reasoningEffort` ALONE from the null check.
#
# The exemption is one member, at one label, and nothing else moves: `model`,
# the two binary digests and the interpreter are checked under every label, and
# the freeze pins are `integrity.study_label()`'s business and are untouched
# here. §2.1 also registers what the exemption costs — the sweep's outputs are
# `citable: false` and outside every population — and `calibration_record()`
# stamps that beside the exemption rather than leaving it to a runbook.

# The pins §2 marks `resolvedAtDesignTime`, as (registry path, why) pairs.
# `codex.reasoningEffort` joins them under §2.1's M-25 ruling: it and
# `codex.model` are "registered as design-time-resolved pins, NOT freeze pins",
# so neither is in `integrity.FREEZE_PINS` and neither makes a run a PILOT on
# its own — what they do is refuse the CALL, under both labels.
DESIGN_TIME_PINS = (
    (("codex", "model"),
     "§2: the model is named by explicit flag at batch time and the wrapper "
     "refuses rather than passing the string None to -m"),
    (("codex", "reasoningEffort"),
     "§2.1/M-24: PINS.json gains codex.reasoningEffort beside model / version "
     "/ binarySha256; the wrapper passes it explicitly and CALL.json stamps "
     "it. There is no transcript witness to bind it to today, so the pin is a "
     "CALL.json self-report where no transcript witness exists — a recorded "
     "intention, and this driver says so in every record it writes"),
    (("codex", "binarySha256"), "§2: the authoring binary's digest"),
    (("jpack", "binarySha256"), "§2: the pinned jpack binary's digest"),
    (("opa", "assetSha256"), "§2: the pinned OPA asset's digest"),
)

# The ONE member the `--sweep` label exempts, and nothing else. Named as a tuple
# so the exemption is enumerable: a second member added here is a diff a
# reviewer can see, which is what "written into the gate and its test before the
# first sweep call" asks for.
SWEEP_EXEMPT_PINS = (("codex", "reasoningEffort"),)


def _pin_at(pins: dict, path):
    node = pins
    for key in path:
        node = node.get(key) if isinstance(node, dict) else None
        if node is None:
            return None
    return node


def design_time_unfilled(pins: dict, mode: str = None) -> list:
    """The design-time-resolved pins still null, in registered order — with
    §2.1's `--sweep` exemption applied to `codex.reasoningEffort` ALONE.

    `mode` is None for the primary batch and the pilot (no exemption) and
    `"sweep"` for the pre-pilot effort sweep. The exemption exists because the
    sweep is what RESOLVES the effort value: a gate that required it would
    require the value the command exists to create, which is the same circularity
    `integrity.CEREMONY_LIFECYCLE_PINS` answers for the golden capture and the
    isolation assent — and the answer is the same shape, at one place, named.

    `integrity.pin_is_filled()` decides FILLED, so a registry of empty strings
    and `TODO(prereg)` sentinels is not a registration here either."""
    if mode is not None and mode not in CALIBRATION_MODES:
        raise BatchError("%r is not a registered calibration mode; §2.1 and "
                         "§2a.2 register %s"
                         % (mode, " and ".join(CALIBRATION_MODES)))
    exempt = SWEEP_EXEMPT_PINS if mode == "sweep" else ()
    unfilled = []
    for path, _why in DESIGN_TIME_PINS:
        if path in exempt:
            continue
        if not integrity.pin_is_filled(_pin_at(pins, path)):
            unfilled.append(".".join(path))
    return unfilled


def require_design_time_pins(pins: dict, mode: str = None) -> None:
    """The design-time half of the label rule, before any call — under EVERY
    label, which is what "checked whether or not the freeze has happened"
    means.

    §2.1: "Running the sweep outside the harness is rejected on sight: that is
    the 019 failure exactly." So the sweep goes through this gate too; the only
    thing its label changes is the one exempt member."""
    unfilled = design_time_unfilled(pins, mode)
    if unfilled:
        raise BatchError(
            "these design-time-resolved pins are still null: %s. §2 marks them "
            "resolvedAtDesignTime and registeredLabelRule checks them whether "
            "or not the freeze has happened, so no call is spent under a "
            "registry that does not name them%s"
            % (", ".join(unfilled),
               "" if mode != "sweep" else
               " (the --sweep label exempts %s alone, and nothing else)"
               % ", ".join(".".join(path) for path in SWEEP_EXEMPT_PINS)))


def calibration_record(mode: str, label: str, pins: dict,
                       setting=None) -> dict:
    """The header every calibration output carries — §2a.2's four registered
    differences from the primary batch, as data.

    They are enumerated here "so a fifth cannot be discovered later": output
    under `calibration/<label>/`, the pilot slot count, `citable: false`, and
    the pin state. A run of the sweep additionally stamps its SETTING, because
    §2.1 registers "each sweep call's setting stamped into its `CALL.json`" —
    a swept condition that is not in the bytes is a condition nobody can bind a
    duration to afterwards."""
    if mode not in CALIBRATION_MODES:
        raise BatchError("%r is not a registered calibration mode; §2.1 and "
                         "§2a.2 register %s"
                         % (mode, " and ".join(CALIBRATION_MODES)))
    if mode == "sweep" and setting is None:
        raise BatchError(
            "a sweep call carries no setting: §2.1 registers that each sweep "
            "call's setting is stamped into its CALL.json, and a swept "
            "condition absent from the bytes is a condition no observed "
            "duration can be priced against")
    return {
        "mode": mode,
        "label": label,
        "root": os.path.relpath(calibration_root(label), STUDY),
        "runsPerArm": (SWEEP_RUNS_PER_ARM if mode == "sweep"
                       else PILOT_RUNS_PER_ARM),
        "citable": CALIBRATION_CITABLE,
        "outsideEveryPopulation": True,
        "setting": setting,
        "designTimePinState": {
            ".".join(path): _pin_at(pins, path) for path, _why
            in DESIGN_TIME_PINS},
        "sweepExemption": ([".".join(path) for path in SWEEP_EXEMPT_PINS]
                           if mode == "sweep" else []),
        "registeredDifferences": [
            "output under calibration/<label>/",
            "the pilot slot count",
            "citable: false",
            "the pin state (§2.1's design-time-resolved rule)",
        ],
        "note": "§1a: the calibration pilot, the pre-pilot effort sweep and the "
                "smoke are non-citable and outside every population. §2.1: the "
                "effort condition is asserted by the wrapper and not "
                "independently witnessed, and that sentence travels with every "
                "published record of the condition.",
    }


def calibration_root(label: str) -> str:
    """`calibration/<label>/`, refused if the label would leave the subtree.

    A label is a directory NAME and never a path: `..`, an absolute path and a
    separator all reach outside the one subtree §2a.2 registers, and the freeze
    gate's whole rule is about what is inside it."""
    if not label or label != os.path.basename(label) or label in (".", "..") \
            or os.path.isabs(label) or os.sep in label:
        raise BatchError(
            "%r is not a calibration label: §2a.2 registers the output as "
            "calibration/<label>/, so the label names one directory inside "
            "that subtree and cannot reach out of it" % (label,))
    return os.path.join(CALIBRATION_ROOT, label)


# --- §7 delta 8: the freeze gate's calibration rule -------------------------

def calibration_freeze_problems(study=None) -> list:
    """§7 DELTA 8: "The freeze gate's `calibration/` rule — permit and require
    the subtree, still refuse any `results/primary-attempt-*`; written into the
    gate and its test before the first pilot call."

    Three rules, and each is a different sentence of the registration:

    * **PERMIT.** `calibration/` exists at the freeze and must not refuse it.
      019 had no such subtree, and `make_manifest.py`'s
      `prior_authoring_problems()` refuses any pre-freeze authoring state — so
      the permission is structural rather than an exception: §2a.2 puts
      calibration output under `calibration/<label>/`, which is outside the
      `arms/<ARM>/authoring` tree that gate derives from `batch.py`'s own
      constants. This function asserts that separation rather than assuming it,
      because the day a calibration slot lands under `arms/` the freeze would
      refuse for a reason nobody would connect to this delta.
    * **REQUIRE.** §2a registers C1–C5 as calibration UNDER REGISTERED
      CONDITIONS and §2a.6 puts the pilot's label, N and output digest into
      `PINS.json` before the primary attempt; §2a.4 requires
      `calibration/derive_floor.py` "committed and sealed before the pilot
      runs". A freeze with no calibration subtree is a freeze that skipped
      C1–C5, so the absence refuses.
    * **STILL REFUSE ANY `results/primary-attempt-*`.** Unchanged from 019's
      R9-2 rule and restated here at the registered spelling: the registered
      root, an attempt root under ANY other name, and a dangling symlink at
      either are all a prior attempt. `lexists`, not `exists`, for R9-2's
      reason.

    Returns problems; the caller composes them with the rest of the freeze
    gate. It is a pure filesystem read and makes no call."""
    root = study if study is not None else STUDY
    problems = []
    calibration = os.path.join(root, "calibration")
    if not os.path.isdir(calibration):
        problems.append(
            "calibration/ is absent and §2a registers C1–C5 as calibration "
            "under registered conditions, with §2a.6 putting the pilot's "
            "label, N and output digest into PINS.json BEFORE the primary "
            "attempt: a freeze with no calibration subtree is a freeze that "
            "skipped the pilot")
    elif not sorted(os.listdir(calibration)):
        problems.append(
            "calibration/ exists and is empty: §2a.2 registers the pilot's "
            "output under calibration/<label>/ and §2a.4 registers "
            "calibration/derive_floor.py as committed and sealed before the "
            "pilot runs, so an empty subtree is the same fact as an absent one")
    # PERMIT, asserted rather than assumed: calibration output must not sit in
    # the authoring tree the freeze gate refuses.
    for arm in ARMS:
        stray = os.path.join(root, "arms", arm, "authoring")
        if os.path.lexists(stray):
            problems.append(
                "arms/%s/authoring exists: §2a.2 registers calibration output "
                "under calibration/<label>/ and the freeze refuses any "
                "pre-freeze authoring tree, so a calibration slot written here "
                "would be refused for a reason that names the wrong cause"
                % arm)
    # STILL REFUSE ANY results/primary-attempt-*.
    results = os.path.join(root, "results")
    if os.path.lexists(os.path.join(root, "results", "primary-attempt-001")):
        problems.append(
            "results/primary-attempt-001 exists and the preregistration "
            "registers its ABSENCE at the freeze")
    if os.path.isdir(results):
        for name in sorted(os.listdir(results)):
            if name == "primary-attempt-001":
                continue                  # already named above
            problems.append(
                "results/%s exists: an attempt root under a second name is the "
                "same fact the freeze forbids, and results/ holds attempt roots "
                "and nothing else" % name)
    return problems


def derive_schedule(rounds: int) -> int:
    """`batch.py derive-schedule --rounds N` — §7 delta 7's re-pin command.

    Runs the search at N and prints the `batch` block the registry takes, so
    re-pinning at §2.1's swept round count is a registry edit against a DERIVED
    answer rather than a hand-written table. It writes nothing: the registry is
    edited by a person, and a driver that rewrites its own pins is a driver that
    can rewrite them after the freeze."""
    derived = derive_order(rounds=rounds)
    print("derived at %d rounds: %d blocks of %d + a tail of %d"
          % (derived["rounds"], derived["blocks"], SEQUENCES,
             derived["tailLength"]))
    print("blockOrder %s" % (list(derived["blockOrder"]),))
    print("tail       %s" % (list(derived["tail"]),))
    print("attained   position spread %d, transition spread %d, "
          "self-successions 0"
          % (derived["positionSpread"], derived["transitionSpread"]))
    print("batch.n %d, batch.slots %d"
          % (derived["runsPerArm"], derived["slots"]))
    print("These are the values harness/PINS.json's batch member takes; §2.1's "
          "sweep decides N and this decides nothing else.")
    return 0


# --- the argument surface ----------------------------------------------------

def _argument(argv: list, flag: str, default=None):
    if flag not in argv:
        return default
    index = argv.index(flag)
    if index + 1 >= len(argv):
        raise BatchError("%s needs a value" % flag)
    return argv[index + 1]


USAGE = (
    "usage: batch.py plan\n"
    "       batch.py run --scratch-parent DIR [--resume] [--runs N] [--pins PATH]\n"
    "                    [--golden PATH] [--cli-override PATH] [--dry-run]\n"
    "       batch.py capture --scratch-parent DIR [--captures DIR] [--out PATH]\n"
    "                    [--runs N] [--pins PATH] [--cli-override PATH]\n"
    "       batch.py capture-golden --slots DIR --out PATH [--min-slots N]\n"
    "       batch.py capture-isolation-negative --scratch-parent DIR [--out DIR]\n"
    "                    [--pins PATH] [--golden PATH] [--cli-override PATH]\n"
    "       batch.py shortfall --reason TEXT [--pins PATH]\n"
    "       batch.py sweep --scratch-parent DIR [--pins PATH]\n"
    "                    [--cli-override PATH] [--label NAME] [--settings LIST]\n"
    "                    [--dry-run]\n"
    "\n"
    "sweep is PREREGISTRATION.md §2.1's pre-pilot effort sweep: 3 settings x\n"
    "3 arms x 3 runs = 27 calls, sequential, arm-interleaved with A first,\n"
    "under PIN_LABEL=SWEEP, published in full under sweeps/<label>/ as\n"
    "SWEEP.json and SWEEP.md, citable: false and outside every population.\n"
    "--settings names a SUBSET of the registered three (a resumed or a\n"
    "single-setting run); it cannot introduce a fourth.\n"
    "       batch.py derive-schedule --rounds N\n"
    "\n"
    "--pins names a registry only under the stand-in study of the harness\n"
    "tests. In this tree it is refused unless it names harness/PINS.json:\n"
    "the production run path is judged against the canonical registry alone\n"
    "(round-10 finding R10-1).")

COMMANDS = ("plan", "run", "capture", "capture-golden",
            "capture-isolation-negative", "shortfall", "sweep",
            "derive-schedule")

# Flags a command line may still carry from an earlier driver, each removed by a
# registered decision. They refuse by name rather than being ignored: a command
# line that means something else now must not quietly do something else.
REMOVED = {
    "--start": "resumption is by global schedule index, not by slot index: "
               "`run --resume` continues at the ledger's next index",
    "--start-round": "a round number cannot resume a partly completed round "
                     "without either overlapping recorded slots or silently "
                     "omitting the rest of that round, and neither is detectable "
                     "after the fact from one. Use `run --resume`",
    "--slots": "the population root is derived from the harness's own location "
               "(harness/../arms) and no argument names it",
}


def print_plan() -> int:
    """The registered order and the balance it attains — the command the module
    had while the calling half was unported, kept because it is the one way to
    read the schedule without a registry, a wrapper or a call."""
    slots = schedule()
    profile = balance(slots)
    print("registered call order: %d slots, %d rounds, %d arms (%s)"
          % (len(slots), ROUNDS, POSITIONS, ", ".join(ARMS)))
    print("per arm: %s" % dict(sorted(profile["perArm"].items())))
    print("position spread %d, transition spread %d, self-successions %d"
          % (profile["positionSpread"], profile["transitionSpread"],
             profile["selfSuccessions"]))
    print("per-call timeout ceiling: %d s (apparatus; code %r)"
          % (CALL_TIMEOUT_SECONDS, "call-timeout"))
    return 0


def main(argv: list) -> int:
    if len(argv) < 2 or argv[1] not in COMMANDS:
        print(USAGE, file=sys.stderr)
        return 2
    command = argv[1]
    try:
        pins_path = _argument(argv, "--pins", DEFAULT_PINS)
        # ROUND-10 FINDING R10-1, at the argument surface as well as at the load
        # surface: the operator who types `--pins` at the production tree is
        # answered by the registry rule and not by whichever gate the command
        # happens to reach first.
        require_canonical_registry(pins_path)
        if command in ("run", "shortfall"):
            for flag, why in REMOVED.items():
                if flag in argv:
                    raise BatchError("%s is removed from `batch.py %s`: %s"
                                     % (flag, command, why))
        if command == "plan":
            return print_plan()
        if command == "derive-schedule":
            rounds = _argument(argv, "--rounds")
            if rounds is None:
                raise BatchError("--rounds is required: §7 delta 7 re-derives "
                                 "the schedule AT a round count, and §2.1 "
                                 "registers that count as an output of the "
                                 "pre-pilot effort sweep")
            return derive_schedule(int(rounds))
        if command == "run":
            runs = _argument(argv, "--runs")
            scratch_parent = _argument(argv, "--scratch-parent")
            if scratch_parent is None:
                raise BatchError("--scratch-parent is required")
            # An omitted --runs runs the registered order to its end from
            # wherever the ledger leaves off; there is no count to infer, because
            # the order is the registry's and its length is 150.
            return run_batch(int(runs) if runs is not None else None,
                             "--resume" in argv, scratch_parent, pins_path,
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
        if command == "sweep":
            scratch_parent = _argument(argv, "--scratch-parent")
            if scratch_parent is None:
                raise BatchError("--scratch-parent is required")
            named = _argument(argv, "--settings")
            return run_sweep(scratch_parent, pins_path,
                             _argument(argv, "--cli-override"),
                             _argument(argv, "--label"),
                             [name.strip() for name in named.split(",")
                              if name.strip()] if named else None,
                             "--dry-run" in argv)
        if command == "capture-golden":
            slots_dir = _argument(argv, "--slots")
            if slots_dir is None:
                raise BatchError("--slots is required")
            return capture_golden(slots_dir, _argument(argv, "--out"),
                                  int(_argument(argv, "--min-slots", 2)), pins_path)
        return declare_shortfall(_argument(argv, "--reason"), pins_path)
    except (BatchError, transcript_check.TranscriptError,
            integrity.IntegrityError) as error:
        print("refused: %s" % error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
