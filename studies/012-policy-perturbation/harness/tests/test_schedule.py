"""§2.8's registered call order, re-derived and property-checked.

The five properties are asserted over the expanded 150-slot order, each
RE-DERIVED from the Williams table and the three registered block orders
rather than restated as constants — §2.8 says the harness test does exactly
that. The expansion here is this test's own; a further test asserts
`batch.schedule()` equals it, so the driver cannot drift from the
registration while the properties still pass.
"""
import itertools
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
sys.path.insert(0, HARNESS)

ARMS = ("A", "B", "C", "D", "E")

# §2.8: W1-W5 are the cyclic rows of the Williams first row A, B, E, C, D —
# cyclic in the SYMBOLS (each row increments every arm A->B->C->D->E), which
# is the standard Williams construction — and W6-W10 are those five rows
# reversed. The published ten-row table is restated here verbatim so the
# construction and the registration check each other.
FIRST_ROW = ("A", "B", "E", "C", "D")
PUBLISHED = {
    "W1": ("A", "B", "E", "C", "D"), "W2": ("B", "C", "A", "D", "E"),
    "W3": ("C", "D", "B", "E", "A"), "W4": ("D", "E", "C", "A", "B"),
    "W5": ("E", "A", "D", "B", "C"), "W6": ("D", "C", "E", "B", "A"),
    "W7": ("E", "D", "A", "C", "B"), "W8": ("A", "E", "B", "D", "C"),
    "W9": ("B", "A", "C", "E", "D"), "W10": ("C", "B", "D", "A", "E"),
}
BLOCKS = (
    ("W2", "W4", "W7", "W10", "W1", "W9", "W8", "W6", "W3", "W5"),
    ("W4", "W3", "W2", "W10", "W9", "W8", "W5", "W1", "W7", "W6"),
    ("W4", "W6", "W5", "W7", "W1", "W2", "W10", "W8", "W9", "W3"),
)


def williams():
    increment = {arm: ARMS[(ARMS.index(arm) + 1) % 5] for arm in ARMS}
    rows = [FIRST_ROW]
    for _ in range(4):
        rows.append(tuple(increment[arm] for arm in rows[-1]))
    reversed_rows = [tuple(reversed(row)) for row in rows]
    return {"W%d" % (i + 1): row
            for i, row in enumerate(rows + reversed_rows)}


def test_the_construction_reproduces_the_published_table():
    assert williams() == PUBLISHED


def expand():
    """[(globalIndex, round, position, arm)] — 150 slots, three blocks of the
    ten Williams sequences in the registered block orders."""
    rows = williams()
    slots = []
    index = 0
    round_number = 0
    for block in BLOCKS:
        for name in block:
            round_number += 1
            for position, arm in enumerate(rows[name], start=1):
                index += 1
                slots.append((index, round_number, position, arm))
    return slots


def test_the_williams_square_is_a_williams_square():
    rows = williams()
    assert len(rows) == 10
    for name, row in rows.items():
        assert sorted(row) == sorted(ARMS), name
    # each arm in each position exactly twice over the ten sequences
    for position in range(5):
        count = Counter(row[position] for row in rows.values())
        assert count == Counter({arm: 2 for arm in ARMS}), position
    # each of the twenty ordered pairs adjacent exactly twice
    adjacency = Counter()
    for row in rows.values():
        for left, right in zip(row, row[1:]):
            adjacency[(left, right)] += 1
    assert len(adjacency) == 20
    assert set(adjacency.values()) == {2}


def test_slots_per_arm():
    slots = expand()
    assert len(slots) == 150
    assert Counter(arm for _, _, _, arm in slots) == Counter(
        {arm: 30 for arm in ARMS})


def test_position_counts():
    # each arm in each within-round position exactly 6 times — 25 cells, all 6
    count = Counter((arm, position) for _, _, position, arm in expand())
    assert len(count) == 25
    assert set(count.values()) == {6}


def test_within_round_directed_transitions():
    # each of the 20 ordered pairs exactly 6 times — 120 transitions
    transitions = Counter()
    slots = expand()
    for left, right in zip(slots, slots[1:]):
        if left[1] == right[1]:
            transitions[(left[3], right[3])] += 1
    assert sum(transitions.values()) == 120
    assert len(transitions) == 20
    assert set(transitions.values()) == {6}


def test_round_boundary_transitions():
    # 29 in total; no arm follows itself; 9 pairs twice and 11 once
    transitions = Counter()
    slots = expand()
    for left, right in zip(slots, slots[1:]):
        if left[1] != right[1]:
            transitions[(left[3], right[3])] += 1
    assert sum(transitions.values()) == 29
    assert all(left != right for left, right in transitions)
    spread = Counter(transitions.values())
    assert spread == Counter({2: 9, 1: 11})


def test_total_directed_transitions():
    # 149 transitions; every ordered pair 7 or 8 times — max minus min is 1
    transitions = Counter()
    slots = expand()
    for left, right in zip(slots, slots[1:]):
        transitions[(left[3], right[3])] += 1
    assert sum(transitions.values()) == 149
    assert len(transitions) == 20
    assert set(transitions.values()) <= {7, 8}
    assert max(transitions.values()) - min(transitions.values()) == 1


def test_the_registered_transition_matrix():
    # §2.8 publishes the full matrix; the file's own table must be the
    # arithmetic's, entry for entry.
    registered = {
        "A": {"B": 7, "C": 7, "D": 7, "E": 8},
        "B": {"A": 7, "C": 8, "D": 8, "E": 7},
        "C": {"A": 7, "B": 7, "D": 8, "E": 8},
        "D": {"A": 8, "B": 8, "C": 7, "E": 7},
        "E": {"A": 8, "B": 7, "C": 8, "D": 7},
    }
    transitions = Counter()
    slots = expand()
    for left, right in zip(slots, slots[1:]):
        transitions[(left[3], right[3])] += 1
    for predecessor, row in registered.items():
        for successor, expected in row.items():
            assert transitions[(predecessor, successor)] == expected, (
                predecessor, successor)


def test_batch_schedule_equals_the_registration():
    import batch
    assert batch.schedule() == expand()
