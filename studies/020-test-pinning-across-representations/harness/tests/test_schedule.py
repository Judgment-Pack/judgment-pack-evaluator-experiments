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

**REBUILT FOR STUDY 020, and the rebuild is §7's delta 7 read honestly.** §2
registers Study 019's constants as **wrong by construction at any other N** —
`derive_order()`'s cached answer is the floor (1, 1) *at 50 rounds* — and 020's
N is a `TODO(prereg)` output of the pre-pilot effort sweep (§2.1). So this
module can no longer assert "50 and 150 are the registered shape". It asserts
three things instead:

  * the PROPERTIES hold at whatever round count they are evaluated at, driven at
    more than one N so a property that is really an artefact of 50 fails;
  * the module's constants are a **provisional planning shape** carried from
    019, not a registration — and the registry says so by carrying `batch.n`,
    `batch.slots` and `batch.order` as NULL;
  * `check_registry()` REFUSES that null state, so no call can be spent against
    an unregistered shape. That refusal is the safety property delta 7's
    absence leaves standing, and it is asserted here rather than assumed.
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


def test_the_provisional_order_is_the_derivation_at_its_own_round_count():
    """The constants are a cache; the search is the authority — AT THE ROUND
    COUNT THEY WERE CACHED AT, which is the qualifier §2 says Study 019's
    docstring dropped.

    Exhaustive over all 720 block orderings and all 30 ordered tails, so an
    order that was merely good rather than optimal fails here."""
    derived = batch.derive_order()
    assert derived["blockOrder"] == batch.BLOCK_ORDER
    assert derived["tail"] == batch.TAIL
    assert (derived["positionSpread"], derived["transitionSpread"]) == (1, 1)


def test_the_floor_is_a_property_of_the_search_and_not_of_fifty_rounds():
    """§7's delta 7 in one assertion: the (1, 1) floor is 019's answer AT 50
    ROUNDS, and 020's N is not 50 yet. Driving the search at other tail lengths
    shows the derivation is a function of the round count — so a study that
    registers a different N re-derives rather than inheriting, and a cached
    answer presented as "the registered floor" is wrong by construction.

    Two tail lengths beside the cached one. Each is a different round count and
    each gets its own answer; what is asserted is that the SEARCH answers, that
    the answer attains its own floor, and that the answer is not assumed to be
    019's."""
    for tail_length in (0, 1, 3):
        derived = batch.derive_order(blocks=2, tail_length=tail_length)
        rounds = 2 * batch.SEQUENCES + tail_length
        slots = batch.expand(list(derived["blockOrder"]) * 2
                             + list(derived["tail"]))
        assert len(slots) == rounds * batch.POSITIONS
        profile = batch.balance(slots)
        assert profile["selfSuccessions"] == 0, tail_length
        assert profile["positionSpread"] == derived["positionSpread"]
        assert profile["transitionSpread"] == derived["transitionSpread"]
        # …and the floor itself MOVES with the round count: at a tail length
        # that divides evenly the spreads can be 0, which 019's cached (1, 1)
        # would have asserted away.
        assert derived["positionSpread"] <= 1 and \
            derived["transitionSpread"] <= 1, tail_length


def test_the_module_constants_are_provisional_and_the_registry_says_so(pins):
    """The registered shape is a `TODO(prereg)`. Three registry members are
    NULL and the driver's constants are 019's — and the registry's own note is
    what tells a reader which is which, because a constant with a value looks
    exactly like a registration until someone reads the registry."""
    assert pins["batch"]["n"] is None
    assert pins["batch"]["slots"] is None
    assert pins["batch"]["order"] is None
    note = pins["batch"]["note"]
    assert "TODO(prereg)" in note and "NULL BY CONSTRUCTION" in note
    assert "OUTPUT of the pre-pilot effort sweep" in note
    # The provisional shape is Study 019's, unedited, so the port is a port.
    assert (batch.ROUNDS, batch.RUNS_PER_ARM, batch.REGISTERED_SLOTS) == \
        (50, 50, 150)


