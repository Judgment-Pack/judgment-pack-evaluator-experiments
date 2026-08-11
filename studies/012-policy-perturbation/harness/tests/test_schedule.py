"""§2.8's registered call order, re-derived and property-checked.

The five properties are asserted over the expanded 150-slot order, each
RE-DERIVED from the Williams table and the three registered block orders
rather than restated as constants — §2.8 says the harness test does exactly
that. The expansion here is this test's own; a further test asserts
`batch.schedule()` equals it, so the driver cannot drift from the
registration while the properties still pass.

Round 12, finding 4: they are re-derived from THIS FILE'S BYTES. §2.8's ten
sequences, its three block orders, its five property cells and its transition
matrix are all parsed out of `PREREGISTRATION.md` — each by an anchor unique in
the file, each parser asserting that uniqueness — and diffed against the
constants below and the expansion's own counters. The transcription is kept
beside the parse rather than replaced by it: the construction still checks a
typo in `FIRST_ROW`, and a one-sided edit of §2.8 now names its own drift site
instead of failing six tests at once. Before this the whole module was a copy
checking a copy, and a registration-only edit stayed green.
"""
import itertools
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
sys.path.insert(0, HARNESS)

import fixtures  # noqa: E402  (conftest.py puts this directory on sys.path)

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
# §2.8's fenced block, matched by its own shape rather than by a line number:
# `block N (rounds  a-b):  W… W…`. Three lines in the file match it and no
# other line does.
BLOCK_LINE = re.compile(
    r"^block (\d+) \(rounds\s+(\d+)-(\d+)\):\s+(W\d+(?:\s+W\d+)*)\s*$",
    re.MULTILINE)


def registered_sequences(body):
    """§2.8's ten Williams sequences, parsed out of the registration by the
    table's own header — the shape-based idiom §3.3's and §5's parity tests
    use, so a table that moves in the file is still the same table."""
    matches = [rows for cells, rows in fixtures.markdown_tables(body)
               if [fixtures.plain(cell) for cell in cells] == ["", "order"]]
    assert len(matches) == 1, (
        "PREREGISTRATION.md holds %d tables with the header ['', 'order']; "
        "§2.8's ten sequences are identified by that header" % len(matches))
    return {fixtures.plain(name): tuple(arm.strip() for arm
                                        in fixtures.plain(order).split(","))
            for name, order in matches[0]}


def registered_blocks(body):
    """§2.8's three block orders, parsed out of the fence."""
    found = BLOCK_LINE.findall(body)
    assert [(int(number), int(first), int(last))
            for number, first, last, _names in found] == [
        (1, 1, 10), (2, 11, 20), (3, 21, 30)], (
        "§2.8 registers three blocks of ten rounds each; this file's fence "
        "reads %r" % (found,))
    return tuple(tuple(names.split()) for _n, _f, _l, names in found)


def registered_matrix(body):
    """§2.8's published transition matrix, parsed out of the fence whose header
    row is the five arm names."""
    lines = body.splitlines()
    heads = [index for index, line in enumerate(lines)
             if line.split() == list(ARMS)]
    assert len(heads) == 1, (
        "PREREGISTRATION.md holds %d lines that are exactly the five arm "
        "names; §2.8's matrix is identified by that header" % len(heads))
    matrix = {}
    for line in lines[heads[0] + 1:heads[0] + 1 + len(ARMS)]:
        cells = line.split()
        matrix[cells[0]] = {arm: int(cell)
                            for arm, cell in zip(ARMS, cells[1:])
                            if cell != "-"}
    return matrix


def registered_properties(body):
    """§2.8's five derived properties, name to registered value, both sides
    normalized by `fixtures.plain()` so the file's bolding is not a
    difference."""
    matches = [rows for cells, rows in fixtures.markdown_tables(body)
               if [fixtures.plain(cell) for cell in cells]
               == ["property", "registered value"]]
    assert len(matches) == 1, (
        "PREREGISTRATION.md holds %d tables with the header ['property', "
        "'registered value']; §2.8's five properties are identified by that "
        "header" % len(matches))
    return {fixtures.plain(name): fixtures.plain(value)
            for name, value in matches[0]}


