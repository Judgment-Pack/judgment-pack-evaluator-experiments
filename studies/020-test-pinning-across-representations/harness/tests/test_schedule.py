"""§2's registered call order for three arms, re-derived and property-checked
AT WHATEVER ROUND COUNT THE REGISTRY NAMES.

REBUILT, NOT PATCHED (PREREGISTRATION.md §7 delta 7). Study 019's version of
this file asserted `len(slots) == 150`, `range(1, 51)`, `{16, 17}` per position
cell, `Counter({25: 5, 24: 1})` over the transitions and the pair `(1, 1)` as
the registered floor. Every one of those is a fact about FIFTY ROUNDS, and §2
says so in its own bytes: "at any other round count that assertion is wrong by
construction". 020's N is an OUTPUT of §2.1's pre-pilot effort sweep and does
not exist yet, so a file full of 50s would have to be rewritten again the day it
does — and a file that is rewritten at every N is a file that tests the numbers
rather than the design.

So the assertions here are of three kinds, and keeping them apart is the point:

  * **EXACT properties that hold at every N** — per-arm slot counts equal, the
    Williams square's own two properties, no arm ever immediately following
    itself, contiguous indices, one slot per arm per round.
  * **DERIVED properties**, where the expected value is computed from the
    registered round count by arithmetic stated here — the slot count, the
    transition total, the per-position cell values — so the test knows what to
    expect at N without being told.
  * **THE ATTAINED SPREADS**, which are neither exact nor guessable: they are
    whatever the exhaustive search attains at this N, they are PUBLISHED in the
    registry (§7 delta 7, "with the new attained position spread published"),
    and this file re-runs the search and requires the published pair to equal
    what it finds. That is what stops "carryover-balanced" from being an
    adjective: if a better order existed the search would find it and this test
    would fail rather than pass with a worse one registered.

The counters here are this file's own, not `batch.balance()`'s, wherever a
property could be satisfied by both sides sharing one bug.
"""
from collections import Counter

import pytest

import batch


# The registered round count, read from the driver, which reads it from the
# registry. Nothing in this file writes a round count of its own — that is the
# whole of the delta, and a literal here would reintroduce exactly what §2 says
# is wrong by construction.
ROUNDS = batch.ROUNDS
SLOTS = ROUNDS * len(batch.ARMS)
TRANSITIONS = SLOTS - 1


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


def test_the_registered_shape_is_derived_from_the_registered_round_count():
    """Exact at every N: N rounds of three arms is 3N slots, indices contiguous
    from 1, every round present, every position present, N slots per arm."""
    slots = expansion()
    assert len(slots) == SLOTS == batch.REGISTERED_SLOTS
    assert [index for index, _, _, _ in slots] == list(range(1, SLOTS + 1))
    assert sorted(set(round_index for _, round_index, _, _ in slots)) == \
        list(range(1, ROUNDS + 1))
    assert set(position for _, _, position, _ in slots) == {1, 2, 3}
    assert Counter(arm for _, _, _, arm in slots) == \
        Counter({arm: ROUNDS for arm in batch.ARMS})
    assert batch.RUNS_PER_ARM == ROUNDS


def test_the_block_shape_is_the_round_count_divided_by_the_six_sequences():
    """§2's tail exists because the round count need not be a multiple of 6.
    The shape is derived by division rather than transcribed, so a registry
    naming an N and a `blocks` that do not agree fails here."""
    blocks, tail_length = divmod(ROUNDS, len(batch.williams()))
    assert batch.BLOCKS == blocks
    assert len(batch.TAIL) == tail_length
    assert len(batch.BLOCK_ORDER) * blocks + tail_length == ROUNDS