def test_a_null_registered_shape_refuses_the_batch(pins):
    """The safety property delta 7's absence leaves standing: `check_registry()`
    refuses a registry that names no order, no N and no slot count, so no call
    can be spent against an unregistered shape. Each of the three is driven
    ALONE, because a gate that only refused all three together would pass a
    registry that had filled two.

    The CONTROL is the other half and it is not a passing call: this tree has no
    `arms/<ARM>/PROMPT.txt` yet (the artifact port is `harness/SCAFFOLD.md` item
    A1), so a registry with all three batch members filled still refuses — on
    the MISSING PROMPT, and not on a batch member. That is what distinguishes
    "the gate fires on the shape" from "the gate fires on everything"."""
    import copy
    import integrity
    filled = copy.deepcopy(pins)
    for _name, path in integrity.FREEZE_PINS:
        node = filled
        for key in path[:-1]:
            node = node.setdefault(key, {})
        if node.get(path[-1]) is None:
            node[path[-1]] = "sha256:" + "0" * 64
    filled["batch"]["n"] = batch.RUNS_PER_ARM
    filled["batch"]["slots"] = batch.REGISTERED_SLOTS
    filled["batch"]["order"] = {"blockOrder": list(batch.BLOCK_ORDER),
                                "blocks": batch.BLOCKS,
                                "firstRow": list(batch.WILLIAMS_FIRST_ROW),
                                "tail": list(batch.TAIL)}

    # The control nulls a NON-batch member explicitly (SCAFFOLD item A2 filled
    # the prompt pins on 2026-08-24, so the ambient tree no longer supplies a
    # null for this control to lean on — the registered shape must be nulled
    # deliberately, which is what the control was always about).
    control_null = copy.deepcopy(filled)
    control_null["arms"]["A"]["promptSha256"] = None
    with pytest.raises(batch.BatchError) as control:
        batch.check_registry(control_null)
    for member in ("batch.n", "batch.slots", "batch.order"):
        assert member not in str(control.value), member

    for member in ("n", "slots", "order"):
        one_null = copy.deepcopy(filled)
        one_null["batch"][member] = None
        with pytest.raises(batch.BatchError) as caught:
            batch.check_registry(one_null)
        assert "batch." + member in str(caught.value), member

    # …and the COMMITTED registry, which carries all three as null.
    with pytest.raises(batch.BatchError) as caught:
        batch.check_registry(copy.deepcopy(pins))
    assert "batch.order" in str(caught.value)


def test_the_registry_and_the_driver_will_be_one_order(pins):
    """Study 019 asserted the registry's order equals the driver's. 020 cannot:
    the registry carries none. What CAN be asserted, and is, is that the
    equality holds the moment a shape is registered — driven over a filled copy,
    so the check is live rather than deferred to the round that fills it."""
    import copy
    filled = copy.deepcopy(pins)
    filled["batch"]["order"] = {"blockOrder": list(batch.BLOCK_ORDER),
                                "blocks": batch.BLOCKS,
                                "firstRow": list(batch.WILLIAMS_FIRST_ROW),
                                "tail": list(batch.TAIL)}
    order = filled["batch"]["order"]
    assert tuple(order["firstRow"]) == batch.WILLIAMS_FIRST_ROW
    assert order["blocks"] == batch.BLOCKS
    assert batch.schedule(block=tuple(order["blockOrder"]),
                          tail=tuple(order["tail"])) == batch.schedule()
    assert tuple(pins["batch"]["arms"]) == batch.ARMS


def test_the_registry_and_the_driver_are_one_timeout_ceiling(pins):
    """The wrapper reads the ceiling from the registry and the driver classifies
    on its own constant; two ceilings would be two studies."""
    assert pins["batch"]["callTimeoutSeconds"] == batch.CALL_TIMEOUT_SECONDS == 2700
    assert pins["batch"]["timeoutKillAfterSeconds"] == \
        batch.TIMEOUT_KILL_AFTER_SECONDS


def test_the_registered_batch_shape_is_the_registrations(preregistration):
    """§2 "Batch shape" states what IS registered and what is not; the driver
    and the registry must agree with both halves. A one-sided edit names its own
    drift site.

    Flattened first: the registration wraps its own sentences, so "Per-call
    timeout ceiling" is split across two lines in the file and a raw substring
    test would assert the line wrapping rather than the number."""
    flat = " ".join(preregistration.replace("*", "").split())
    # What IS registered.
    assert "Per-call timeout ceiling: 2700 s, an apparatus bound" in flat
    assert "timeout rate above the registered cap (10 % of slots)" in flat
    assert batch.CALL_TIMEOUT_SECONDS == 2700
    # What is NOT: §2 names the round count as a TODO and says in terms why
    # carrying 019's constants forward would be wrong.
    assert ("TODO(prereg): the re-derived call order, the attained position "
            "spread, and the re-pinned `batch.order` / `batch.n` / "
            "`batch.slots`") in flat
    assert ("019's `batch.py` hard-codes `SEQUENCES = 6`, `ROUNDS = 50`" in flat)
    assert "at any other round count that assertion is wrong by construction" \
        in flat
