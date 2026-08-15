#!/usr/bin/env python3
"""The batch driver — PARTIAL PORT, schedule core only.

PORTED from Study 012's `harness/batch.py`
(sha256 `6ee3bf3e2b217257fe38976df4610461c9ed9866db485678348b3ad8036fdcf3`, the
destination digest Study 012's own `harness/PORTS.md` records for it, at commit
`019c95be9e86c575878015954dfec17e4f84e683`). `harness/PORTS.md` in THIS study
carries the two-sided table and the enumerated change list; `harness/integrity.py`
machine-reads it and binds this file to that digest before anything runs.

**This is a partial port and says so in its own bytes.** What is carried is the
registered call order and the constants that decide what a slot is; what is
NOT carried is the whole of Study 012's driver — preflight, the golden
recapture, slot creation and sealing, the chained ledger, resume, shortfall,
the isolation negative control. `harness/SCAFFOLD.md` lists every deferred
piece by name and by source line range, so the remainder is a scheduled port
and not a discovery. Nothing here calls the wrapper yet: this module plans, and
`harness/PORTS.md` records that the calling half is unported.

The enumerated changes to what IS carried (PREREGISTRATION.md §2 "Batch shape",
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

Deliberately unchanged: `schedule_entries()`'s derivation of `slotIndex` from
the order, `slot_path()`'s `arms/<ARM>/authoring/run-NNN` layout, and the five
`SCHEDULE_KEYS` — the members a slot carries so a drift is a per-slot check and
not a claim about bookkeeping.
"""
from __future__ import annotations
import itertools
import os
import sys
from collections import Counter

# The ceremony's commands run with bytecode writing disabled (Study 012 §2.10,
# carried): set structurally, not left to the operator's environment.
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
ARMS_ROOT = os.path.join(STUDY, "arms")


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
# 50 rounds of three arms: eight whole blocks of the six sequences (48 rounds)
# and a registered two-sequence tail. The tail exists because 50 is not a
# multiple of 6 — stated here rather than hidden in an expansion, because it is
# the reason exact balance is unavailable and a floor is registered instead.
BLOCKS = 8
BLOCK_ORDER = ("W1", "W2", "W3", "W4", "W6", "W5")
TAIL = ("W4", "W6")
ROUNDS = BLOCKS * SEQUENCES + len(TAIL)          # 50
RUNS_PER_ARM = ROUNDS                            # 50 slots per arm
REGISTERED_SLOTS = ROUNDS * POSITIONS            # 150
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
# addition (change 3 above); 0, 1, 10 and 11 are Study 012's, unchanged.
WRAPPER_EXIT_MEANINGS = {
    0: ("complete", "the call exited 0 and the slot is complete"),
    1: ("preflight-refused", "a pre-call refusal; nothing was called and no "
                             "slot was left behind"),
    10: ("call-nonzero-exit", "the call exited non-zero; the slot is retained "
                              "without completion.txt"),
    11: ("slot-shape", "the run produced other than exactly one new session; "
                       "slot retained"),
    12: ("call-timeout", "the call reached the registered %d s ceiling and was "
                         "terminated; slot retained" % CALL_TIMEOUT_SECONDS),
}

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
    ("golden-context-mismatch", "golden-context mismatch"),
    ("binary-digest-mismatch", "binary digest mismatch"),
    ("transcript-refused", "transcript refusal"),
)
AUTHORING_CODES = (
    ("no-marker-block", "no extractable marker block"),
    ("unparseable-artifact", "unparseable artifact"),
    ("schema-invalid-pack", "schema-invalid pack"),
    ("opa-check-failed", "opa check failure"),
    ("v0-syntax", "v0-syntax"),
    ("unreadable-output-shape", "unreadable output shape"),
)


def _partition() -> dict:
    """{code: ("apparatus"|"authoring", the phrase §1a registers)}.

    Built rather than written out, so the two tuples above are the only place a
    code is named and a code that drifted into both sides refuses at import."""
    table = {}
    for side, rows in (("apparatus", APPARATUS_CODES),
                       ("authoring", AUTHORING_CODES)):
        for code, phrase in rows:
            if code in table:
                raise BatchError(
                    "the code %r is registered on both sides of §1a's "
                    "partition: pipeline-invalid and authoring outcomes are "
                    "disjoint by construction" % code)
            table[code] = (side, phrase)
    return table