def one(counter):
    """The single value a balanced counter takes — asserted single before it is
    used, because a property that reads "all six" must not be written out of a
    counter holding a 5 and a 7."""
    values = set(counter.values())
    assert len(values) == 1, counter
    return values.pop()


def derived_properties():
    """The five property cells §2.8 publishes, written out of the expansion's
    own counters in the file's own words — so the diff against the registration
    is arithmetic against prose and not prose against prose."""
    slots = expand()
    per_arm = Counter(arm for _, _, _, arm in slots)
    positions = Counter((arm, position) for _, _, position, arm in slots)
    within, boundary, total = Counter(), Counter(), Counter()
    for left, right in zip(slots, slots[1:]):
        pair = (left[3], right[3])
        total[pair] += 1
        (within if left[1] == right[1] else boundary)[pair] += 1
    # The cell says no arm ever immediately follows itself, so that is earned
    # here rather than copied into the string.
    assert all(left != right for left, right in boundary), boundary
    spread = Counter(boundary.values())
    return {
        "slots per arm": "%d, all five equal" % one(per_arm),
        "position counts": (
            "each arm in each within-round position exactly %d times "
            "(%d cells, all %d)"
            % (one(positions), len(positions), one(positions))),
        "within-round directed transitions": (
            "each of the %d ordered pairs X->Y exactly %d times "
            "(%d transitions)"
            % (len(within), one(within), sum(within.values()))),
        "round-boundary transitions": (
            "%d in total; no arm ever immediately follows itself; %d ordered "
            "pairs occur twice and %d occur once"
            % (sum(boundary.values()), spread[2], spread[1])),
        "total directed transitions": (
            "%d; every ordered pair occurs %d or %d times — max minus min "
            "is %d"
            % (sum(total.values()), min(total.values()), max(total.values()),
               max(total.values()) - min(total.values()))),
    }


def williams():
    increment = {arm: ARMS[(ARMS.index(arm) + 1) % 5] for arm in ARMS}
    rows = [FIRST_ROW]
    for _ in range(4):
        rows.append(tuple(increment[arm] for arm in rows[-1]))
    reversed_rows = [tuple(reversed(row)) for row in rows]
    return {"W%d" % (i + 1): row
            for i, row in enumerate(rows + reversed_rows)}


def test_the_construction_reproduces_the_published_table(preregistration):
    """Three-way: the construction, the transcription above, and §2.8's own ten
    rows as parsed out of the registration. Round 12, finding 4 — the first two
    checked each other and neither read the file."""
    assert williams() == PUBLISHED == registered_sequences(preregistration)


def test_the_registered_block_orders_are_the_files(preregistration):
    """Round 12, finding 4: the three block orders are the file's, not a copy
    of them. Nothing else in the suite opens §2.8, so a registration-only edit
    to this fence used to leave the whole suite green."""
    assert registered_blocks(preregistration) == BLOCKS


def test_the_five_registered_properties_are_the_arithmetics(preregistration):
    """§2.8: "the properties the harness test asserts over the expanded
    150-slot order, each re-derived from the table above rather than restated".
    Round 12, finding 4: that sentence is now true of this file's bytes rather
    than of a copy of them — the five cells are parsed and diffed against the
    strings the counters write."""
    assert registered_properties(preregistration) == derived_properties()


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


def test_the_registered_transition_matrix(preregistration):
    # §2.8 publishes the full matrix; the file's own table must be the
    # arithmetic's, entry for entry. Round 12, finding 4: the matrix is READ
    # from the registration rather than transcribed here, and its shape is
    # asserted first so a truncated fence cannot satisfy the loop vacuously.
    registered = registered_matrix(preregistration)
    assert set(registered) == set(ARMS), registered
    for predecessor, row in registered.items():
        assert set(row) == set(ARMS) - {predecessor}, (predecessor, row)
    assert sum(sum(row.values()) for row in registered.values()) == 149
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
