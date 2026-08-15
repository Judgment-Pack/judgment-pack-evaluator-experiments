"""§2's registered call order for three arms, re-derived and property-checked.

Study 012's test asserted five properties over a 150-slot order that was
EXACTLY balanced in all of them. This study's 150 slots are 50 rounds of three,
and 50 rounds do not divide over 3 positions nor 149 transitions over 6 ordered
pairs — so exact balance is arithmetically unavailable and what is registered is
the FLOOR of both spreads. The tests below therefore assert two different kinds
of thing, and keeping them apart is the point:

  * the EXACT properties that survive three arms (per-arm slot counts, the
    Williams square's own two properties, no arm ever immediately following
    itself, the contiguity of every index);
  * the FLOOR properties (position spread 1, directed-transition spread 1),
    each asserted against a spread this file computes from the expansion's own
    counters — and, separately, against `batch.derive_order()`, which
    establishes by exhaustive search that no order of the six sequences does
    better. That second assertion is what stops "carryover-balanced" from being
    an adjective: if a better order existed, the search would find it and this
    test would fail rather than pass with a worse one registered.

The counters here are this file's own, not `batch.balance()`'s, wherever a
property could be satisfied by both sides sharing one bug.
"""
from collections import Counter

import pytest

import batch


def expansion():
    return batch.schedule()


def test_the_williams_square_is_a_williams_square():
    rows = batch.williams()
    assert len(rows) == 6
    for name, row in rows.items():
        assert sorted(row) == sorted(batch.ARMS), name
    # each arm in each position exactly twice over the six sequences
    for position in range(3):
        count = Counter(row[position] for row in rows.values())
        assert count == Counter({arm: 2 for arm in batch.ARMS}), position
    # each of the six ordered pairs adjacent exactly twice
    adjacency = Counter()
    for row in rows.values():
        for left, right in zip(row, row[1:]):
            adjacency[(left, right)] += 1
    assert len(adjacency) == 6
    assert set(adjacency.values()) == {2}


def test_the_registered_shape():
    slots = expansion()
    assert len(slots) == 150 == batch.REGISTERED_SLOTS
    assert [index for index, _, _, _ in slots] == list(range(1, 151))
    assert sorted(set(round_index for _, round_index, _, _ in slots)) == \
        list(range(1, 51))
    assert set(position for _, _, position, _ in slots) == {1, 2, 3}
    assert Counter(arm for _, _, _, arm in slots) == \
        Counter({arm: 50 for arm in batch.ARMS})


def test_position_counts_are_at_the_floor():
    # 50 slots over 3 positions cannot be equal. Each arm holds two positions
    # 17 times and one 16 times; every cell is 16 or 17 and the spread is 1.
    counts = Counter((arm, position) for _, _, position, arm in expansion())
    assert len(counts) == 9
    assert set(counts.values()) == {16, 17}
    for arm in batch.ARMS:
        per_arm = sorted(counts[(arm, position)] for position in (1, 2, 3))
        assert per_arm == [16, 17, 17], arm


def test_no_arm_ever_immediately_follows_itself():
    slots = expansion()
    for left, right in zip(slots, slots[1:]):
        assert left[3] != right[3], (left, right)


def test_total_directed_transitions_are_at_the_floor():
    # 149 transitions over the 6 ordered pairs: five pairs 25 times and one 24.
    transitions = Counter()
    slots = expansion()
    for left, right in zip(slots, slots[1:]):
        transitions[(left[3], right[3])] += 1
    assert sum(transitions.values()) == 149
    assert len(transitions) == 6
    assert set(transitions.values()) <= {24, 25}
    assert max(transitions.values()) - min(transitions.values()) == 1
    assert Counter(transitions.values()) == Counter({25: 5, 24: 1})