CODE_PARTITION = _partition()


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


def round_order(block=BLOCK_ORDER, tail=TAIL) -> tuple:
    """The 50 round names: the block order eight times, then the tail.

    A permutation check on both, for the same reason Study 012 checked its three
    blocks: every sequence holds every arm once, so a block that ran W4 twice
    and W3 never still gives 50 slots per arm and destroys the transition
    balance the registration is about."""
    rows = williams()
    if not all(isinstance(name, str) for name in block) \
            or sorted(block) != sorted(rows):
        raise BatchError("the registered block order is %r, which is not a "
                         "permutation of W1…W%d" % (list(block), SEQUENCES))
    if len(tail) != len(set(tail)) or any(name not in rows for name in tail):
        raise BatchError("the registered tail is %r, which is not a sequence of "
                         "distinct members of W1…W%d" % (list(tail), SEQUENCES))
    if len(block) * BLOCKS + len(tail) != ROUNDS:
        raise BatchError("%d blocks of %d and a tail of %d is %d rounds; the "
                         "registration is %d"
                         % (BLOCKS, len(block), len(tail),
                            len(block) * BLOCKS + len(tail), ROUNDS))
    return tuple(list(block) * BLOCKS + list(tail))


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


def derive_order(blocks=BLOCKS, tail_length=None):
    """The registered order, DERIVED: the search `BLOCK_ORDER` and `TAIL` are
    the answer to.

    Over every one of the 720 orderings of W1…W6 and every one of the 30 ordered
    two-sequence tails, keep the orders in which no arm ever immediately follows
    itself, and return the lexicographically-least (by W-index) of those that
    minimize the pair (position spread, transition spread). Exact balance is
    arithmetically unavailable at three arms and 50 rounds — 50 slots do not
    divide over 3 positions and 149 transitions do not divide over 6 ordered
    pairs — so the registration is the FLOOR of both spreads, which this search
    establishes rather than assumes: it reports the minimum it found, and the
    harness test requires that minimum to be (1, 1) and to be attained by the
    constants above.

    Deliberately not run at import: it is a second of work and the driver plans
    the same order every time. The constants are the cache; this is the
    authority."""
    tail_length = ROUNDS - blocks * SEQUENCES if tail_length is None else tail_length
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
        raise BatchError("no order of W1…W%d avoids an arm following itself"
                         % SEQUENCES)
    (spreads, permutation, tail) = best
    return {"blockOrder": permutation, "tail": tail,
            "positionSpread": spreads[0], "transitionSpread": spreads[1]}


def schedule(block=BLOCK_ORDER, tail=TAIL) -> list:
    """The 150 slots of §2's registered call order, expanded deterministically
    from the table above: `[(globalIndex, round, position, arm)]`, global index
    1…150, round 1…50, within-round position 1…3.

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
    # Both spreads are at the arithmetic floor for three arms over 50 rounds, so
    # a schedule that drifted from the registered order would have to attain the
    # same floor to pass here, and the harness test pins the order itself.
    if profile["selfSuccessions"] or profile["positionSpread"] > 1 \
            or profile["transitionSpread"] > 1:
        raise BatchError(
            "the expanded call order has %d self-successions, position spread "
            "%d and transition spread %d; §2 registers none, 1 and 1"
            % (profile["selfSuccessions"], profile["positionSpread"],
               profile["transitionSpread"]))
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


def main(argv: list) -> int:
    """The plan, printed. The calling half of this driver is unported
    (`harness/SCAFFOLD.md`), so this entry deliberately does nothing but publish
    the order it would run and the balance it attains — there is no `run`
    subcommand to mistake for one."""
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
    print("NOT PORTED YET: preflight, golden recapture, slot creation and "
          "sealing, the chained ledger, resume, shortfall, the isolation "
          "negative control — see harness/SCAFFOLD.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
