#!/usr/bin/env python3
"""Section 2a.4's committed threshold deriver — sealed BEFORE the pilot runs.

WHAT THIS EMITS, AND WHAT NEVER ENTERS IT
-----------------------------------------
"A committed `calibration/derive_floor.py`, sealed before the pilot runs,
emitting any threshold from the pilot's own per-arm counts by an exact
Clopper-Pearson rule, with **no human number entering**." The only numbers in
this file are the registered alpha (section 2a.1's one-sided 95 % bound — the
same table that showed 019's 5/5 pilot licensed 0.549, not the 0.60 it was
cited for) and the pilot's registered size; every threshold is derived from
the counts the pilot RECORD carries, through `e4lib/stats.py`'s ported and
test-vector-certified exact Clopper-Pearson implementation, and the go/no-go
compares a DERIVED value against a DECLARED one (`PINS.json`'s
`calibration.minimumViable`, the maintainer's pre-pilot declaration under
section 2a.4(2)) — this file computes, it never chooses.

THE RECORD CONTRACT (round-1 finding R1-17: the freeze gate used to look for
a labelled subtree and validate nothing)
----------------------------------------
The pilot publishes `calibration/<label>/PILOT-RATES.json`:

    {"label": ..., "citable": false, "perArm": {
        "A": {"calls": 12, "perfect": k, "identityPass": m},
        "B": {...}, "C": {...}}}

`validate_record()` refuses a record whose arms are not exactly A/B/C, whose
calls are not the registered pilot size, whose counts are not integers within
[0, calls], or which claims citability. `make_manifest.py`'s freeze gate calls
it, so a freeze can no longer be satisfied by a directory that merely exists.

WHAT THE GO/NO-GO READS
-----------------------
Both derived floors are emitted for every arm — the exact CP lower bound of
the PERFECT rate and of the IDENTITY-PASSING rate — because both counts are
in the record and hiding one would be a choice. Which floor the DECLARED
minimum binds is the maintainer's registered declaration
(`calibration.minimumViableBasis`), made with the §2.1 sweep's exposure on
the record: §5.7 registers arm A's imperfection as a REPORTED RESULT, so a
perfect-rate minimum over all arms would abort by design and the declaration
must say so if it means to. Under M-9's ruling the below-minimum branch
ABORTS: no freeze, no descope.

Under C5's append-only re-pilot rule the derived threshold is the MAXIMUM
over all pilots; this file derives one pilot's floors and the maximum is
taken over its outputs, never inside them.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
HARNESS = os.path.join(STUDY, "harness")
if HARNESS not in sys.path:
    sys.path.insert(0, HARNESS)

from e4lib import stats  # noqa: E402

#: Section 2a.2's registered pilot size.
PILOT_CALLS_PER_ARM = 12
ARMS = ("A", "B", "C")
RECORD_NAME = "PILOT-RATES.json"

#: Section 2a.1's registered alpha — ONE-SIDED 95 %. `stats.lower_bound()` is
#: the two-sided interval's lower edge (its `ALPHA` is 1/40, one tail of a
#: 95 % interval) and quietly using it would change the registered rule:
#: at 12/12 it gives 0.735 where §2a.1's own table registers **0.779**. The
#: exact machinery is still `stats.py`'s — `_tail_ge` and `_bisect`, the
#: ported, certified, platform-stable primitives — applied at the alpha the
#: registration names, and `test_pilot.py` binds the three n=12 outputs to
#: the table's own bytes.
ONE_SIDED_ALPHA = Fraction(1, 20)


def one_sided_lower_bound(k: int, n: int) -> float:
    """Exact one-sided 95 % Clopper-Pearson lower bound: the largest p (to
    IEEE-754 bisection) with P(X >= k | p) < alpha still on its left."""
    if k == 0:
        return 0.0
    return stats._bisect(
        lambda p: stats._tail_ge(k, n, Fraction(p)) < ONE_SIDED_ALPHA)


class FloorError(Exception):
    """A refusal. The message names the precondition that failed."""


def validate_record(record: dict) -> dict:
    """The R1-17 schema gate: a pilot record is the registered shape or it is
    not a pilot record, and the freeze gate reads this refusal."""
    if not isinstance(record, dict):
        raise FloorError("FLOOR-RECORD the pilot record is not an object")
    if record.get("citable") is not False:
        raise FloorError(
            "FLOOR-RECORD the pilot record must say citable: false in its own "
            "bytes (§2a.2's third registered difference)")
    per_arm = record.get("perArm")
    if not isinstance(per_arm, dict) or sorted(per_arm) != sorted(ARMS):
        raise FloorError(
            "FLOOR-RECORD the pilot record's arms are %r and the registered "
            "arms are exactly A, B, C"
            % (sorted(per_arm) if isinstance(per_arm, dict) else per_arm))
    for arm in ARMS:
        cell = per_arm[arm]
        calls = cell.get("calls")
        if calls != PILOT_CALLS_PER_ARM:
            raise FloorError(
                "FLOOR-RECORD arm %s records %r calls and §2a.2 registers the "
                "pilot at %d/arm" % (arm, calls, PILOT_CALLS_PER_ARM))
        for member in ("perfect", "identityPass"):
            count = cell.get(member)
            if not isinstance(count, int) or isinstance(count, bool) \
                    or not 0 <= count <= calls:
                raise FloorError(
                    "FLOOR-RECORD arm %s's %s is %r; an integer in [0, %d] is "
                    "the registered shape" % (arm, member, count, calls))
    return record


def derive(record: dict) -> dict:
    """Both per-arm floors, by the exact rule, plus the go/no-go inputs."""
    validate_record(record)
    floors = {}
    for arm in ARMS:
        cell = record["perArm"][arm]
        floors[arm] = {
            "calls": cell["calls"],
            "perfect": cell["perfect"],
            "identityPass": cell["identityPass"],
            "perfectFloor": one_sided_lower_bound(cell["perfect"],
                                                  cell["calls"]),
            "identityFloor": one_sided_lower_bound(cell["identityPass"],
                                                   cell["calls"]),
        }
    return {"rule": "exact one-sided 95 % Clopper-Pearson lower bound "
                    "(e4lib/stats.py's exact primitives at §2a.1's alpha)",
            "pilotCallsPerArm": PILOT_CALLS_PER_ARM,
            "perArm": floors}


def go_no_go(derived: dict, minimum, basis: str) -> dict:
    """DECLARED minimum against DERIVED floors. Aborts, never descopes (M-9).

    `minimum` and `basis` come from the registry's maintainer declaration —
    this file validates and applies them and chooses neither."""
    if not isinstance(minimum, (int, float)) or isinstance(minimum, bool):
        raise FloorError(
            "FLOOR-DECLARATION calibration.minimumViable is %r; §2a.4(2)'s "
            "declared value must exist before this gate can be evaluated"
            % (minimum,))
    if basis not in ("perfectFloor", "identityFloor"):
        raise FloorError(
            "FLOOR-DECLARATION calibration.minimumViableBasis is %r; the "
            "declaration names which derived floor it binds "
            "(perfectFloor or identityFloor)" % (basis,))
    failing = sorted(arm for arm in ARMS
                     if derived["perArm"][arm][basis] < minimum)
    return {"minimumViable": minimum, "basis": basis,
            "failingArms": failing,
            "go": not failing,
            "consequence": ("proceed toward the freeze" if not failing else
                            "ABORT: §2a.4(2) under ruling M-9 — the study "
                            "does not freeze and does not descope")}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Section 2a.4's threshold deriver (sealed pre-pilot).")
    parser.add_argument("--record", required=True,
                        help="path to the pilot's PILOT-RATES.json")
    args = parser.parse_args(argv)
    with open(args.record, "rb") as handle:
        record = json.loads(handle.read().decode("utf-8"))
    derived = derive(record)
    with open(os.path.join(HARNESS, "PINS.json"), "rb") as handle:
        pins = json.loads(handle.read().decode("utf-8"))
    calibration = pins.get("calibration") or {}
    verdict = go_no_go(derived, calibration.get("minimumViable"),
                       calibration.get("minimumViableBasis"))
    sys.stdout.write(json.dumps({"derived": derived, "goNoGo": verdict},
                                indent=2, sort_keys=True) + "\n")
    return 0 if verdict["go"] else 3


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FloorError as refusal:
        sys.stderr.write("%s\n" % refusal)
        sys.exit(1)