def test_position_counts_are_as_even_as_the_round_count_allows():
    """N slots over 3 positions divide exactly iff 3 | N; otherwise every cell
    is one of the two integers around N/3. Both branches are asserted, so the
    day the sweep names a multiple of three this test tightens rather than
    breaks."""
    counts = Counter((arm, position) for _, _, position, arm in expansion())
    assert len(counts) == 9
    low, remainder = divmod(ROUNDS, 3)
    permitted = {low} if not remainder else {low, low + 1}
    assert set(counts.values()) <= permitted
    for arm in batch.ARMS:
        assert sum(counts[(arm, position)] for position in (1, 2, 3)) == ROUNDS


def test_no_arm_ever_immediately_follows_itself():
    slots = expansion()
    for left, right in zip(slots, slots[1:]):
        assert left[3] != right[3], (left, right)


def test_total_directed_transitions_are_as_even_as_the_slot_count_allows():
    """3N − 1 transitions over the 6 ordered pairs. With no self-succession the
    six ordered pairs are the only ones that occur, and the counts are the two
    integers around (3N − 1)/6."""
    transitions = Counter()
    slots = expansion()
    for left, right in zip(slots, slots[1:]):
        transitions[(left[3], right[3])] += 1
    assert sum(transitions.values()) == TRANSITIONS
    assert len(transitions) == 6
    low, remainder = divmod(TRANSITIONS, 6)
    permitted = {low} if not remainder else {low, low + 1}
    assert set(transitions.values()) <= permitted


def test_the_within_round_and_boundary_split_adds_up():
    slots = expansion()
    within, boundary = Counter(), Counter()
    for left, right in zip(slots, slots[1:]):
        (within if left[1] == right[1] else boundary)[(left[3], right[3])] += 1
    assert sum(within.values()) == ROUNDS * 2       # two within-round each
    assert sum(boundary.values()) == ROUNDS - 1     # one per round boundary
    profile = batch.balance(slots)
    assert profile["within"] == within and profile["boundary"] == boundary


def test_the_attained_spreads_are_the_ones_the_registry_publishes(pins):
    """§7 delta 7: "the new attained position spread published".

    The expansion's own counters, against the registry's published pair. 019
    asserted `== 1` here, which is the floor at 50 rounds and a wrong assertion
    at any other N — at a round count where the arithmetic divides evenly the
    floor is 0 and a drifted order attaining 1 would have passed."""
    profile = batch.balance(expansion())
    order = pins["batch"]["order"]
    assert profile["positionSpread"] == order["positionSpread"]
    assert profile["transitionSpread"] == order["transitionSpread"]
    assert profile["selfSuccessions"] == order.get("selfSuccessions") == 0
    assert batch.REGISTERED_POSITION_SPREAD == order["positionSpread"]
    assert batch.REGISTERED_TRANSITION_SPREAD == order["transitionSpread"]


def test_the_registered_order_is_the_search_at_the_registered_round_count(pins):
    """The registry is a cache; the search is the authority — and the search is
    re-run AT THE REGISTERED ROUND COUNT rather than at 50.

    Exhaustive over all 720 block orderings and every ordered tail of the
    required length, so a registered order that was merely good rather than
    optimal fails here, and a registry publishing a spread better than anything
    attainable fails here too."""
    derived = batch.derive_order(rounds=ROUNDS)
    assert derived["rounds"] == ROUNDS
    assert derived["blockOrder"] == batch.BLOCK_ORDER
    assert derived["tail"] == batch.TAIL
    order = pins["batch"]["order"]
    assert derived["positionSpread"] == order["positionSpread"]
    assert derived["transitionSpread"] == order["transitionSpread"]
    assert derived["slots"] == batch.REGISTERED_SLOTS
    assert derived["runsPerArm"] == batch.RUNS_PER_ARM