def test_the_within_round_and_boundary_split_adds_up():
    slots = expansion()
    within, boundary = Counter(), Counter()
    for left, right in zip(slots, slots[1:]):
        (within if left[1] == right[1] else boundary)[(left[3], right[3])] += 1
    assert sum(within.values()) == 100      # 50 rounds x 2 within-round
    assert sum(boundary.values()) == 49     # 49 round boundaries
    profile = batch.balance(slots)
    assert profile["within"] == within and profile["boundary"] == boundary


def test_balance_reports_the_registered_spreads():
    profile = batch.balance(expansion())
    assert profile["positionSpread"] == 1
    assert profile["transitionSpread"] == 1
    assert profile["selfSuccessions"] == 0


def test_the_registered_order_is_the_derivation():
    """The constants are a cache; the search is the authority.

    Exhaustive over all 720 block orderings and all 30 ordered tails, so a
    registered order that was merely good rather than optimal fails here."""
    derived = batch.derive_order()
    assert derived["blockOrder"] == batch.BLOCK_ORDER
    assert derived["tail"] == batch.TAIL
    assert (derived["positionSpread"], derived["transitionSpread"]) == (1, 1)


def test_slot_entries_and_paths():
    entries = batch.schedule_entries()
    assert len(entries) == 150
    for entry in entries:
        assert tuple(sorted(entry)) == tuple(sorted(batch.SCHEDULE_KEYS))
    for arm in batch.ARMS:
        indices = [entry["slotIndex"] for entry in entries if entry["arm"] == arm]
        assert indices == list(range(1, 51)), arm
    first = entries[0]
    assert batch.slot_path(first).endswith(
        "arms/%s/authoring/run-001" % first["arm"])


def test_a_block_order_that_is_not_a_permutation_refuses():
    with pytest.raises(batch.BatchError):
        batch.schedule(block=("W1", "W1", "W3", "W4", "W6", "W5"))
    with pytest.raises(batch.BatchError):
        batch.williams(first_row=("A", "A", "C"))
    with pytest.raises(batch.BatchError):
        batch.schedule(tail=("W4", "W4"))


def test_the_registry_and_the_driver_are_one_order(pins):
    """The registry's own order expanded through the driver's own function, and
    required to equal the driver's default expansion — so a registry that
    registered a different order refuses rather than being quietly ignored."""
    order = pins["batch"]["order"]
    assert tuple(order["firstRow"]) == batch.WILLIAMS_FIRST_ROW
    assert order["blocks"] == batch.BLOCKS
    assert batch.schedule(block=tuple(order["blockOrder"]),
                          tail=tuple(order["tail"])) == batch.schedule()
    assert pins["batch"]["n"] == batch.RUNS_PER_ARM
    assert pins["batch"]["slots"] == batch.REGISTERED_SLOTS
    assert tuple(pins["batch"]["arms"]) == batch.ARMS


def test_the_registry_and_the_driver_are_one_timeout_ceiling(pins):
    """The wrapper reads the ceiling from the registry and the driver classifies
    on its own constant; two ceilings would be two studies."""
    assert pins["batch"]["callTimeoutSeconds"] == batch.CALL_TIMEOUT_SECONDS == 2700
    assert pins["batch"]["timeoutKillAfterSeconds"] == \
        batch.TIMEOUT_KILL_AFTER_SECONDS


def test_the_registered_batch_shape_is_the_registrations(preregistration):
    """§2 "Batch shape" states N, the slot count and the ceiling in prose; the
    driver derives them. A one-sided edit names its own drift site.

    Flattened first: the registration wraps its own sentences, so "Per-call
    timeout ceiling" is split across two lines in the file and a raw substring
    test would assert the line wrapping rather than the number."""
    flat = " ".join(preregistration.replace("*", "").split())
    assert "N = 50 runs/arm, 150 slots" in flat
    assert "Per-call timeout ceiling: 2700 s, an apparatus bound" in flat
    assert "timeout rate above the registered cap (10% of slots)" in flat
    assert batch.RUNS_PER_ARM == 50 and batch.REGISTERED_SLOTS == 150
    assert batch.CALL_TIMEOUT_SECONDS == 2700