@pytest.mark.parametrize("rounds", [6, 12, 50])
def test_the_search_is_correct_at_round_counts_other_than_the_registered_one(
        rounds):
    """The delta's actual content, asserted where it can be: the derivation is a
    FUNCTION of N and answers at round counts this study has not registered.

    At a multiple of six the tail is empty and the order is whole blocks; the
    attained spreads are whatever the search finds and are reported rather than
    asserted, because the point is that this file does not know them in advance
    and does not need to."""
    derived = batch.derive_order(rounds=rounds)
    assert derived["rounds"] == rounds
    assert derived["blocks"] * 6 + derived["tailLength"] == rounds
    assert sorted(derived["blockOrder"]) == sorted(batch.williams())
    assert derived["slots"] == rounds * 3
    assert derived["positionSpread"] >= 0
    assert derived["transitionSpread"] >= 0
    # And the order it returns really does avoid self-succession at that N.
    slots = batch.expand(list(derived["blockOrder"]) * derived["blocks"]
                         + list(derived["tail"]))
    assert batch.balance(slots)["selfSuccessions"] == 0


def test_slot_entries_and_paths():
    entries = batch.schedule_entries()
    assert len(entries) == SLOTS
    for entry in entries:
        assert tuple(sorted(entry)) == tuple(sorted(batch.SCHEDULE_KEYS))
    for arm in batch.ARMS:
        indices = [entry["slotIndex"] for entry in entries
                   if entry["arm"] == arm]
        assert indices == list(range(1, ROUNDS + 1)), arm
    first = entries[0]
    assert batch.slot_path(first).endswith(
        "arms/%s/authoring/run-001" % first["arm"])


def test_a_block_order_that_is_not_a_permutation_refuses():
    with pytest.raises(batch.BatchError):
        batch.schedule(block=("W1", "W1", "W3", "W4", "W6", "W5"))
    with pytest.raises(batch.BatchError):
        batch.williams(first_row=("A", "A", "C"))
    with pytest.raises(batch.BatchError):
        batch.schedule(tail=("W4",) * (len(batch.TAIL) or 1))


def test_the_registry_and_the_driver_are_one_order(pins):
    """The registry's own order expanded through the driver's own function, and
    required to equal the driver's default expansion.

    §7 delta 7 changes what this test PROVES, and the change is worth stating.
    019's driver held its own copy of the block order and this compared two
    spellings; 020's driver reads the registry, so comparing them would be
    vacuous. What is compared instead is stronger: the registry's order against
    the exhaustive SEARCH at the registry's own round count
    (`test_the_registered_order_is_the_search_...` above), and here the
    registry's members against the shape the driver derived from them."""
    order = pins["batch"]["order"]
    assert tuple(order["firstRow"]) == batch.WILLIAMS_FIRST_ROW
    assert order["blocks"] == batch.BLOCKS
    assert order["rounds"] == batch.ROUNDS
    assert order["tailLength"] == len(batch.TAIL)
    assert batch.schedule(block=tuple(order["blockOrder"]),
                          tail=tuple(order["tail"])) == batch.schedule()
    assert pins["batch"]["n"] == batch.RUNS_PER_ARM
    assert pins["batch"]["slots"] == batch.REGISTERED_SLOTS
    assert tuple(pins["batch"]["arms"]) == batch.ARMS


def test_a_registry_with_no_round_count_refuses_rather_than_defaulting(
        tmp_path, pins):
    """§7 delta 7's refusal. §2.1 registers N as an output of the pre-pilot
    sweep, so "the registry does not name one yet" is a real state — and a
    driver that answered it with a default would be inventing the number the
    registration says it does not have."""
    import json
    for value in (None, 0, -1, "50"):
        registry = json.loads(json.dumps(pins))
        registry["batch"]["n"] = value
        where = tmp_path / ("pins-%s.json" % value)
        where.write_text(json.dumps(registry), encoding="utf-8")
        with pytest.raises(batch.BatchError) as raised:
            batch._registered_batch_shape(str(where))
        assert "batch.n" in str(raised.value)
        assert "pre-pilot effort sweep" in str(raised.value)


def test_a_registry_with_no_published_spread_refuses_at_the_expansion(
        tmp_path, pins):
    """The other half of "with the new attained position spread published": an
    order whose balance is not published is an order whose balance nothing
    checks, so the expansion refuses rather than falling back on 019's (1, 1)."""
    saved = batch.REGISTERED_POSITION_SPREAD
    batch.REGISTERED_POSITION_SPREAD = None
    try:
        with pytest.raises(batch.BatchError) as raised:
            batch.schedule()
        assert "publishes no positionSpread" in str(raised.value)
    finally:
        batch.REGISTERED_POSITION_SPREAD = saved


def test_the_registry_and_the_driver_are_one_timeout_ceiling(pins):
    """The wrapper reads the ceiling from the registry and the driver classifies
    on its own constant; two ceilings would be two studies."""
    assert pins["batch"]["callTimeoutSeconds"] == \
        batch.CALL_TIMEOUT_SECONDS == 2700
    assert pins["batch"]["timeoutKillAfterSeconds"] == \
        batch.TIMEOUT_KILL_AFTER_SECONDS


def test_the_registered_batch_shape_is_the_registrations(preregistration):
    """§2 "Batch shape" states the ceiling and the cap in prose; the driver
    derives them. A one-sided edit names its own drift site.

    **THE ROUND COUNT IS DELIBERATELY NOT ASSERTED AGAINST PROSE HERE, AND THAT
    IS A REGISTERED FINDING RATHER THAN A GAP.** 019's prose stated "N = 50
    runs/arm, 150 slots" and this test read that sentence. 020's §2 states no N
    at all: it carries "**TODO(prereg): the re-derived call order, the attained
    position spread, and the re-pinned `batch.order` / `batch.n` /
    `batch.slots`** — they are functions of N, which §2.1 registers as an output
    of the pre-pilot sweep", and §2.1 carries the matching TODO for the compute
    condition. So what is asserted is the state the registration is actually in:
    the TODO is present, no round count is claimed as registered, and the
    registry's own block says the same thing in its note. The day the sweep runs
    and §2 is filled, THIS test is the one that must be tightened to read the
    number — and it names that obligation rather than leaving it to a memory."""
    # Emphasis, code marks and the blockquote markers are stripped before the
    # prose is read, the same treatment `tests/test_partition.py` gives §1a:
    # they are wrapping decisions and the registration is the sentence. The
    # TODO(prereg) blocks are BLOCKQUOTES, so a reader that did not strip "> "
    # would be asserting the quoting rather than the obligation.
    flat = " ".join(
        line.lstrip("> ") for line
        in preregistration.replace("*", "").replace("`", "").split("\n"))
    flat = " ".join(flat.split())
    assert "Per-call timeout ceiling: 2700 s" in flat
    assert "timeout rate above the registered cap (10 % of slots)" in flat
    assert batch.CALL_TIMEOUT_SECONDS == 2700
    # The registration's own statement that N is not yet registered.
    assert ("TODO(prereg): the re-derived call order, the attained position "
            "spread, and the re-pinned batch.order / batch.n / batch.slots"
            in flat)
    assert ("TODO(prereg) — the registered compute condition: the "
            "codex.reasoningEffort value and the per-arm N" in flat)
    assert ("carryover-balanced schedule for three arms, re-derived at 020's "
            "registered round count and asserted by a harness test" in flat)


def test_the_registry_says_its_round_count_is_not_yet_a_registration(pins):
    """The registry's half of the same finding. §7 delta 7 requires
    `batch.order` / `batch.n` / `batch.slots` to be RE-PINNED at the registered
    round count; until §2.1's sweep has run there is no such count, so the block
    carries 019's numbers and says so in its own note. A note that merely
    described them as carried would let a reader take them for a registration —
    this asserts the note names the delta and the TODO it waits on."""
    note = pins["batch"]["note"]
    assert "NOT YET A STUDY 020 REGISTRATION" in note
    assert "§7 delta 7" in note
    assert "pre-pilot effort sweep" in note
    assert "derive-schedule" in note
    # …and the derivation that will replace them is named as data, so the
    # re-pin is against a search rather than against a hand-written table.
    assert "derive_order" in pins["batch"]["order"]["derivedBy"]
